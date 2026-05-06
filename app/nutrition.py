import os
import pandas as pd

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path  = os.path.join(base_dir, 'data', 'nutrition.csv')

_df_cache = None



def load_data():
    global _df_cache
    if _df_cache is None:
        try:
            if os.path.exists(csv_path):
                _df_cache = pd.read_csv(csv_path)
                _df_cache.columns = [c.lower().strip() for c in _df_cache.columns]
            else:
                print(f"[nutrition] Fichier CSV manquant : {csv_path}")
        except Exception as e:
            print(f"[nutrition] Erreur chargement CSV : {e}")
    return _df_cache


def get_nutrition_data(food_name):
   
    df = load_data()
    if df is None or not food_name:
        return None

    try:
        food_name = food_name.lower().strip()
        col = 'food' if 'food' in df.columns else 'name'
        match = df[df[col].str.lower().str.strip() == food_name]

        if not match.empty:
            row = match.iloc[0]
            return {
                'calories': float(row.get('calories', 0) or 0),
                'protein':  float(row.get('protein',  0) or 0),
                'carbs':    float(row.get('carbs',    0) or 0),
                'fat':      float(row.get('fat',      0) or 0),
                'sodium':   float(row.get('sodium',   0) or 0),
            }
    except Exception as e:
        print(f"[nutrition] Erreur get_nutrition_data : {e}")

    return None


def get_daily_needs(user):
  
    bmr = user.get_besoins_caloriques()   
    return {
        'calories': round(bmr,              1),
        'protein':  round(bmr * 0.25 / 4,  1),
        'carbs':    round(bmr * 0.50 / 4,  1),
        'fat':      round(bmr * 0.25 / 9,  1),
    }


def get_meal_summary(results):
 
    totals = {'calories': 0.0, 'protein': 0.0, 'carbs': 0.0, 'fat': 0.0}
    for item in results:
        nutrition = item.get('nutrition', {})
        quantity  = item.get('quantity', 1)
        for key in totals:
            totals[key] += (nutrition.get(key) or 0) * quantity
    return {k: round(v, 1) for k, v in totals.items()}