from flask_migrate import Migrate
from .api import app, db

migrate = Migrate(app, db)

from . import models
