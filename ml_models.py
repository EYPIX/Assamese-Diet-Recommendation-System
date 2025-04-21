import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import logging
import pickle
import os

# Initialize models as globals
meal_type_model = None
knn_model = None
scaler = None

def preprocess_data(food_data):
    """Preprocess food data for machine learning models"""
    # Extract features and target
    X = food_data[['calories', 'protein', 'carbohydrates', 'fat', 'fiber']]
    
    # Handle missing meal type
    food_data_with_meal_type = food_data.dropna(subset=['meal_type'])
    
    if food_data_with_meal_type.empty:
        return X, []
    
    y_meal_type = food_data_with_meal_type['meal_type']
    X_meal_type = food_data_with_meal_type[['calories', 'protein', 'carbohydrates', 'fat', 'fiber']]
    
    return X_meal_type, y_meal_type

def train_meal_type_model(X, y):
    """Train a Random Forest classifier for meal type prediction"""
    global meal_type_model
    
    if X.empty or len(y) == 0:
        logging.warning("Not enough data to train meal type model")
        return None
    
    # Initialize and train the model
    meal_type_model = RandomForestClassifier(n_estimators=100, random_state=42)
    meal_type_model.fit(X, y)
    
    # Save the model
    with open('meal_type_model.pkl', 'wb') as f:
        pickle.dump(meal_type_model, f)
    
    return meal_type_model

def train_knn_model(X):
    """Train a K-Nearest Neighbors model for food similarity"""
    global knn_model, scaler
    
    if X.empty:
        logging.warning("Not enough data to train KNN model")
        return None
    
    # Initialize scaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Initialize and train the model
    knn_model = NearestNeighbors(n_neighbors=min(10, len(X)), algorithm='auto')
    knn_model.fit(X_scaled)
    
    # Save the models
    with open('knn_model.pkl', 'wb') as f:
        pickle.dump(knn_model, f)
    
    with open('scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    return knn_model

def load_models(X, y_meal_type, retrain=False):
    """Load or train models"""
    global meal_type_model, knn_model, scaler
    
    # Check if models exist and load them, otherwise train new ones
    if os.path.exists('meal_type_model.pkl') and not retrain and len(y_meal_type) > 0:
        with open('meal_type_model.pkl', 'rb') as f:
            meal_type_model = pickle.load(f)
    else:
        meal_type_model = train_meal_type_model(X, y_meal_type)
    
    if os.path.exists('knn_model.pkl') and os.path.exists('scaler.pkl') and not retrain and not X.empty:
        with open('knn_model.pkl', 'rb') as f:
            knn_model = pickle.load(f)
        with open('scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
    else:
        knn_model = train_knn_model(X)

def predict_meal_type(features):
    """Predict the meal type for a food item"""
    global meal_type_model
    
    if meal_type_model is None:
        return "Unknown", {}
    
    # Make prediction
    prediction = meal_type_model.predict(features)
    
    # Get probabilities for each class
    probabilities = meal_type_model.predict_proba(features)[0]
    class_probabilities = dict(zip(meal_type_model.classes_, probabilities))
    
    return prediction[0], class_probabilities

def find_similar_foods(food_id, food_data, n_neighbors=6):
    """Find similar foods based on nutritional content"""
    global knn_model, scaler
    
    if knn_model is None or scaler is None:
        return []
    
    # Convert food_id to int if it's a string
    if isinstance(food_id, str) and food_id.isdigit():
        food_id = int(food_id)
    
    # Get the food by ID
    food_row = food_data[food_data['id'] == food_id]
    
    if food_row.empty:
        return []
    
    # Get the features of the food
    food_features = food_row[['calories', 'protein', 'carbohydrates', 'fat', 'fiber']].values
    
    # Scale the features
    food_features_scaled = scaler.transform(food_features)
    
    # Find the k nearest neighbors
    distances, indices = knn_model.kneighbors(food_features_scaled, n_neighbors=min(n_neighbors, len(food_data)))
    
    # Get the IDs of the similar foods
    similar_foods_ids = food_data.iloc[indices[0]]['id'].values
    
    # Convert to int if needed
    similar_foods_ids = [int(id) for id in similar_foods_ids]
    
    return similar_foods_ids

def assign_meal_types(food_data):
    """Assign meal types to foods that don't have one"""
    # Find foods without meal type
    foods_without_meal_type = food_data[food_data['meal_type'].isnull()]
    
    # If there are no foods without meal type, return the original data
    if foods_without_meal_type.empty:
        return food_data
    
    # Make a copy to avoid modifying the original
    updated_food_data = food_data.copy()
    
    # Predict meal type for each food without one
    for idx, food in foods_without_meal_type.iterrows():
        features = np.array([[
            food['calories'], 
            food['protein'], 
            food['carbohydrates'], 
            food['fat'], 
            food['fiber']
        ]])
        
        # Predict meal type
        meal_type, _ = predict_meal_type(features)
        
        # Update food data with predicted meal type
        updated_food_data.at[idx, 'meal_type'] = meal_type
    
    return updated_food_data

def generate_meal_plan(food_data, target_calories, target_protein, target_carbs, target_fat, target_fiber):
    """Generate a meal plan based on nutritional goals with robust error handling"""
    # Make sure all nutritional values are positive
    target_calories = max(1, target_calories)
    target_protein = max(1, target_protein)
    target_carbs = max(1, target_carbs)
    target_fat = max(1, target_fat)
    target_fiber = max(1, target_fiber)
    
    # Ensure all foods have meal types
    food_data = assign_meal_types(food_data)
    
    # Split foods by meal type
    breakfast_foods = food_data[food_data['meal_type'] == 'breakfast']
    lunch_foods = food_data[food_data['meal_type'] == 'lunch']
    dinner_foods = food_data[food_data['meal_type'] == 'dinner']
    
    # Check if we have enough foods in each category
    if breakfast_foods.empty or lunch_foods.empty or dinner_foods.empty:
        logging.warning(f"Not enough food types. Breakfast: {len(breakfast_foods)}, Lunch: {len(lunch_foods)}, Dinner: {len(dinner_foods)}")
        # Create some default meals if categories are empty
        if breakfast_foods.empty and not food_data.empty:
            # Assign some foods as breakfast
            breakfast_foods = food_data.head(min(3, len(food_data)))
        if lunch_foods.empty and not food_data.empty:
            # Assign some foods as lunch
            lunch_foods = food_data.iloc[1:min(4, len(food_data))]
        if dinner_foods.empty and not food_data.empty:
            # Assign some foods as dinner
            dinner_foods = food_data.iloc[2:min(5, len(food_data))]
    
    # Function to select foods for a meal based on nutritional targets
    def select_foods_for_meal(available_foods, target_calories_meal, target_protein_meal, target_carbs_meal, target_fat_meal, target_fiber_meal, max_items=3):
        # Make sure we have foods to work with
        if available_foods.empty:
            logging.warning("No available foods for meal")
            return []
        
        # Initialize variables
        selected_foods = []
        current_nutrition = {'calories': 0, 'protein': 0, 'carbohydrates': 0, 'fat': 0, 'fiber': 0}
        
        # Make a copy to avoid modifying the original
        available_foods_copy = available_foods.copy()
        
        # Ensure food IDs are integers
        available_foods_copy['id'] = available_foods_copy['id'].astype(int)
        
        # Limit max_items to the number of available foods
        max_items = min(max_items, len(available_foods_copy))
        
        # If we have very few foods, just select them all
        if len(available_foods_copy) <= max_items:
            return list(available_foods_copy['id'].values)
        
        # Main selection loop
        attempts = 0
        max_attempts = 50  # Prevent infinite loops
        
        while len(selected_foods) < max_items and not available_foods_copy.empty and attempts < max_attempts:
            attempts += 1
            
            # Calculate remaining nutritional needs
            remaining_calories = max(1, target_calories_meal - current_nutrition['calories'])
            remaining_protein = max(1, target_protein_meal - current_nutrition['protein'])
            remaining_carbs = max(1, target_carbs_meal - current_nutrition['carbohydrates'])
            remaining_fat = max(1, target_fat_meal - current_nutrition['fat'])
            remaining_fiber = max(1, target_fiber_meal - current_nutrition['fiber'])
            
            # Calculate a score for each food based on how well it fits the remaining needs
            scores = []
            for idx, food in available_foods_copy.iterrows():
                # Skip any rows with NaN values
                if pd.isna(food['calories']) or pd.isna(food['protein']) or pd.isna(food['carbohydrates']) or pd.isna(food['fat']) or pd.isna(food['fiber']):
                    scores.append(float('inf'))
                    continue
                
                # Calculate how well the food meets the remaining nutritional needs
                score = (
                    abs(food['calories'] - remaining_calories / (max_items - len(selected_foods))) / remaining_calories +
                    abs(food['protein'] - remaining_protein / (max_items - len(selected_foods))) / remaining_protein +
                    abs(food['carbohydrates'] - remaining_carbs / (max_items - len(selected_foods))) / remaining_carbs +
                    abs(food['fat'] - remaining_fat / (max_items - len(selected_foods))) / remaining_fat +
                    abs(food['fiber'] - remaining_fiber / (max_items - len(selected_foods))) / remaining_fiber
                )
                
                scores.append(score)
            
            # If all scores are infinity, just pick the first food
            if all(s == float('inf') for s in scores):
                selected_food_idx = available_foods_copy.index[0]
            else:
                # Select the food with the lowest score
                min_score_idx = np.argmin(scores)
                selected_food_idx = available_foods_copy.index[min_score_idx]
            
            selected_food = available_foods_copy.loc[selected_food_idx]
            
            # Add the food to the selection
            food_id = int(selected_food['id'])
            selected_foods.append(food_id)
            
            # Update current nutrition
            current_nutrition['calories'] += selected_food['calories']
            current_nutrition['protein'] += selected_food['protein']
            current_nutrition['carbohydrates'] += selected_food['carbohydrates']
            current_nutrition['fat'] += selected_food['fat']
            current_nutrition['fiber'] += selected_food['fiber']
            
            # Remove the selected food from available foods
            available_foods_copy = available_foods_copy.drop(selected_food_idx)
        
        return selected_foods
    
    # Allocate target nutrition to each meal
    target_calories_breakfast = target_calories * 0.25
    target_calories_lunch = target_calories * 0.4
    target_calories_dinner = target_calories * 0.35
    
    target_protein_breakfast = target_protein * 0.25
    target_protein_lunch = target_protein * 0.4
    target_protein_dinner = target_protein * 0.35
    
    target_carbs_breakfast = target_carbs * 0.3
    target_carbs_lunch = target_carbs * 0.4
    target_carbs_dinner = target_carbs * 0.3
    
    target_fat_breakfast = target_fat * 0.25
    target_fat_lunch = target_fat * 0.35
    target_fat_dinner = target_fat * 0.4
    
    target_fiber_breakfast = target_fiber * 0.25
    target_fiber_lunch = target_fiber * 0.4
    target_fiber_dinner = target_fiber * 0.35
    
    # Try to select foods for each meal
    try:
        breakfast_selection = select_foods_for_meal(
            breakfast_foods, 
            target_calories_breakfast, 
            target_protein_breakfast, 
            target_carbs_breakfast, 
            target_fat_breakfast, 
            target_fiber_breakfast
        )
    except Exception as e:
        logging.error(f"Error selecting breakfast foods: {str(e)}")
        breakfast_selection = []
    
    try:
        lunch_selection = select_foods_for_meal(
            lunch_foods, 
            target_calories_lunch, 
            target_protein_lunch, 
            target_carbs_lunch, 
            target_fat_lunch, 
            target_fiber_lunch
        )
    except Exception as e:
        logging.error(f"Error selecting lunch foods: {str(e)}")
        lunch_selection = []
    
    try:
        dinner_selection = select_foods_for_meal(
            dinner_foods, 
            target_calories_dinner, 
            target_protein_dinner, 
            target_carbs_dinner, 
            target_fat_dinner, 
            target_fiber_dinner
        )
    except Exception as e:
        logging.error(f"Error selecting dinner foods: {str(e)}")
        dinner_selection = []
    
    # Make sure we have at least some foods in each meal
    if not breakfast_selection and not breakfast_foods.empty:
        breakfast_selection = list(breakfast_foods.head(1)['id'].values)
    
    if not lunch_selection and not lunch_foods.empty:
        lunch_selection = list(lunch_foods.head(1)['id'].values)
    
    if not dinner_selection and not dinner_foods.empty:
        dinner_selection = list(dinner_foods.head(1)['id'].values)
    
    # Log the meal plan
    logging.info(f"Meal plan generated - Breakfast: {breakfast_selection}, Lunch: {lunch_selection}, Dinner: {dinner_selection}")
    
    return {
        'breakfast': breakfast_selection,
        'lunch': lunch_selection,
        'dinner': dinner_selection
    }