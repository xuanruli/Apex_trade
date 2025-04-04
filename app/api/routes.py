from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app.models.user import User
from app.services.auth import verify_exist, authorize_user, oauth_login_google
from app.services.alpha_vantage import get_time_series_for_stock
from app.services.chart import create_candlestick_chart, create_line_chart, create_bar_chart, convert_dict_to_df
from plotly.io import to_html
api_bp = Blueprint('api', __name__)


@api_bp.route('/')
def index():
    return render_template('index.html')

@api_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # verify user
        if not authorize_user(username, password):
            flash('Username not exist or password not match. Please try again', 'error')
            return render_template('login.html')

        user = User.get_by_username(username)
        session['user_id'] = user['id']

        return redirect(url_for('api.portfolio'))
    else: # GET
        return render_template('login.html')

@api_bp.route('/login-with-google')
def google_login():
    """deal with google log in request"""
    return oauth_login_google()

@api_bp.route('/logout')
def logout():
    # Clear session data
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('api.index'))

@api_bp.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')

        # sign up logic
        if verify_exist(username, email):
            flash('Username or email already exists. Please choose a different one or log in.', 'error')
            return render_template('signup.html')

        # register user
        User(username, email, firstname, lastname, password).save()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('api.login'))
    else: # GET
        return render_template('signup.html')

# need format like asset <
@api_bp.route('/asset')
def asset():
    # Get time series data and create charts
    data = get_time_series_for_stock('AAPL')
    df = convert_dict_to_df(data)

    # Create charts and convert them to HTML
    candlestick_chart = to_html(create_candlestick_chart(df, 'AAPL'), full_html=False)
    line_chart = to_html(create_line_chart(df, 'AAPL'), full_html=False)
    bar_chart = to_html(create_bar_chart(df, 'AAPL'), full_html=False)

    # Create stock dictionary with all required fields
    stock = {
        'Symbol': 'AAPL',
        'Name': 'Apple Inc.',
        'Exchange': 'NASDAQ',
        'Price': 175.34,
        'WeekHigh': 182.63,
        'WeekLow': 164.08,
        'Sector': 'Technology',
        'Industry': 'Consumer Electronics',
        'MarketCap': '2.75T',
        'PERatio': 28.5,
        'EPS': 6.15,
        'Dividend': 0.92,
        'DividendYield': 0.53
    }

    return render_template('asset.html',
                         stock=stock,
                         candlestick_chart=candlestick_chart,
                         line_chart=line_chart,
                         bar_chart=bar_chart)


@api_bp.route('/portfolio')
def portfolio():
    user_id = session.get('user_id')
    # ...
    return render_template('portfolio.html')

@api_bp.route('/news')
def news():
    # ...
    return render_template('news.html')

@api_bp.route('/analysis')
def analysis():
    # ...
    return render_template('Portfolio Analysis.html')

@api_bp.route('/report')
def report():
    # ...
    return render_template('recommendation.html')

@api_bp.route('/historical/<user_id>')
def historical_data(user_id):
    # ...
    return render_template('historical.html')

@api_bp.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    data = get_time_series_for_stock(symbol)
    return jsonify(data)