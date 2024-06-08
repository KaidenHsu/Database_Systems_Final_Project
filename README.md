# Movie Streaming Platform Management System
This repo is my final project for the course "Database Systems" in NCCU.

## Caveat
Please note that code in this repo is intended solely for demo purposes and is susceptible to various bugs. Please DO NOT use it in practice!

## E-R Diagram
<img src="./images/ER_Diagram.jpg" alt="Load failed" width="420" height="594">

## Relational Schema
<img src="./images/Schema_1.jpg" alt="Load failed" width="420" height="594">
<img src="./images/Schema_2.jpg" alt="Load failed" width="420" height="594">

## System Function Analysis

The system provides the following key functionalities:

1. **User Management**
   - **Registration**: New users can register by providing necessary details such as password and phone.
   - **Authentication**: Users can log in using their `usr_id` and password.
   - **Profile Management**: Users can update their profile details.

2. **Movie Management**
   - **Add New Movies**: Admins can add new movies with details like title, description, `rel_year`, and rating.
   - **Update Movie Details**: Admins can update movie information.
   - **Delete Movies**: Admins can remove movies from the database.

3. **Subscription Management**
   - **Subscribe**: Users can subscribe to different plans with specific start and end dates.
   - **View Subscriptions**: Users can view their current and past subscriptions.
   - **Cancel Subscription**: Users can cancel their ongoing subscriptions.

4. **Rental Management**
   - **Rent Movies**: Users can rent movies by specifying the start and end dates.
   - **View Rentals**: Users can view their current and past rentals.

5. **Review Management**
   - **Add Reviews**: Users can review movies by providing rating, comment, and date.
   - **Edit Reviews**: Users can update their reviews.
   - **Delete Reviews**: Users can remove their reviews.

6. **Genre Management**
   - **Add Genres**: Admins can add new genres to the database.
   - **Assign Genres to Movies**: Admins can categorize movies by assigning genres.
   - **View Genres**: Users can view the list of available genres.

7. **Search and Browse**
   - **Search Movies**: Users can search for movies based on title, description, `rel_year`, rating, and genre.
   - **Browse by Genre**: Users can browse movies categorized under different genres.