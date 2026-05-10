from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    age = db.Column(db.Integer)
    poids = db.Column(db.Float)
    taille = db.Column(db.Float)
    sexe = db.Column(db.String(10))
    maladies = db.Column(db.Text, default="")
    allergies = db.Column(db.Text, default="")

    calories_consumed = db.Column(db.Float, default=0.0)
    last_reset = db.Column(db.DateTime, default=datetime.utcnow)
    daily_goal = db.Column(db.Float, default=2000.0)

    scans = db.relationship('Scan', backref='owner', lazy='select', cascade="all, delete-orphan")
    def check_daily_reset(self):
        """Réinitialise les calories si nous sommes un nouveau jour."""
        now = datetime.utcnow()
        if self.last_reset.date() < now.date():
            self.calories_consumed = 0.0
            self.last_reset = now
            return True
        return False
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_besoins_caloriques(self):
        if not self.poids or not self.taille or not self.age:
            return 2200

        if self.sexe == 'H':
            return (13.397 * self.poids) + (4.799 * self.taille) - (5.677 * self.age) + 88.362
        return (9.247 * self.poids) + (3.098 * self.taille) - (4.330 * self.age) + 447.593

    def get_allergies_list(self):
        if not self.allergies:
            return []
        return [a.strip().lower() for a in self.allergies.split(',') if a.strip()]

    def get_maladies_list(self):
        if not self.maladies:
            return []
        return [m.strip().lower() for m in self.maladies.split(',') if m.strip()]

    def profile_complete(self):
        return all([self.age, self.poids, self.taille, self.sexe])

    def __repr__(self):
        return f'<User {self.username}>'


class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(200))
    food_list = db.Column(db.Text)
    total_calories = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    alerts = db.Column(db.Text)

    def get_alerts_list(self):
        if not self.alerts:
            return []
        return self.alerts.split('|')

    def __repr__(self):
        return f'<Scan {self.id} - {self.food_list[:30]}>'