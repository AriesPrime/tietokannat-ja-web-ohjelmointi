from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import login_user, logout_user, login_required, current_user
from models import distributions, users, game, settings, stats, leaderboard

from forms import SignupForm, SigninForm
import helpers

app_routes = Blueprint('app_routes', __name__)


def redirect_if_authenticated():
    if current_user.is_authenticated:
        return redirect(url_for('app_routes.wordle'))
    return None


@app_routes.route('/')
def root():
    return redirect(url_for('app_routes.wordle'))


@app_routes.route('/<path:unknown_path>')
def catch_all(unknown_path):
    return redirect(url_for('app_routes.wordle'))


@app_routes.route('/wordle')
@login_required
def wordle():
    return render_template('wordle.html', user=current_user)


@app_routes.route('/validate_word', methods=['post'])
@login_required
def validate_word():
    word = request.get_json().get('word', '').lower()
    return jsonify({'is_valid': helpers.is_valid_word(word)})


@app_routes.route('/get_stats', methods=['get'])
@login_required
def get_stats():
    return jsonify(stats.get_stats(current_user.id))


@app_routes.route('/get_distribution', methods=['get'])
@login_required
def get_distribution():
    return jsonify(distributions.get_distribution(current_user.id))


@app_routes.route('/new_game', methods=['post'])
@login_required
def new_game():
    correct_word = helpers.get_random_word()

    if game.new_game(current_user.id, correct_word):
        return jsonify({'success': True}), 200

    return jsonify({'success': False, 'error': 'Failed to start new game.'}), 500


@app_routes.route('/save_guess', methods=['post'])
@login_required
def save_guess():
    guess = request.get_json().get('guess', '').lower()

    success, response = game.save_guess(current_user.id, guess)

    if success:
        if response['game_over']:
            stats.update_stats(current_user.id, response)
            leaderboard.update_leaderboard(
                current_user.id, stats.get_stats(current_user.id))
            distributions.update_distribution(
                current_user.id, response['guess_count'])

        return jsonify({'success': True, 'response': response}), 200

    return jsonify({'success': False, 'error': 'Failed to save guess.'}), 500


@app_routes.route('/last_game', methods=['get'])
@login_required
def last_game():
    success, response = game.last_game(current_user.id)

    if success:
        return jsonify({'success': True, 'game': response}), 200

    return jsonify({'success': False, 'message': 'No games found'}), 200


@app_routes.route('/get_settings', methods=['get'])
@login_required
def get_settings():
    return jsonify(settings.get_settings(current_user.id))


@app_routes.route('/set_settings', methods=['post'])
@login_required
def set_settings():
    data = request.get_json()
    success = settings.set_settings(
        current_user.id,
        data.get('dark_mode'),
        data.get('high_contrast'),
        data.get('keyboard_only')
    )

    if success:
        return jsonify({'success': True}), 200
    return jsonify({'success': False, 'error': 'Failed to save settings.'}), 500


@app_routes.route('/signup', methods=['get', 'post'])
def signup():
    redirect_response = redirect_if_authenticated()
    if redirect_response:
        return redirect_response

    form = SignupForm()
    message = None

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        success, error_message = users.signup(username, email, password)
        if success:
            return redirect(url_for('app_routes.signin'))
        message = error_message

    return render_template('signup.html', form=form, message=message)


@app_routes.route('/signin', methods=['get', 'post'])
def signin():
    redirect_response = redirect_if_authenticated()
    if redirect_response:
        return redirect_response

    form = SigninForm()
    message = None

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user_obj = users.signin(username, password)
        if user_obj:
            login_user(user_obj)
            return redirect(url_for('app_routes.wordle'))
        message = 'Invalid username or password.'

    return render_template('signin.html', form=form, message=message)


@app_routes.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('app_routes.signin'))
