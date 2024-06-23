from datetime import datetime, timezone
from flask_login import UserMixin
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    usr_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    subscriptions = db.relationship('Subscription', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    rents = db.relationship('Rent', backref='user', lazy=True)

    def get_id(self):
        return str(self.usr_id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.phone}')"

class Movie(db.Model):
    mov_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    rel_year = db.Column(db.Integer, nullable=False)
    reviews = db.relationship('Review', backref='movie', lazy=True, cascade="all, delete-orphan")
    rents = db.relationship('Rent', backref='movie', lazy=True, cascade="all, delete-orphan")
    genres = db.relationship('MovieGenre', backref='movie', lazy=True, cascade="all, delete-orphan")

    @property
    def rating(self):
        reviews = [review.rating for review in self.reviews if review.rating is not None]
        return sum(reviews) / len(reviews) if reviews else 0

    def __repr__(self):
        return f"Movie('{self.title}', '{self.rel_year}', '{self.rating}')"

class Subscription(db.Model):
    sub_id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.Date, nullable=False, default=datetime.now(timezone.utc))
    end = db.Column(db.Date, nullable=False, default=datetime(9999, 12, 31))
    usr_id = db.Column(db.Integer, db.ForeignKey('user.usr_id'), nullable=False)

    def __repr__(self):
        return f"Subscription('{self.plan}', '{self.start}', '{self.end}')"

class Review(db.Model):
    rev_id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, default=datetime.now(timezone.utc))
    usr_id = db.Column(db.Integer, db.ForeignKey('user.usr_id'), nullable=False)
    mov_id = db.Column(db.Integer, db.ForeignKey('movie.mov_id'), nullable=False)

    def __repr__(self):
        return f"Review('{self.rating}', '{self.date}', '{self.comment}')"

class Genre(db.Model):
    gen_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    movies = db.relationship('MovieGenre', backref='genre', lazy=True)

    def __repr__(self):
        return f"Genre('{self.name}')"

class Rent(db.Model):
    usr_id = db.Column(db.Integer, db.ForeignKey('user.usr_id'), primary_key=True)
    mov_id = db.Column(db.Integer, db.ForeignKey('movie.mov_id'), primary_key=True)
    start = db.Column(db.Date, nullable=False)
    end = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"Rent('User: {self.usr_id}', 'Movie: {self.mov_id}', '{self.start} to {self.end}')"

class MovieGenre(db.Model):
    mov_id = db.Column(db.Integer, db.ForeignKey('movie.mov_id'), primary_key=True)
    gen_id = db.Column(db.Integer, db.ForeignKey('genre.gen_id'), primary_key=True)

    def __repr__(self):
        return f"MovieGenre('Movie: {self.mov_id}', 'Genre: {self.gen_id}')"