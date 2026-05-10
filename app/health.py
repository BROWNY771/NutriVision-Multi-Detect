from app.nutrition import get_daily_needs, get_meal_summary



def _pct(consumed, target):
    if not target:
        return 0
    return min(round(consumed / target * 100, 1), 999)


def _status(pct):
   
    if pct < 10:
        return 'too_low'
    if pct <= 55:
        return 'ok'
    if pct <= 75:
        return 'high'
    return 'critical'

def _get_conditions(user):
    maladies = (user.maladies or '').lower()
    return {
        'diabetes':     'diabète'      in maladies,
        'hypertension': 'hypertension' in maladies,
    }

def analyze_restrictions(user):
    
    restrictions = []
    cond = _get_conditions(user)
    if cond['diabetes']:
        restrictions.append('low_sugar')
    if cond['hypertension']:
        restrictions.append('low_salt')
    if user.allergies:
        restrictions.extend(
            a.strip().lower()
            for a in user.allergies.split(',') if a.strip()
        )
    return restrictions

def generate_alerts(user, results, total_calories):
   
    alerts          = []
    user_allergies  = [a.strip().lower() for a in (user.allergies or '').split(',') if a.strip()]
    cond            = _get_conditions(user)

    for item in results:
        food_name = item.get('name', '')
        nutrition = item.get('nutrition', {})

        if user_allergies and food_name.lower() in user_allergies:
            alerts.append(f"🚫 ALLERGIE : {food_name} est dans votre liste d'allergènes !")

        if cond['diabetes'] and (nutrition.get('carbs') or 0) > 20:
            alerts.append(f"⚠️ {food_name} est riche en glucides — attention (diabète)")

        if cond['hypertension'] and (nutrition.get('sodium') or 0) > 500:
            alerts.append(f"⚠️ {food_name} est riche en sodium — attention (hypertension)")

    bmr      = user.get_besoins_caloriques()
    meal_pct = _pct(total_calories, bmr)
    if meal_pct > 50:
        alerts.append(
            f"Repas très calorique : {int(total_calories)} kcal "
            f"= {meal_pct}% de votre besoin journalier ({int(bmr)} kcal)"
        )
    elif meal_pct > 33:
        alerts.append(
            f"Repas calorique : {int(total_calories)} kcal "
            f"({meal_pct}% de votre besoin journalier)"
        )

    return alerts


def generate_recommendations(user, results, total_calories):
   
    needs   = get_daily_needs(user)
    summary = get_meal_summary(results)
    cond    = _get_conditions(user)

    comparison = {}
    for key in ('calories', 'protein', 'carbs', 'fat'):
        consumed = summary.get(key, 0)
        target   = needs.get(key, 0)
        pct      = _pct(consumed, target)
        comparison[key] = {
            'consumed': consumed,
            'target':   target,
            'pct':      pct,
            'status':   _status(pct),
        }

    recommendations = []
    cal   = comparison['calories']
    prot  = comparison['protein']
    carbs = comparison['carbs']
    fat   = comparison['fat']

    # Calorie load
    if cal['status'] == 'critical':
        recommendations.append(
            "Ce repas couvre plus de 75 % de vos besoins caloriques. "
            "Privilégiez des repas très légers pour le reste de la journée."
        )
    elif cal['status'] == 'high':
        recommendations.append(
            "Repas assez calorique. Compensez avec une activité physique "
            "légère (30 min de marche ≈ 150 kcal)."
        )
    elif cal['status'] == 'too_low':
        recommendations.append(
            "Repas peu calorique. Assurez-vous de manger suffisamment "
            "sur le reste de la journée."
        )

    if prot['status'] == 'too_low':
        recommendations.append(
            "Protéines insuffisantes. Pensez à ajouter des œufs, du poulet, "
            "du poisson ou des légumineuses."
        )
    elif prot['status'] == 'critical':
        recommendations.append(
            "Très riche en protéines. Hydratez-vous bien pour aider vos reins."
        )

    if carbs['status'] in ('high', 'critical'):
        if cond['diabetes']:
            recommendations.append(
                "Glucides élevés — important avec votre diabète. "
                "Préférez des glucides complexes et évitez les sucres rapides."
            )
        else:
            recommendations.append(
                "Repas riche en glucides. Équilibrez avec des protéines "
                "et des fibres pour éviter un pic glycémique."
            )

    # Fat
    if fat['status'] in ('high', 'critical'):
        if cond['hypertension']:
            recommendations.append(
                "🩺 Lipides élevés — à surveiller avec votre hypertension. "
                "Limitez les graisses saturées."
            )
        else:
            recommendations.append(
                "Repas riche en lipides. Privilégiez les bonnes graisses "
                "(avocat, noix, huile d'olive)."
            )

    if not recommendations:
        recommendations.append(
            "Ce repas est bien équilibré par rapport à vos besoins. Continuez ainsi !"
        )

    return comparison, recommendations