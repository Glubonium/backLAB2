from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
app = Flask(__name__)

# app.config.from_pyfile('config.py', silent=True)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:aot1@localhost/L3"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

import my_app.views
import my_app.model
