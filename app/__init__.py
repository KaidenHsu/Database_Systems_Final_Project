from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

# Initialize the Flask application
app = Flask(__name__)

# Set the secret key for session management and other security purposes
app.config['SECRET_KEY'] = 'your_secret_key'

# Configure the database URI; here, it uses SQLite with the database file named 'site.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Initialize SQLAlchemy with the Flask app for ORM capabilities
db = SQLAlchemy(app)

# Initialize Bcrypt with the Flask app for hashing passwords
bcrypt = Bcrypt(app)

# Initialize LoginManager with the Flask app to manage user sessions
login_manager = LoginManager(app)
# Set the login view, which is the route that users will be redirected to if they need to log in
login_manager.login_view = 'login'

# Initialize Flask-Migrate with the Flask app and SQLAlchemy database instance for handling migrations
migrate = Migrate(app, db)

# Import routes and models to ensure they are registered with the Flask app
# This should be done after the app and its extensions are initialized to avoid circular imports
from app import routes, models