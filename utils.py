import pandas as pd
from models import db, Food
import os

def allowed_file(filename, allowed_extensions):
    """Check if the file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

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
            'name': 'Luchi',
            'description': 'Deep-fried flatbread made from wheat flour',
            'calories': 180.0,
            'protein': 3.5,
            'carbohydrates': 30.0,
            'fat': 8.0,
            'fiber': 1.5,
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
            'name': 'Aloo Pitika',
            'description': 'Mashed potatoes with mustard oil, onions, and chilis',
            'calories': 180.0,
            'protein': 3.0,
            'carbohydrates': 33.0,
            'fat': 6.0,
            'fiber': 4.0,
            'meal_type': 'lunch'
        },
        {
            'name': 'Rongalau Bor',
            'description': 'Pumpkin fritters with gram flour',
            'calories': 160.0,
            'protein': 5.0,
            'carbohydrates': 25.0,
            'fat': 7.0,
            'fiber': 3.0,
            'meal_type': 'lunch'
        },
        {
            'name': 'Xaak Bor',
            'description': 'Fritters made with leafy greens',
            'calories': 130.0,
            'protein': 6.0,
            'carbohydrates': 18.0,
            'fat': 5.0,
            'fiber': 4.5,
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
            'name': 'Lai Xaak',
            'description': 'Stir-fried mustard greens',
            'calories': 90.0,
            'protein': 4.0,
            'carbohydrates': 12.0,
            'fat': 3.0,
            'fiber': 7.0,
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
        },
        {
            'name': 'Bengena Pitika',
            'description': 'Mashed roasted eggplant with onions and spices',
            'calories': 120.0,
            'protein': 3.0,
            'carbohydrates': 15.0,
            'fat': 6.0,
            'fiber': 5.0,
            'meal_type': 'dinner'
        },
        {
            'name': 'Bilahi Maas',
            'description': 'Tomato and fish curry',
            'calories': 210.0,
            'protein': 22.0,
            'carbohydrates': 10.0,
            'fat': 9.0,
            'fiber': 3.0,
            'meal_type': 'dinner'
        },
        {
            'name': 'Kosu Xaak',
            'description': 'Colocasia leaves stir fry',
            'calories': 110.0,
            'protein': 5.0,
            'carbohydrates': 14.0,
            'fat': 4.0,
            'fiber': 6.0,
            'meal_type': 'dinner'
        },
        {
            'name': 'Narasingha Bhaji',
            'description': 'Stir-fried water spinach',
            'calories': 80.0,
            'protein': 4.0,
            'carbohydrates': 10.0,
            'fat': 3.0,
            'fiber': 6.5,
            'meal_type': 'dinner'
        }
    ]

    for food_data in sample_data:
        food = Food(**food_data)
        db.session.add(food)
    
    db.session.commit()

def save_as_csv(data, filename):
    """Save data to a CSV file"""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    return os.path.abspath(filename)
