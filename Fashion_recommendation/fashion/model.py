from datetime import datetime , timezone
from fashion import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader 
def load_user(user_id):
    return User.query.get(int(user_id))




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    image_file = db.Column(db.String(20), nullable = False, default = 'default.jpg')
    password = db.Column(db.String(60), nullable = False)
    info = db.relationship('Info', backref = 'user', uselist = False)
    recommendation = db.relationship('Recommendation',backref = 'user',uselist = False)
    prompt = db.relationship('Prompt',backref = 'user', lazy = True)
    categories = db.relationship('Category', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),unique = True, nullable=False)
    style_preference = db.Column(db.String(100), nullable=False, default = 'casual') # e.g., casual, formal, trendy
    body_type = db.Column(db.String(100), nullable=False,default = 'M')  
    gender = db.Column(db.String(100), nullable=False, default = 'male')  # e.g. student, teacher 
    color_preference = db.Column(db.String(100), nullable=False, default = 'black')  # e.g., black, blue

    def __repr__(self):
        return f"Info('{self.style_preference}', '{self.body_type}', '{self.gender}','{self.color_preference}')"
    
class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    prompt_text = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"Result('{self.prompt_text}')"

class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recommended_item = db.Column(db.String(200), nullable=False)  # e.g., outfit name or ID
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"Recommendation('{self.user_id}', '{self.recommended_item}')"
    
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cat_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"{self.id}"

# New Item table
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Dynamically create columns based on category
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"Item('{self.name}', Category ID: '{self.category_id}')"
 