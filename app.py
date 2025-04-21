import os
import logging
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
import numpy as np
from models import db, Food

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "assamese_diet_recommendation_secret_key")

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///assamese_diet.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Initialize the database within application context
with app.app_context():
    db.create_all()
    # Create sample data if database is empty
    if Food.query.count() == 0:
        # We'll implement this function later
        pass

# Constants
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_sample_data():
    """Create sample Assamese food data for initial database"""
    sample_data = [
        {
            'name': 'Jolpan',
            'description': 'Traditional Assamese breakfast with flattened rice, curd and jaggery',
            'calories': 250.0,
            'protein': 8.0,
            'carbohydrates': 45.0,
            'fat': 6.0,
            'fiber': 3.5,
            'meal_type': 'breakfast'
        },
        {
            'name': 'Pitha',
            'description': 'Rice cake with fillings like coconut and jaggery',
            'calories': 200.0,
            'protein': 4.0,
            'carbohydrates': 35.0,
            'fat': 7.0,
            'fiber': 2.5,
            'meal_type': 'breakfast'
        },
        {
            'name': 'Khar',
            'description': 'Traditional Assamese dish made with raw papaya and lentils',
            'calories': 150.0,
            'protein': 7.0,
            'carbohydrates': 22.0,
            'fat': 4.0,
            'fiber': 5.0,
            'meal_type': 'lunch'
        },
        {
            'name': 'Masor Tenga',
            'description': 'Sour fish curry with tomatoes and lemon',
            'calories': 220.0,
            'protein': 25.0,
            'carbohydrates': 10.0,
            'fat': 10.0,
            'fiber': 3.0,
            'meal_type': 'lunch'
        },
        {
            'name': 'Bor Diya Hahor Mangxo',
            'description': 'Duck meat curry with lentil dumplings',
            'calories': 350.0,
            'protein': 30.0,
            'carbohydrates': 20.0,
            'fat': 18.0,
            'fiber': 2.5,
            'meal_type': 'dinner'
        },
        {
            'name': 'Ou Tenga Masor Jul',
            'description': 'Fish curry with elephant apple',
            'calories': 240.0,
            'protein': 28.0,
            'carbohydrates': 12.0,
            'fat': 12.0,
            'fiber': 2.0,
            'meal_type': 'dinner'
        }
    ]

    for food_data in sample_data:
        food = Food(**food_data)
        db.session.add(food)
    
    db.session.commit()

# Simple meal type prediction
def predict_meal_type(features):
    """A simple rule-based meal type prediction"""
    calories = features[0][0]
    protein = features[0][1]
    carbs = features[0][2]
    fat = features[0][3]
    
    # Simple rules for meal type prediction
    if calories < 200:
        return "breakfast", {"breakfast": 0.7, "lunch": 0.2, "dinner": 0.1}
    elif calories > 400:
        return "dinner", {"breakfast": 0.1, "lunch": 0.3, "dinner": 0.6}
    else:
        return "lunch", {"breakfast": 0.2, "lunch": 0.6, "dinner": 0.2}

# Simple food similarity finder
def find_similar_foods(food_id, food_data, n_neighbors=6):
    """Find similar foods based on nutritional content"""
    try:
        # Get the food by ID
        food_row = food_data[food_data['id'] == food_id]
        
        if food_row.empty:
            return []
        
        # Get the features of the food
        food_features = food_row[['calories', 'protein', 'carbohydrates', 'fat']].values[0]
        
        # Calculate similarity based on nutritional values
        similar_foods = []
        for idx, row in food_data.iterrows():
            if row['id'] != food_id:  # Don't include the original food
                # Get features
                features = [row['calories'], row['protein'], row['carbohydrates'], row['fat']]
                
                # Calculate Euclidean distance
                distance = np.sqrt(sum((food_features[i] - features[i])**2 for i in range(len(features))))
                
                similar_foods.append((row['id'], distance))
        
        # Sort by distance and get the nearest neighbors
        similar_foods.sort(key=lambda x: x[1])
        similar_food_ids = [food[0] for food in similar_foods[:n_neighbors]]
        
        return similar_food_ids
    except Exception as e:
        logger.error(f"Error finding similar foods: {str(e)}")
        return []

# Simple meal plan generator
def generate_meal_plan(food_data, target_calories, target_protein, target_carbs, target_fat, target_fiber):
    """Generate a meal plan based on nutritional goals"""
    try:
        # Make sure all foods have meal types
        for idx, row in food_data.iterrows():
            if pd.isna(row['meal_type']):
                # Predict meal type based on nutritional content
                features = np.array([[
                    row['calories'], 
                    row['protein'], 
                    row['carbohydrates'], 
                    row['fat']
                ]])
                meal_type, _ = predict_meal_type(features)
                food_data.at[idx, 'meal_type'] = meal_type
        
        # Split foods by meal type
        breakfast_foods = food_data[food_data['meal_type'] == 'breakfast']
        lunch_foods = food_data[food_data['meal_type'] == 'lunch']
        dinner_foods = food_data[food_data['meal_type'] == 'dinner']
        
        # Handle case where meal types might be empty
        if breakfast_foods.empty:
            breakfast_foods = food_data.head(3)
            breakfast_foods['meal_type'] = 'breakfast'
        
        if lunch_foods.empty:
            lunch_foods = food_data.iloc[3:6]
            lunch_foods['meal_type'] = 'lunch'
            
        if dinner_foods.empty:
            dinner_foods = food_data.iloc[6:9]
            dinner_foods['meal_type'] = 'dinner'
        
        # Simple selection of foods (take the first 2 of each type)
        breakfast_selection = list(breakfast_foods.head(2)['id'].values)
        lunch_selection = list(lunch_foods.head(2)['id'].values)
        dinner_selection = list(dinner_foods.head(2)['id'].values)
        
        return {
            'breakfast': breakfast_selection,
            'lunch': lunch_selection,
            'dinner': dinner_selection
        }
    except Exception as e:
        logger.error(f"Error generating meal plan: {str(e)}")
        return {'breakfast': [], 'lunch': [], 'dinner': []}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
            
        file = request.files['file']
        
        # If the user does not select a file, the browser submits an empty file
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            try:
                # Process the uploaded file
                df = pd.read_csv(file_path)
                
                # Rename columns if needed
                column_mapping = {
                    'Food Item': 'name',
                    'Meal Type': 'meal_type',
                    'Calories (kcal)': 'calories',
                    'Protein (g)': 'protein',
                    'Carbohydrates (g)': 'carbohydrates',
                    'Fats (g)': 'fat',
                }
                
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns:
                        df = df.rename(columns={old_col: new_col})
                
                # Add description if missing
                if 'description' not in df.columns and 'Category' in df.columns:
                    df['description'] = df['name'] + " - " + df['Category']
                elif 'description' not in df.columns:
                    df['description'] = df['name']
                
                # Add fiber if missing
                if 'fiber' not in df.columns:
                    df['fiber'] = 2.0  # Default value
                
                # Standardize meal types
                if 'meal_type' in df.columns:
                    df['meal_type'] = df['meal_type'].str.lower()
                    
                    # Handle invalid meal types
                    valid_types = ['breakfast', 'lunch', 'dinner']
                    mask = ~df['meal_type'].isin(valid_types)
                    df.loc[mask, 'meal_type'] = 'lunch'  # Default to lunch
                
                # Fill missing values
                df = df.fillna({
                    'calories': 200,
                    'protein': 5,
                    'carbohydrates': 30,
                    'fat': 7,
                    'fiber': 3
                })
                
                # Add data to the database
                for _, row in df.iterrows():
                    food = Food(
                        name=str(row['name']),
                        description=str(row['description']),
                        calories=float(row['calories']),
                        protein=float(row['protein']),
                        carbohydrates=float(row['carbohydrates']),
                        fat=float(row['fat']),
                        fiber=float(row['fiber']),
                        meal_type=str(row['meal_type']) if 'meal_type' in row and not pd.isna(row['meal_type']) else None
                    )
                    db.session.add(food)
                
                db.session.commit()
                
                flash('File successfully uploaded and processed')
                return redirect(url_for('upload'))
                
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                flash(f'Error processing file: {str(e)}')
                return redirect(request.url)
    
    # For GET request, show all foods in the database
    foods = Food.query.all()
    return render_template('upload.html', foods=foods)

@app.route('/meal_prediction', methods=['GET', 'POST'])
def meal_prediction():
    result = None
    foods = Food.query.all()
    
    if request.method == 'POST':
        food_id = request.form.get('food_id')
        
        if food_id:
            food = Food.query.get(food_id)
            if food:
                # Create feature vector
                features = np.array([[
                    food.calories, 
                    food.protein, 
                    food.carbohydrates, 
                    food.fat
                ]])
                
                # Predict meal type
                meal_type, probabilities = predict_meal_type(features)
                
                # Update food object with prediction if meal_type is None
                if food.meal_type is None:
                    food.meal_type = meal_type
                    db.session.commit()
                
                result = {
                    'food': food,
                    'predicted_meal_type': meal_type,
                    'probabilities': probabilities
                }
    
    return render_template('meal_prediction.html', foods=foods, result=result)

@app.route('/similar_foods', methods=['GET', 'POST'])
def similar_foods():
    result = None
    foods = Food.query.all()
    
    if request.method == 'POST':
        food_id = request.form.get('food_id')
        num_similar = int(request.form.get('num_similar', 5))
        
        if food_id:
            food = Food.query.get(food_id)
            if food:
                # Get all foods from database for comparison
                all_foods = pd.read_sql('SELECT * FROM food', db.engine)
                
                # Find similar foods
                similar_food_indices = find_similar_foods(
                    food_id=int(food_id),
                    food_data=all_foods,
                    n_neighbors=num_similar
                )
                
                # Get similar food objects
                similar_foods = [Food.query.get(idx) for idx in similar_food_indices if Food.query.get(idx) is not None]
                
                result = {
                    'food': food,
                    'similar_foods': similar_foods
                }
    
    return render_template('similar_foods.html', foods=foods, result=result)

@app.route('/meal_plan', methods=['GET', 'POST'])
def meal_plan():
    result = None
    
    if request.method == 'POST':
        # Get user nutrition goals
        try:
            target_calories = float(request.form.get('target_calories', 2000))
            target_protein = float(request.form.get('target_protein', 50))
            target_carbs = float(request.form.get('target_carbs', 250))
            target_fat = float(request.form.get('target_fat', 70))
            target_fiber = float(request.form.get('target_fiber', 25))
            
            # Get all foods from database
            all_foods = pd.read_sql('SELECT * FROM food', db.engine)
            
            if all_foods.empty:
                flash('No food data available. Please add some food items first.')
                return render_template('meal_plan.html', result=None)
            
            # Generate meal plan
            meal_plan_data = generate_meal_plan(
                food_data=all_foods,
                target_calories=target_calories,
                target_protein=target_protein,
                target_carbs=target_carbs,
                target_fat=target_fat,
                target_fiber=target_fiber
            )
            
            # Get food objects for the meal plan
            breakfast = []
            lunch = []
            dinner = []
            
            # Process breakfast foods
            for food_id in meal_plan_data.get('breakfast', []):
                if food_id is not None:
                    food = Food.query.get(int(food_id))
                    if food is not None:
                        breakfast.append(food)
            
            # Process lunch foods
            for food_id in meal_plan_data.get('lunch', []):
                if food_id is not None:
                    food = Food.query.get(int(food_id))
                    if food is not None:
                        lunch.append(food)
            
            # Process dinner foods
            for food_id in meal_plan_data.get('dinner', []):
                if food_id is not None:
                    food = Food.query.get(int(food_id))
                    if food is not None:
                        dinner.append(food)
            
            # Check if we have any foods in the meal plan
            if not breakfast and not lunch and not dinner:
                flash('Could not generate a meal plan with the current food database. Please add more foods with different meal types.')
                return render_template('meal_plan.html', result=None)
            
            # Calculate total nutrition values
            total_nutrition = {
                'calories': sum(food.calories for food in breakfast + lunch + dinner),
                'protein': sum(food.protein for food in breakfast + lunch + dinner),
                'carbohydrates': sum(food.carbohydrates for food in breakfast + lunch + dinner),
                'fat': sum(food.fat for food in breakfast + lunch + dinner),
                'fiber': sum(food.fiber for food in breakfast + lunch + dinner)
            }
            
            # Calculate percentage of targets met
            target_nutrition = {
                'calories': target_calories,
                'protein': target_protein,
                'carbohydrates': target_carbs,
                'fat': target_fat,
                'fiber': target_fiber
            }
            
            percentage_met = {
                nutrient: (total_nutrition[nutrient] / target * 100) if target > 0 else 0
                for nutrient, target in target_nutrition.items()
            }
            
            result = {
                'breakfast': breakfast,
                'lunch': lunch,
                'dinner': dinner,
                'total_nutrition': total_nutrition,
                'target_nutrition': target_nutrition,
                'percentage_met': percentage_met
            }
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Meal plan generation error: {error_message}")
            flash(f'Error generating meal plan: {error_message}')
            return render_template('meal_plan.html', result=None)
    
    return render_template('meal_plan.html', result=result)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/foods')
def api_foods():
    foods = Food.query.all()
    food_list = [{
        'id': food.id,
        'name': food.name,
        'calories': food.calories,
        'protein': food.protein,
        'carbohydrates': food.carbohydrates,
        'fat': food.fat,
        'fiber': food.fiber,
        'meal_type': food.meal_type
    } for food in foods]
    return jsonify(food_list)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)