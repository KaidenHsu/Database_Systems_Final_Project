from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, MovieForm, UpdateAccountForm, \
      UpdatePhoneForm, UpdatePasswordForm, SubscriptionForm, RentForm, ReviewForm
from app.models import User, Movie, Subscription, Rent, Review, Genre, MovieGenre
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime, timedelta
from sqlalchemy import desc, func
from datetime import datetime, timezone

# Home route
@app.route("/")
@app.route("/home")
def home():
    rented_movie_ids = [rent.mov_id for rent in current_user.rents] if current_user.is_authenticated else []
    available_movies = db.session.query(Movie).filter(~Movie.mov_id.in_(rented_movie_ids)).all()
    available_movies_sorted = sorted(available_movies, key=lambda m: m.rating, reverse=True)
    rented_movies = current_user.rents if current_user.is_authenticated else []
    all_genres = Genre.query.all()
    return render_template('home.html', available_movies=available_movies_sorted, rented_movies=rented_movies, all_genres=all_genres)

# Register route
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username is already taken. Please choose a different one.', 'danger')
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, password_hash=hashed_password, phone=form.phone.data)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# Login route
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

# Logout route
@app.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

# Define your admin key (ensure this is secure in a real application)
ADMIN_KEY = 'your_admin_key_here'

@app.route("/admin")
def admin():
    admin_key = request.args.get('admin_key')
    if admin_key != ADMIN_KEY:
        return "Forbidden", 403

    movies = Movie.query.all()
    users = User.query.all()
    all_genres = Genre.query.all()
    return render_template('admin.html', movies=movies, users=users, all_genres=all_genres, datetime=datetime, timezone=timezone)

@app.route("/admin/movie/new", methods=['GET', 'POST'])
@login_required
def admin_new_movie():
    admin_key = request.args.get('admin_key')
    if admin_key != 'your_admin_key_here':
        return "Forbidden", 403

    form = MovieForm()
    if form.validate_on_submit():
        movie = Movie(title=form.title.data, description=form.description.data, rel_year=form.rel_year.data)
        db.session.add(movie)
        db.session.commit()

        # Add genres to the movie
        genre_ids = request.form.get("selected_genres", "").split(",")
        for genre_id in genre_ids:
            if genre_id:
                movie_genre = MovieGenre(mov_id=movie.mov_id, gen_id=int(genre_id))
                db.session.add(movie_genre)
        
        db.session.commit()
        flash('The movie has been added!', 'success')
        return redirect(url_for('admin', admin_key='your_admin_key_here'))

    all_genres = Genre.query.all()
    return render_template('admin_new_movie.html', title='Add New Movie', form=form, all_genres=all_genres)

@app.route("/admin/movie/<int:movie_id>/edit", methods=['GET', 'POST'])
@login_required
def admin_update_movie(movie_id):
    admin_key = request.args.get('admin_key')
    if admin_key != 'your_admin_key_here':
        return "Forbidden", 403

    movie = Movie.query.get_or_404(movie_id)
    form = MovieForm(obj=movie)

    if form.validate_on_submit():
        movie.title = form.title.data
        movie.description = form.description.data
        movie.rel_year = form.rel_year.data
        db.session.commit()

        # Update genres for the movie
        selected_genres = request.form.get("selected_genres", "").split(",")
        movie_genres = MovieGenre.query.filter_by(mov_id=movie_id).all()
        existing_genres = set(genre.gen_id for genre in movie_genres)
        new_genres = set(int(genre_id) for genre_id in selected_genres if genre_id)

        # Remove genres not in the new selection
        for genre_id in existing_genres - new_genres:
            movie_genre = MovieGenre.query.filter_by(mov_id=movie_id, gen_id=genre_id).first()
            if movie_genre:
                db.session.delete(movie_genre)

        # Add new genres
        for genre_id in new_genres - existing_genres:
            movie_genre = MovieGenre(mov_id=movie_id, gen_id=genre_id)
            db.session.add(movie_genre)

        db.session.commit()
        flash('The movie has been updated!', 'success')
        return redirect(url_for('admin', admin_key='your_admin_key_here'))

    all_genres = Genre.query.all()
    movie_genre_ids = [genre.gen_id for genre in movie.genres]
    return render_template('admin_update_movie.html', title='Update Movie', form=form, all_genres=all_genres, movie_genre_ids=movie_genre_ids, movie=movie)

@app.route("/admin/movie/<int:movie_id>/delete", methods=['POST'])
def admin_delete_movie(movie_id):
    if request.args.get('admin_key') != ADMIN_KEY:
        abort(403)  # Forbidden
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Movie has been deleted by admin!', 'success')
    return redirect(url_for('admin', admin_key=ADMIN_KEY))

@app.route("/admin/genres", methods=['GET', 'POST'])
@login_required
def admin_manage_genres():
    admin_key = request.args.get('admin_key')
    if admin_key != 'your_admin_key_here':
        return "Forbidden", 403

    if request.method == 'POST':
        if 'add_genre' in request.form:
            genre_name = request.form.get('genre_name')
            if genre_name:
                new_genre = Genre(name=genre_name)
                db.session.add(new_genre)
                db.session.commit()
                flash('New genre added successfully!', 'success')
        elif 'delete_genre' in request.form:
            genre_id = request.form.get('delete_genre')
            genre_to_delete = Genre.query.get(genre_id)
            if genre_to_delete:
                # Delete associated entries in the movie_genre table
                MovieGenre.query.filter_by(gen_id=genre_id).delete()
                db.session.delete(genre_to_delete)
                db.session.commit()
                flash('Genre deleted successfully!', 'success')

    all_genres = Genre.query.all()
    return render_template('admin_manage_genres.html', title='Manage Genres', genres=all_genres, admin_key=admin_key)

@app.route("/profile")
@login_required
def profile():
    current_subscription = current_user.subscriptions[-1] if current_user.subscriptions and current_user.subscriptions[-1].end > datetime.now(timezone.utc).date() else None
    return render_template('profile.html', current_subscription=current_subscription, datetime=datetime, timezone=timezone)

@app.route("/update_phone", methods=['GET', 'POST'])
@login_required
def update_phone():
    form = UpdatePhoneForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password_hash, form.password.data):
            current_user.phone = form.new_phone.data
            db.session.commit()
            flash('Your phone number has been updated!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Incorrect password.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", 'danger')
    return render_template('update_phone.html', form=form)

@app.route("/update_password", methods=['GET', 'POST'])
@login_required
def update_password():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.old_password.data):
            if form.new_password.data == form.confirm_new_password.data:
                user.password_hash = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
                db.session.commit()
                flash('Your password has been updated!', 'success')
                return redirect(url_for('profile'))
            else:
                flash('New passwords do not match.', 'danger')
        else:
            flash('Incorrect old password.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", 'danger')
    return render_template('update_password.html', form=form)

@app.route("/update_subscription", methods=['GET', 'POST'])
@login_required
def update_subscription():
    form = SubscriptionForm()
    if request.method == 'POST':
        duration = request.form.get('duration')
        
        if duration == '1_month':
            new_end_date = datetime.now(timezone.utc).date() + timedelta(days=30)
            if current_user.subscriptions:
                current_user.subscriptions[-1].end = new_end_date
            else:
                new_subscription = Subscription(start=datetime.now(timezone.utc).date(), end=new_end_date, usr_id=current_user.usr_id)
                db.session.add(new_subscription)
            flash('Subscription updated for 1 month!', 'success')
        
        elif duration == '1_year':
            new_end_date = datetime.now(timezone.utc).date() + timedelta(days=365)
            if current_user.subscriptions:
                current_user.subscriptions[-1].end = new_end_date
            else:
                new_subscription = Subscription(start=datetime.now(timezone.utc).date(), end=new_end_date, usr_id=current_user.usr_id)
                db.session.add(new_subscription)
            flash('Subscription updated for 1 year!', 'success')
        
        elif duration == 'cancel':
            if current_user.subscriptions:
                current_user.subscriptions[-1].end = datetime.now(timezone.utc).date()
            flash('Subscription canceled.', 'success')
        
        db.session.commit()
        return redirect(url_for('profile'))

    current_subscription = current_user.subscriptions[-1] if current_user.subscriptions else None
    return render_template('update_subscription.html', title='Update Subscription', form=form, current_subscription=current_subscription, datetime=datetime, timezone=timezone)

@app.route("/delete_account", methods=['POST'])
@login_required
def delete_account():
    user = current_user
    try:
        # Delete all related subscriptions
        Subscription.query.filter_by(usr_id=user.usr_id).delete()

        # Delete all related rents
        Rent.query.filter_by(usr_id=user.usr_id).delete()

        # Delete all related reviews
        Review.query.filter_by(usr_id=user.usr_id).delete()

        # Finally, delete the user
        db.session.delete(user)
        db.session.commit()
        flash('Your account has been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while trying to delete your account.', 'danger')
        print(f"Error: {e}")

    logout_user()
    return redirect(url_for('home'))

@app.route("/movie/<int:movie_id>/rent", methods=['GET', 'POST'])
@login_required
def rent_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    form = RentForm()
    if form.validate_on_submit():
        start_date = datetime.today().date()
        end_date = form.end_date.data
        if end_date <= start_date:
            flash('End date must be after today.', 'danger')
        else:
            rent = Rent(usr_id=current_user.usr_id, mov_id=movie.mov_id, start=start_date, end=end_date)
            db.session.add(rent)
            db.session.commit()
            flash(f'You have successfully rented {movie.title}!', 'success')
            return redirect(url_for('movie_details', movie_id=movie.mov_id))
    return render_template('movie_details.html', title='Rent Movie', form=form, movie=movie, datetime=datetime, timezone=timezone)

@app.route("/my_rentals")
@login_required
def my_rentals():
    rentals = Rent.query.filter_by(usr_id=current_user.usr_id).all()
    return render_template('my_rentals.html', title='My Rentals', rentals=rentals)

@app.route("/movie/<int:movie_id>", methods=['GET', 'POST'])
@login_required
def movie_details(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    form = RentForm()
    if form.validate_on_submit():
        start_date = datetime.now(timezone.utc).date()
        end_date = form.end_date.data
        if end_date <= start_date:
            flash('End date must be after start date.', 'danger')
        else:
            rent = Rent(usr_id=current_user.usr_id, mov_id=movie.mov_id, start=start_date, end=end_date)
            db.session.add(rent)
            db.session.commit()
            flash(f'You have successfully rented {movie.title}!', 'success')
            return redirect(url_for('home'))

    return render_template('movie_details.html', title=movie.title, movie=movie, form=form, datetime=datetime, timezone=timezone)

@app.route("/add_review/<int:movie_id>", methods=['GET', 'POST'])
@login_required
def add_review(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    existing_review = Review.query.filter_by(usr_id=current_user.usr_id, mov_id=movie_id).first()
    if existing_review:
        return redirect(url_for('update_review', review_id=existing_review.rev_id))
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(rating=form.rating.data, comment=form.comment.data, usr_id=current_user.usr_id, mov_id=movie_id)
        db.session.add(review)
        db.session.commit()
        flash('Your review has been added!', 'success')
        return redirect(url_for('home'))
    return render_template('add_review.html', title='Add Review', form=form, movie=movie)

@app.route("/update_review/<int:review_id>", methods=['GET', 'POST'])
@login_required
def update_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.usr_id != current_user.usr_id:
        flash('You cannot update this review.', 'danger')
        return redirect(url_for('home'))
    form = ReviewForm(obj=review)
    if form.validate_on_submit():
        review.rating = form.rating.data
        review.comment = form.comment.data
        db.session.commit()
        flash('Your review has been updated!', 'success')
        return redirect(url_for('home'))
    return render_template('add_review.html', title='Update Review', form=form, movie=review.movie)