from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from gensim.models import KeyedVectors



app = Flask(__name__)
app.config['SECRET_KEY'] = '05bdd74ddb0e228e401a5dbab791efe2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fashion.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app) 
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'

path_to_model = 'fashion/GoogleNews-vectors-negative300.bin.gz'
print('start')
google_model = KeyedVectors.load_word2vec_format(path_to_model, binary=True)
print('done')



import fashion.routes

