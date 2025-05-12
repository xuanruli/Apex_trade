from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app.logger import logger
from app.models.user import User
from app.models.transaction import Transaction
from app.models.portfolio import Portfolio
from app.models.asset import Asset
from app.services.auth import verify_exist, authorize_user, oauth_login_google
from app.services.news import get_recent_stock_news
from app.services.chart import load_asset_page
from datetime import datetime
from flask_mail import Message
from weasyprint import HTML
from validate_email import validate_email
import pandas as pd
import numpy as np
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

        # go to admin page if it's an admin
        if username == "apex_admin":
            return redirect(url_for('api.admin'))

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
            return jsonify({"success": False, "message": "Please log in first to start trade"}), 401

        data = request.get_json()

        symbol = data.get('symbol')
        action_type = data.get('actionType')  # 'buy' or 'sell'
        quantity = int(data.get('quantity'))
        order_type = data.get('orderType')  # 'market', 'limit', or 'stop'
        price = float(data.get('price'))
        transaction_date = datetime.now()

        user_id = session['id']
        Transaction(user_id, symbol, quantity, price, action_type, transaction_date).save()
        portfolio = Portfolio.get_by_user_id(user_id)

        if portfolio.update_portfolio(symbol, quantity, price, action_type.lower()):
            flash(f"Order: {action_type} {quantity} shares of {symbol} with price {price} successful!", 'success')
        else:
            flash(f"Order: {action_type} {quantity} shares of {symbol} with price {price} successful!", 'error')


        return jsonify({
            'success': True,
            'message': 'Trade Success!'
        })

@api_bp.route('/portfolio')
def portfolio():
    if 'id' not in session:
        flash("Please log in first to get access with portfolio", "info")
        return redirect(url_for('api.login'))
    if session.get('username') == "apex_admin":
        return redirect(url_for('api.admin'))

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


@api_bp.route('/analysis', methods=['GET'])
def analysis():
    # Get portfolio data

    ef_data = ef_draw()

    # pie chart
    user_id = session['id']
    chart_data = pie_chart(user_id)

    # Pass data to template
    return render_template('analysis.html', data=ef_data, chart_data=chart_data)

def ef_draw():
    portfolio = pd.DataFrame(Portfolio.get_all_portfolios())
    portfolio_symbols = portfolio['stock_symbol'].unique()

    # Get price data - use longer timeframe if possible
    price_df = Asset.get_one_year_price_db(portfolio_symbols)

    # Calculate returns
    returns = price_df.pct_change().dropna()

    # Calculate expected returns and covariance
    expected_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252

    # Set risk-free rate (current 10-year Treasury yield)
    risk_free_rate = 0.0423  # 4.23% based on current Treasury yield

    # Check for any negative expected returns and adjust if necessary
    for symbol in expected_returns.index:
        if expected_returns[symbol] < risk_free_rate:
            # Option 1: Set to risk-free rate plus a small premium
            expected_returns[symbol] = risk_free_rate + 0.01
            # Option 2: Use longer historical data if available

    # Convert to lists for JSON serialization
    ef_data = {
        'symbols': expected_returns.index.tolist(),
        'returns': expected_returns.values.tolist(),
        'covariance': cov_matrix.values.tolist(),
        'risk_free_rate': risk_free_rate
    }
    return ef_data

def pie_chart(user_id):
    portfolio = Portfolio.get_by_user_id(user_id)
    holdings_data = portfolio.get_holding_summary()

    symbols = [item['symbol'] for item in holdings_data]
    market_values = [item['market_value'] for item in holdings_data]

    chart_data = {
        'symbols': symbols,
        'market_values': market_values,
        'holdings': holdings_data
    }
    return chart_data

@api_bp.route('/historical')
def historical():
    id = session.get('id')
    transactions = Transaction.get_all_transactions(id)
    return render_template('historical.html', transactions = transactions)

@api_bp.route('/admin')
def admin():
    if session.get('username') != "apex_admin":
        flash('only admin can access this page', 'error')
        return redirect(url_for('api.index'))
    users = User.get_all_users()
    transactions = Transaction.get_all_user_transactions()
    portfolios = Portfolio.get_all_portfolios()

    return render_template('admin.html', users=users, transactions=transactions, portfolios=portfolios)

@api_bp.route('/admin/change-password', methods = ['POST'])
def change_password():
    if request.method == 'POST':
        data = request.get_json()
        user_id = data.get('user_id')
        new_pass = data.get('new_password')
        User.change_password(user_id, new_pass)

        return jsonify({
            'success': True,
            'message': 'Change Password Success!'
        })

@api_bp.route('/admin/delete', methods = ['POST'])
def delete_user():
    if request.method == 'POST':
        data = request.get_json()
        user_id = data.get('user_id')
        user_name = data.get('username')
        if user_name == 'apex_admin':
            return jsonify({'success': False,'message': 'Admin cannot be deleted'}), 401
        User.delete_user(user_id)

        return jsonify({
            'success': True,
            'message': 'Delete Success!'
        })

@api_bp.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'GET':
        return render_template('report.html')

    if request.method == 'POST':
        from app import mail  # avoid import error conflict

        if not validate_email(request.form['email']):
            flash('Invalid email address, please try again', 'error')
            return redirect(url_for('api.report'))

        ef_data = ef_draw()
        # pie chart
        user_id = session['id']
        chart_data = pie_chart(user_id)

        rendered_html = render_template('analysis.html', pdf_mode=True, base_url=request.url_root.rstrip('/'), data=ef_data, chart_data=chart_data)

        name = session['name']

        base_url = request.url_root
        pdf_file = HTML(string=rendered_html, base_url=base_url).write_pdf()
        msg = Message('Your Apex Trading Portfolio Report',
                      recipients=[request.form['email']])
        msg.body = f"""Dear {name},\n\n\nThank you for using Apex Trading's portfolio analysis services. As requested, please find attached your personalized Portfolio Analysis Report in PDF format.\n\n\nThis report provides a comprehensive overview of your current investment positions, performance metrics, and potential optimization opportunities based on our proprietary market analysis.\n\n\nIf you have any questions regarding this report or would like to schedule a consultation with one of our financial advisors, please don't hesitate to contact our customer support team at ryan29li33@gmail.com.\n\n\nThe Apex Trading Team\nPortfolio Analysis Department"""
        msg.attach('Apex_analysis.pdf', 'application/pdf', pdf_file)

        try:
            mail.send(msg)
            flash('Portfolio Analysis Report Sent Successful', 'success')
        except Exception as e:
            print(str(e))
            flash("Portfolio Analysis Report Sent Unsuccessful", 'error')

        return redirect(url_for('api.portfolio'))


@api_bp.route("/crash")
def crash():
    return 1 / 0

