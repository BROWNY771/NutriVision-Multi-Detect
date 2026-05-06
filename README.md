# NutriVision Pro

NutriVision Pro is an intelligent web-based system for food detection and personalized nutritional analysis.
It combines computer vision (YOLOv8), data-driven nutrition modeling, and health-aware recommendation logic to provide real-time dietary insights from meal images.

---

## Features

* Multi-food detection from a single image using YOLOv8
* Personalized nutritional analysis (calories, proteins, carbohydrates, fats, sodium)
* Health-aware alerts based on user conditions (diabetes, hypertension, allergies)
* Daily intake comparison using BMR estimation
* Scan history tracking per user
* Secure authentication system with hashed passwords

---

## Project Architecture

The project follows a Flask MVC architecture:

```bash
nutrivision-pro/
├── app/
│   ├── __init__.py        # Flask app factory
│   ├── models.py          # SQLAlchemy models (User, Scan)
│   ├── routes.py          # Application routes
│   ├── detector.py        # YOLOv8 inference logic
│   ├── nutrition.py       # Nutritional computations
│   ├── health.py          # Alerts & recommendations engine
│   ├── static/            # CSS, JS, uploaded images
│   └── templates/         # Jinja2 templates
├── data/
│   ├── nutrition.csv      # Food nutrition dataset
│   └── data.yaml          # YOLO configuration
├── yolov8n/s/m.pt         # Model weights
└── run.py                 # Entry point
```

---

## Tech Stack

| Layer          | Technology                           |
| -------------- | ------------------------------------ |
| Frontend       | HTML5, CSS3, Bootstrap 5, JavaScript |
| Backend        | Python 3.11, Flask 3                 |
| AI Model       | YOLOv8 (Ultralytics)                 |
| Data           | Pandas, CSV dataset                  |
| Database       | SQLite, SQLAlchemy                   |
| Authentication | Flask-Login, Werkzeug                |
| Migrations     | Flask-Migrate, Alembic               |

---

## How It Works

1. User provides health profile (age, weight, conditions, allergies)
2. User uploads a meal image
3. YOLOv8 detects food items
4. Nutrition engine computes macronutrients
5. Health engine evaluates risks and generates alerts
6. Recommendations are produced
7. Results are stored and displayed

---

## BMR Calculation

The system uses the Mifflin-St Jeor equation:

* Male
  BMR = (10 × weight) + (6.25 × height) − (5 × age) + 5

* Female
  BMR = (10 × weight) + (6.25 × height) − (5 × age) − 161

Fallback value: 2200 kcal/day

---

## Alert System

| Level    | Condition                     |
| -------- | ----------------------------- |
| Critical | Allergy detected              |
| High     | Diabetes or hypertension risk |
| Medium   | High calorie meal             |
| Info     | Moderate calorie excess       |

---

## Database Schema

### User

* id, username, password_hash
* age, weight, height, gender
* allergies, diseases

### Scan

* id, image_url, food_list
* total_calories, alerts
* timestamp, user_id

---

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/nutrivision-pro.git
cd nutrivision-pro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

---

## Demo

Add screenshots here (dashboard, detection results, alerts interface).

---

## Future Improvements

* Mobile application version
* Cloud deployment (AWS, Azure)
* Advanced medical recommendation system
* Improved model accuracy with custom dataset
* Portion size estimation

---

## Author

Souhail El Bettachi
Master Big Data & Artificial Intelligence

---

## License

This project is intended for academic and educational purposes.
