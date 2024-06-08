from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456789@3306/pyflaskweb'
db = SQLAlchemy(app)

from shop import routes