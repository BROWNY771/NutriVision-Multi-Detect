import sys
import os

ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.append(ROOT_DIR)

from app import create_app
from app.models import User

app = create_app()

with app.app_context():

    users = User.query.all()

    print(users)