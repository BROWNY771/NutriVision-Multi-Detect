import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models import User, Scan
from app.detector import detect_multi_food
from app.nutrition import get_nutrition_data
from app.health import generate_alerts, generate_recommendations   # FIX: both imported

bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# DASHBOARD
@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    results         = []
    alerts          = []
    comparison      = {}    
    recommendations = []
    image_url       = None
    total_calories  = 0

    if request.method == 'POST':
        file = request.files.get('image')

        if not file or file.filename == '':
            flash("Aucune image sélectionnée.", "warning")
            return redirect(url_for('main.index'))

        if not allowed_file(file.filename):
            flash("Format non supporté. Utilisez PNG, JPG ou WEBP.", "danger")
            return redirect(url_for('main.index'))

        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        image_url  = url_for('static', filename='uploads/' + filename)
        detections = detect_multi_food(filepath)

        for item in detections:
            nutrition = get_nutrition_data(item['name'])
            if not nutrition:
                continue
            item['nutrition'] = nutrition
            item['quantity']  = item.get('count', 1)
            total_calories   += nutrition['calories'] * item['quantity']
            results.append(item)

        alerts = generate_alerts(current_user, results, total_calories)

        comparison, recommendations = generate_recommendations(
            current_user, results, total_calories
        )

        scan = Scan(
            image_url     = image_url,
            food_list     = ", ".join([d['name'] for d in detections]) if detections else "Aucun",
            total_calories= total_calories,
            user_id       = current_user.id,
            alerts        = "|".join(alerts) if alerts else None,
        )
        db.session.add(scan)
        db.session.commit()

    history = (
        Scan.query
        .filter_by(user_id=current_user.id)
        .order_by(Scan.timestamp.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "index.html",
        results         = results,
        alerts          = alerts,
        comparison      = comparison,      
        recommendations = recommendations,  
        history         = history,
        image_url       = image_url,
        total_calories  = total_calories,
    )

# LOGIN

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash("Veuillez remplir tous les champs.", "warning")
            return redirect(url_for('main.login'))

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f"Bienvenue, {user.username} !", "success")
            return redirect(url_for('main.index'))

        flash("Nom d'utilisateur ou mot de passe incorrect.", "danger")

    return render_template("auth.html")

# SIGNUP

@bp.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if not username or not password:
        flash("Veuillez remplir tous les champs.", "warning")
        return redirect(url_for('main.login'))

    if len(password) < 6:
        flash("Le mot de passe doit contenir au moins 6 caractères.", "warning")
        return redirect(url_for('main.login'))

    if User.query.filter_by(username=username).first():
        flash("Ce nom d'utilisateur est déjà pris.", "warning")
        return redirect(url_for('main.login'))

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    flash("Compte créé avec succès ! Vous pouvez vous connecter.", "success")
    return redirect(url_for('main.login'))

# LOGOUT

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for('main.login'))

# PROFILE

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            age    = int(request.form.get('age')    or 0)
            poids  = float(request.form.get('poids')  or 0)
            taille = float(request.form.get('taille') or 0)

            if age < 0 or poids < 0 or taille < 0:
                raise ValueError("Valeurs négatives non autorisées")

            current_user.age      = age
            current_user.poids    = poids
            current_user.taille   = taille
            current_user.sexe     = request.form.get('sexe')
            current_user.allergies= request.form.get('allergies', '').strip()
            current_user.maladies = request.form.get('maladies', '').strip()

            db.session.commit()
            flash("Profil mis à jour avec succès.", "success")

        except ValueError:
            flash("Erreur : vérifiez les valeurs saisies (nombres positifs uniquement).", "danger")

        return redirect(url_for('main.profile'))  

    return render_template("profile.html")