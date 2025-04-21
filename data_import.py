import pandas as pd
from flask import Flask
from models import db, Food

# Create a Flask app context
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///assamese_diet.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def import_food_data(csv_path):
    """Import food data from CSV file into the database"""
    with app.app_context():
        # Read CSV
        df = pd.read_csv(csv_path)
        
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
        
        # Clear existing data (optional)
        # db.session.query(Food).delete()
        # db.session.commit()
        
        # Add each food to the database
        print(f"Importing {len(df)} food items...")
        added_count = 0
        
        for _, row in df.iterrows():
            try:
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
                added_count += 1
            except Exception as e:
                print(f"Error adding food {row['name']}: {str(e)}")
        
        # Commit changes
        db.session.commit()
        print(f"Successfully imported {added_count} food items")

if __name__ == "__main__":
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Import data
    csv_path = "assamese_meal_plan_dataset.csv"  # Update this path to your CSV file
    import_food_data(csv_path)