from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)  # in grams
    carbohydrates = db.Column(db.Float, nullable=False)  # in grams
    fat = db.Column(db.Float, nullable=False)  # in grams
    fiber = db.Column(db.Float, nullable=False)  # in grams
    meal_type = db.Column(db.String(20), nullable=True)  # breakfast, lunch, or dinner
    
    def __repr__(self):
        return f'<Food {self.name}>'