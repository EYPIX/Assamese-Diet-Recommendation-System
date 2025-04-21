# Assamese Diet Recommendation System

A machine learning-based diet recommendation system specifically designed for Assamese cuisine. The system uses supervised learning to predict appropriate meal types for food items based on their nutritional content, finds similar foods based on nutritional profiles, and generates personalized meal plans that meet specific nutritional goals.

## Features

- **Meal Type Prediction**: Predicts whether a food item is best suited for breakfast, lunch, or dinner based on nutritional content
- **Similar Food Finder**: Identifies foods with similar nutritional profiles
- **Nutritional Goal-Based Recommendations**: Suggests foods that best match user-defined nutritional targets
- **Daily Meal Plan Generation**: Creates complete meal plans with breakfast, lunch, and dinner options that collectively meet nutritional requirements
- **Data Upload**: Allows users to upload new food data to expand the recommendation database

## Technical Stack

- **Backend**: Python Flask API with scikit-learn machine learning models
- **Frontend**: HTML/CSS/JavaScript with Tailwind CSS for styling
- **Machine Learning**: Random Forest models for classification and regression tasks
- **Data Processing**: Pandas and NumPy for data manipulation
- **Database**: SQLite for data storage

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- VSCode
- Git (optional, for cloning the repository)

## Installation

### Step 1: Clone the repository (or download the ZIP file)

```bash
git clone https://github.com/yourusername/assamese-diet-recommendation.git
cd assamese-diet-recommendation
```

### Step 2: Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

## Setting up in VSCode

1. Open VSCode
2. Choose "File" > "Open Folder" and select the project folder
3. Ensure VSCode is using the correct Python interpreter:
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
   - Type "Python: Select Interpreter" and select the virtual environment you created

## Running the Application

### Method 1: Using VSCode

1. Open the integrated terminal in VSCode (View > Terminal)
2. Make sure your virtual environment is activated
3. Run the command:
   ```bash
   python main.py
   ```
4. Open a web browser and navigate to `http://localhost:5000`

### Method 2: Using the terminal

1. Activate your virtual environment
2. Run the command:
   ```bash
   python main.py
   ```
   or
   ```bash
   flask run
   ```
3. Open a web browser and navigate to `http://localhost:5000`

## Project Structure

```
assamese-diet-recommendation/
├── app.py                  # Main Flask application
├── main.py                 # Entry point
├── ml_models.py            # Machine learning models for recommendations
├── models.py               # Database models
├── utils.py                # Utility functions
├── templates/              # HTML templates
│   ├── index.html          # Home page
│   ├── upload.html         # Data upload page
│   ├── meal_prediction.html # Meal type prediction page
│   ├── similar_foods.html  # Similar food finder page
│   ├── meal_plan.html      # Meal plan generation page
│   └── about.html          # About page
├── static/                 # Static files (CSS, JS, images)
├── uploads/                # Directory for uploaded files
├── requirements.txt        # Dependencies
└── README.md               # This file
```

## Using the Application

1. **Home Page**: Navigate through the application features
2. **Upload Data**: Add new Assamese food items to the database
3. **Meal Prediction**: Predict the most suitable meal type for foods
4. **Similar Foods**: Find foods with similar nutritional profiles
5. **Meal Plan**: Generate a complete meal plan based on nutritional goals

## Development

### Adding New Features

1. Make sure you have the required dependencies installed
2. Create a new branch for your feature
3. Implement your changes
4. Test thoroughly
5. Submit a pull request

### Database Management

The application uses SQLite by default. If you need to modify the database schema:

1. Update the models in `models.py`
2. Run the Flask application with `flask db migrate -m "Description of changes"`
3. Apply the migrations with `flask db upgrade`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Special thanks to contributors of Assamese cuisine data
- Flask community for the excellent web framework
- scikit-learn for machine learning capabilities
