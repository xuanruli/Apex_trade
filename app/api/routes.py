from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app.models.user import User
from app.models.transaction import Transaction
from app.models.portfolio import Portfolio
from app.services.auth import verify_exist, authorize_user, oauth_login_google
from app.services.alpha_vantage import get_time_series_for_stock, get_news, get_global_quote, get_overview
from app.services.chart import create_candlestick_chart, create_line_chart, create_bar_chart, convert_dict_to_df
from app.services.news import get_recent_stock_news
from app.services.reports import schedule_report
from plotly.io import to_html
from datetime import datetime
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
        session['id'] = user['id']
        session['username'] = username
        session['name'] = str(user['firstname']) + " " + str(user['lastname'])

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

def load_asset_page():
    symbol = request.args.get('symbol') or session.get('symbol', "AAPL")
    session['symbol'] = symbol

    news = get_news(symbol=symbol)
    global_quote = get_global_quote(symbol=symbol)
    overview = get_overview(symbol=symbol)

    stock = {
        'Name': overview['Name'],
        'Symbol': overview['Symbol'],
        'Exchange': overview['Exchange'],
        'Price': global_quote['05. price'],
        'WeekHigh': overview['52WeekHigh'],
        'WeekLow': overview['52WeekLow'],
        'Sector': overview['Sector'],
        'Industry': overview['Industry'],
        'MarketCap': overview['MarketCapitalization'],
        'PERatio': overview['PERatio'],
        'EPS': overview['EPS'],
        'Dividend': overview['DividendPerShare'],
        'DividendYield': overview['DividendYield']
    }

    titles, urls = [], []
    for i in range(3):
        titles.append(news['feed'][i]['title'])
        urls.append(news['feed'][i]['url'])

    # Get time series data and create charts
    data = get_time_series_for_stock(symbol)
    df = convert_dict_to_df(data)

    default_start = df.index[-1].date().isoformat()
    default_end = df.index[0].date().isoformat()

    start_date = request.args.get('start_date') or session.get('start_date', default_start)
    end_date = request.args.get('end_date') or session.get('end_date', default_end)

    session['start_date'] = start_date
    session['end_date'] = end_date

    if start_date and end_date:
        try:
            df = df[(df.index >= start_date) & (df.index <= end_date)]
        except Exception as e:
            print(f"Error filtering by date: {e}")

    # Create charts and convert them to HTML
    candlestick_chart = to_html(create_candlestick_chart(df, symbol), full_html=False)
    line_chart = to_html(create_line_chart(df, symbol), full_html=False)
    bar_chart = to_html(create_bar_chart(df, symbol), full_html=False)

    print(urls)
    print(titles)

    return stock, candlestick_chart, line_chart, bar_chart, titles, urls, start_date, end_date

@api_bp.route('/asset', methods=['GET'])
def asset():
    if request.method == 'GET':
        stock, candlestick_chart, line_chart, bar_chart, titles, urls, start_date, end_date = load_asset_page()

        return render_template('asset.html',
                stock=stock,
                candlestick_chart=candlestick_chart,
                line_chart=line_chart,
                bar_chart=bar_chart,
                titles=titles,
                urls=urls,
                start_date=start_date,
                end_date=end_date)


@api_bp.route('/trade', methods = ['POST'])
def trade():
    if request.method == 'POST':
        if 'id' not in session:
            flash("Please log in first to start trade", "info")
            return redirect(url_for('api.login'))

        symbol = request.form.get('symbol')
        action_type = request.form.get('actionType')  # 'buy' or 'sell'
        quantity = int(request.form.get('quantity'))
        order_type = request.form.get('orderType')  # 'market', 'limit', or 'stop'
        price = float(request.form.get('price'))
        transaction_date = datetime.now()
        return_page = request.form.get('return_to')

        user_id = session['id']
        Transaction(user_id, symbol, quantity, price, action_type, transaction_date).save()
        portfolio = Portfolio.get_by_user_id(user_id)

        if portfolio.update_portfolio(symbol, quantity, price, action_type.lower()):
            flash(f"Order: {action_type} {quantity} shares of {symbol} with price {price} successful!", 'success')
        else:
            flash(f"Order: {action_type} {quantity} shares of {symbol} with price {price} successful!", 'error')

        if return_page == 'asset':
            return redirect(url_for('api.asset', symbol=symbol))
        else:  # default return is portfolio page
            return redirect(url_for('api.portfolio'))

@api_bp.route('/portfolio')
def portfolio():
    if 'id' not in session:
        flash("Please log in first to get access with portfolio", "info")
        return redirect(url_for('api.login'))

    id = session.get('id')
    if not Portfolio.check_portfolio(id):
        return render_template('portfolio.html', portfolio_summary = [], total_value = [])

    portfolio = Portfolio.get_by_user_id(id)
    portfolio_summary = portfolio.get_portfolio_summary()
    holding_summary = portfolio.get_holding_summary()

    return render_template('portfolio.html', portfolio_summary = portfolio_summary, holding_summary = holding_summary)

@api_bp.route('/news')
def news():
    articles = get_recent_stock_news(count=3)
    return render_template('news.html', articles=articles)

@api_bp.route('/analysis')
def analysis():
    # ...
    return render_template('Portfolio Analysis.html')

@api_bp.route('/historical')
def historical():
    id = session.get('id')
    transactions = Transaction.get_all_transactions(id)
    return render_template('historical.html', transactions = transactions)

@api_bp.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    data = get_time_series_for_stock(symbol)
    return jsonify(data)

@api_bp.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        # Get form values
        email = request.form.get('email')
        report_type = request.form.get('report_type', 'Performance Report')
        frequency = request.form.get('frequency', 'Weekly')  # e.g., Daily, Weekly, etc.
        
        # For the report format, assume checkboxes are named 'pdf', 'excel', and 'csv'
        report_formats = []
        if request.form.get('pdf'):
            report_formats.append('PDF')
        if request.form.get('excel'):
            report_formats.append('Excel')
        if request.form.get('csv'):
            report_formats.append('CSV')
        
        additional_notes = request.form.get('notes', '')
        
        # Call the report service to send the report email
        success = schedule_report(email, report_type, frequency, report_formats, additional_notes)
        
        if success:
            flash("Report scheduled! Check your email for the details.", "report")
        else:
            flash("There was an error scheduling your report. Please try again later.", "report")
        
        # Redirect to portfolio page after submitting
        return redirect(url_for('api.portfolio'))
    
    # GET request: simply render the recommendation page
    return render_template('recommendation.html')

@api_bp.route("/crash")
def crash():
    return 1 / 0

