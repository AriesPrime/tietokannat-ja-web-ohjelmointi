# Wordle Replica

## Overview

This is a Wordle-inspired web application built with Flask, JavaScript, and PostgreSQL. I’ve also incorporated the Google Chart API ([https://developers.google.com/chart/interactive/docs](https://developers.google.com/chart/interactive/docs)) to visualize SQL data effectively. The game setup is flexible; while classic Wordle gives you six tries to guess a 5-letter word, my version technically allows customization of the board size and the guessable word. For instance, you could configure it to provide 7 tries for guessing a 6-letter word by modifying the code and adding a list of valid 6-letter words.

## Features

- **User Authentication**: Secure signup and login functionality.
- **Gameplay**: Guess the word within six tries, with tile colors providing feedback.
- **Statistics**: Tracks games played, win percentage, current streak, and longest streak.
- **Settings**: Toggle dark mode, high contrast mode, and keyboard-only input.

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- PostgreSQL

### Installation Steps

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/AriesPrime/tietokannat-ja-web-ohjelmointi
   ```

2. **Set Up a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate   # On macOS/Linux
   venv\Scripts\activate    # On Windows
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Database**:

   - Create a PostgreSQL database (e.g., `wordle`).
   - Configure the database connection in a `.env` file:
     ```env
     DATABASE_URL=postgresql://username:password@localhost/wordle
     ```
   - Initialize the database:
     ```bash
     python init_db.py
     ```

5. **Run the Application**:

   ```bash
   flask run
   ```

   Access the app at `http://127.0.0.1:5000`.

## Usage

- **Sign Up**: Create a new account.
- **Log In**: Access your personalized Wordle experience.
- **Play**: Start guessing words and enjoy the game.
- **View Stats**: Check your performance in the stats modal.
- **Adjust Settings**: Use the settings modal to customize your experience.

## Project Structure

```
tietokannat-ja-web-ohjelmointi/
├── app.py                  # Main Flask application
├── db.py                   # Database connection and session setup
├── forms.py                # Flask-WTF forms
├── helpers.py              # Helper functions
├── routes.py               # Flask routes
├── schema.sql              # SQL schema for database
├── words.txt               # List of valid words for the game
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
├── static/                 # Static files
│   ├── css/                # Stylesheets
│   │   ├── main.css
│   │   ├── info.css
│   │   ├── settings.css
│   │   ├── signin.css
│   │   ├── signup.css
│   │   ├── stats.css
│   │   └── wordle.css      # Main Wordle game styles
│   ├── fonts/              # Fonts
│   └── js/                 # JavaScript files
│       └── scripts.js
├── templates/              # HTML templates
│   ├── modals/             # Modal templates
│   │   ├── info.html       # How-to-play modal
│   │   ├── settings.html   # Settings modal
│   │   └── stats.html      # Statistics modal
│   ├── signin.html         # Sign-in page
│   ├── signup.html         # Sign-up page
│   └── wordle.html         # Main Wordle game page
├── models/                 # Modularized models
│   ├── __init__.py         # Module initializer
│   ├── distribution.py     # Guess distribution model
│   ├── game.py             # Game-related model
│   ├── leaderboard.py      # Leaderboard-related model
│   ├── settings.py         # Settings-related model
│   ├── stats.py            # Game statistics model
│   └── users.py            # User-related model
├── venv/                   # Virtual environment
│   └── ...                 # Virtual environment files

```

## Database Tables

### User Table

Stores information about the users of the application.

- **id**: Primary key, unique identifier for the user.
- **username**: Unique username chosen by the user.
- **email**: Unique email address.
- **password\_hash**: Encrypted password.
- **created\_at**: Timestamp for when the user account was created.

### Game Table

Tracks the details of each game played by a user.

- **id**: Primary key, unique identifier for the game.
- **user\_id**: Foreign key referencing the user who played the game.
- **attempt**: Number of attempts made.
- **guesses**: The guesses made by the user.
- **correct\_word**: The word to guess.
- **is\_completed**: Whether the game was completed.
- **is\_won**: Whether the user won the game.
- **started\_at**: Timestamp for when the game started.
- **ended\_at**: Timestamp for when the game ended.

### Settings Table

Stores user-specific settings for the application.

- **id**: Primary key, unique identifier for the settings.
- **user\_id**: Foreign key referencing the user.
- **dark\_mode**: Boolean indicating if dark mode is enabled.
- **high\_contrast**: Boolean indicating if high contrast mode is enabled.
- **keyboard\_only**: Boolean indicating if on-screen keyboard-only input is enabled.

### GameStats Table

Tracks statistics for each user.

- **id**: Primary key, unique identifier for the stats.
- **user\_id**: Foreign key referencing the user.
- **games\_played**: Total games played by the user.
- **games\_won**: Total games won by the user.
- **total\_attempts**: Total attempts made across all games.
- **longest\_streak**: Longest winning streak.
- **current\_streak**: Current winning streak.

### Leaderboard Table

Stores data for displaying the leaderboard.

- **id**: Primary key, unique identifier for the leaderboard entry.
- **user\_id**: Foreign key referencing the user.
- **username**: The username of the player.
- **games\_won**: Total games won by the player.
- **longest\_streak**: Player’s longest winning streak.
- **win\_rate**: Winning rate calculated as games won divided by games played.
- **average\_attempts**: Average attempts per game.

### Distribution Table

Tracks the distribution of guesses for each user.

- **id**: Primary key, unique identifier for the distribution.
- **user\_id**: Foreign key referencing the user.
- **one**: Number of games won in 1 guess.
- **two**: Number of games won in 2 guesses.
- **three**: Number of games won in 3 guesses.
- **four**: Number of games won in 4 guesses.
- **five**: Number of games won in 5 guesses.
- **six**: Number of games won in 6 guesses.

## Features To Be Added

- **Leaderboard**: Add functionality to display top players and their rankings.
- **Code Optimization**: Refactor and optimize the code for better performance and readability.
- **Visual Enhancements**: Implement core animations to improve the game's user experience.
- **Reponjsiveness**: Implement Responsive Web Design.