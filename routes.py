from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Game, GameStats, Leaderboard, Settings, Distribution

from forms import SignupForm, SigninForm
from helpers import get_random_word, valid_words

app_routes = Blueprint('app_routes', __name__)

def redirect_if_authenticated():
    if current_user.is_authenticated:
        return redirect(url_for('app_routes.wordle'))
    return None

@app_routes.route('/')
def root():
    return redirect(url_for('app_routes.wordle'))

@app_routes.route('/wordle')
@login_required
def wordle():
    return render_template('wordle.html', user=current_user,)

@app_routes.route('/api/most_recent_game', methods=['GET'])
@login_required
def most_recent_game():
    game = Game.query.filter_by(user_id=current_user.id).order_by(Game.id.desc()).first()

    if not game:
        return jsonify({"guesses": [], "correct_word": None})

    guesses = game.guesses.split(",") if game.guesses else []
    return jsonify({
        "game_id": game.id,
        "guesses": guesses,
        "correct_word": game.correct_word,
        "is_completed": game.is_completed
    })

@app_routes.route('/api/validate_word', methods=['POST'])
@login_required
def check_word():
    data = request.get_json()
    word = data.get('word', '').lower()
    is_valid = word in valid_words

    return jsonify({'is_valid': is_valid})

@app_routes.route('/api/save_guess', methods=['POST'])
@login_required
def save_guess():
    data = request.get_json()
    guess = data.get('guess', '').lower()

    game = Game.query.filter_by(user_id=current_user.id).order_by(Game.id.desc()).first()
    distribution = Distribution.query.filter_by(user_id=current_user.id).first()

    if not game:
        return jsonify({'success': False, 'error': 'No active game found.'})
    
    if not distribution:
        distribution = Distribution(user_id=current_user.id)
        db.session.add(distribution)

    guesses = game.guesses.split(",") if game.guesses else []
    guesses.append(guess)
    game.guesses = ",".join(guesses)

    if guess == game.correct_word:
        game.is_completed = True
        game.is_won = True
        game.ended_at = db.func.now()
        game.attempt = len(guesses)
        distribution.update_distribution(len(guesses))
    elif len(guesses) >= 6:
        game.is_completed = True
        game.is_won = False
        game.ended_at = db.func.now()
        game.attempt = len(guesses)

    if game.is_completed:
        update_game_stats_and_leaderboard(game)

    try:
        db.session.commit()
        return jsonify({'success': True, 'game_over': game.is_completed, 'guessCount': len(guesses)})
    except Exception as e:
        print(f"Error saving guess: {e}")
        return jsonify({'success': False, 'error': 'Database error.'})

@app_routes.route('/api/new_game', methods=['POST'])
@login_required
def new_game():
    try:
        game = Game.query.filter_by(user_id=current_user.id).order_by(Game.id.desc()).first()

        if game and not game.is_completed:
            print(f"Error: Active game exists with ID {game.id}")
            return jsonify({'success': False, 'error': 'You must complete your current game before starting a new one.'}), 400

        new_word = get_random_word()

        new_game = Game(
            user_id=current_user.id,
            correct_word=new_word,
            guesses=""
        )
        db.session.add(new_game)
        db.session.commit()

        print(f"New game created with ID {new_game.id} and word {new_word}")
        return jsonify({'success': True, 'correct_word': new_word}), 200
    except Exception as e:
        print(f"Error starting a new game: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'An error occurred while starting a new game. Please try again later.'}), 500

@app_routes.route('/api/get_settings', methods=['GET'])
@login_required
def get_settings():
    settings = Settings.query.filter_by(user_id=current_user.id).first()

    if not settings:
        return jsonify({
            "dark_mode": False,
            "high_contrast": False,
            "keyboard_input_only": False,
        })

    return jsonify({
        "dark_mode": settings.dark_mode,
        "high_contrast": settings.high_contrast,
        "keyboard_only": settings.keyboard_only,
    })

@app_routes.route('/api/set_settings', methods=['POST'])
@login_required
def save_settings():
    data = request.get_json()

    if not all(key in data for key in ["dark_mode", "high_contrast", "keyboard_only"]):
        return jsonify({"error": "Missing settings keys"}), 400

    settings = Settings.query.filter_by(user_id=current_user.id).first()
    if not settings:
        settings = Settings(user_id=current_user.id)

    settings.dark_mode = data["dark_mode"]
    settings.high_contrast = data["high_contrast"]
    settings.keyboard_only = data["keyboard_only"]

    db.session.add(settings)
    db.session.commit()

    return jsonify({"message": "Settings saved successfully"}), 200


@app_routes.route('/api/get_stats', methods=['GET'])
@login_required
def get_stats():
    try:
        stats = GameStats.query.filter_by(user_id=current_user.id).first()
        leaderboard = Leaderboard.query.filter_by(user_id=current_user.id).first()

        if not stats:
            return jsonify({
                "success": True,
                "data": {
                    "games_played": 0,
                    "games_won": 0,
                    "win_rate": 0,
                    "longest_streak": 0,
                    "current_streak": 0,
                    "average_attempts": 0,
                }
            })

        return jsonify({
            "success": True,
            "data": {
                "games_played": stats.games_played,
                "games_won": stats.games_won,
                "win_rate": leaderboard.win_rate if leaderboard else 0,
                "longest_streak": stats.longest_streak,
                "current_streak": stats.current_streak,
                "average_attempts": leaderboard.average_attempts if leaderboard else 0,
            }
        })
    except Exception as e:
        print(f"Error fetching statistics: {e}")
        return jsonify({"success": False, "error": "Failed to fetch statistics."}), 500

@app_routes.route('/api/get_distribution', methods=['GET'])
@login_required
def get_guess_distribution():
    guess_distribution = Distribution.query.filter_by(user_id=current_user.id).first()

    if not guess_distribution:
        return jsonify({
            "one": 0,
            "two": 0,
            "three": 0,
            "four": 0,
            "five": 0,
            "six": 0,
        })

    return jsonify({
        "one": guess_distribution.one,
        "two": guess_distribution.two,
        "three": guess_distribution.three,
        "four": guess_distribution.four,
        "five": guess_distribution.five,
        "six": guess_distribution.six,
    })



@app_routes.route('/signup', methods=['GET', 'POST'])
def signup():
    redirect_response = redirect_if_authenticated()
    if redirect_response:
        return redirect_response

    form = SignupForm()
    message = None

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            message = "Username already exists. Please choose another."
        elif User.query.filter_by(email=form.email.data).first():
            message = "Email already registered. Please use a different email."
        else:
            new_user = User(
                username=form.username.data,
                email=form.email.data
            )
            new_user.set_password(form.password.data)
            db.session.add(new_user)

            default_settings = Settings(
                user_id=new_user.id,
                dark_mode=False,
                high_contrast=False,
                keyboard_only=False
            )
            db.session.add(default_settings)
            db.session.commit()
            return redirect(url_for('app_routes.signin'))

    return render_template('signup.html', form=form, message=message)

@app_routes.route('/signin', methods=['GET', 'POST'])
def signin():
    redirect_response = redirect_if_authenticated()
    if redirect_response:
        return redirect_response

    form = SigninForm()
    message = None

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('app_routes.wordle'))
        else:
            message = "Invalid username or password. Please try again."

    return render_template('signin.html', form=form, message=message)

@app_routes.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('app_routes.signin'))

def update_game_stats_and_leaderboard(game):
    stats = GameStats.query.filter_by(user_id=current_user.id).first()
    if not stats:
        stats = GameStats(user_id=current_user.id)
        db.session.add(stats)

    stats.update_stats(game)

    leaderboard = Leaderboard.query.filter_by(user_id=current_user.id).first()
    if not leaderboard:
        leaderboard = Leaderboard(user_id=current_user.id, username=current_user.username)
        db.session.add(leaderboard)

    leaderboard.update_leaderboard(stats)
