from app.models.user import User
from app.logger import logger
import os
import requests
from flask import redirect, url_for, flash, session, request
from urllib.parse import urlencode
from dotenv import load_dotenv
from flask import Blueprint

load_dotenv()

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

auth_bp = Blueprint('auth', __name__)

# This is for general database login
def authorize_user(username, password):
    """
    This is verification for log in
    1. Refuse Oauth user to log in
    2. Check If username not exist
    3. Check if password match with current password
    """
    user_info = User.get_by_username(username)
    if user_info and user_info['password_hash'] == "OAuth":
        return False
    if not user_info or not User.check_password(username, password):
        return False
    logger.info(f"[AUTH] - verified user log in: {username}")
    return True

def verify_exist(username, email):
    """
    This is verification for signing up process
    1. check username or email if already exist
    """
    if User.get_by_username(username) or User.get_by_email(email):
        logger.info(f"[AUTH] - verified user sign up: {username}")
        return True
    return False


# Below is for google login
def oauth_login_google():
    """Redirect to Google login route"""
    return redirect(url_for("auth.google_login"))

def get_google_provider_cfg():
    """Get Google's OAuth 2.0 endpoint configuration"""
    try:
        return requests.get(GOOGLE_DISCOVERY_URL).json()
    except Exception as e:
        logger.error(f"Failed to fetch Google provider config: {e}")
        return None

@auth_bp.route("/login/google")
def google_login():
    """Initiate Google login"""
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    if not google_provider_cfg:
        return "Error fetching Google configuration", 500

    # Get the authorization endpoint
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': f'{request.base_url}/callback',
        'response_type': 'code',
        'scope': 'https://www.googleapis.com/auth/userinfo.email openid https://www.googleapis.com/auth/userinfo.profile'
    }
    request_uri = f"{authorization_endpoint}?{urlencode(params)}"

    # Redirect to Google's OAuth page
    return redirect(request_uri)

@auth_bp.route("/login/google/callback")
def google_callback():
    """Handle Google OAuth callback"""
    code = request.args.get("code")
    if not code:
        flash("Authentication failed", "error")
        return redirect(url_for("api.login"))

    google_provider_cfg = get_google_provider_cfg()
    if not google_provider_cfg:
        return "Error fetching Google configuration", 500

    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request for tokens
    token_url, headers, data = (
        token_endpoint,
        {"Content-Type": "application/x-www-form-urlencoded"},
        {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": request.base_url,
            "grant_type": "authorization_code",
        },
    )

    try:
        # Exchange code for token
        token_response = requests.post(
            token_url,
            headers=headers,
            data=data,
            timeout=10,
        )
        token_response.raise_for_status()
        tokens = token_response.json()
    except Exception as e:
        logger.error(f"[AUTH] - Error getting tokens: {e}")
        flash("Authentication failed", "error")
        return redirect(url_for("api.login"))

    try:
        # Get user info endpoint
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]

        # Get user info
        userinfo_response = requests.get(
            userinfo_endpoint,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            timeout=10,
        )
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()

        if not user_info.get("email_verified", False):
            flash("Email not verified with Google", "error")
            return redirect(url_for("api.login"))

        email = user_info["email"]

        # Check if user exists
        existing_user = User.get_by_email(email)

        if existing_user:
            user_id = existing_user["id"]
            logger.info(f"[AUTH] - verified user logged in: {email}")
        else:
            # Create new user
            username = email.split("@")[0]
            firstname = user_info.get("given_name", "")
            lastname = user_info.get("family_name", "")

            User(username, email, firstname, lastname).save()
            logger.info(f"[AUTH] - Created new user: {username}")

            new_user = User.get_by_username(username)
            user_id = new_user["id"]

        # Set session
        session['id'] = user_id
        session['username'] = user_info["email"].split("@")[0]
        session['name'] = user_info["name"]

        flash("Successfully logged in with Google", "success")
        return redirect(url_for("api.index"))

    except Exception as e:
        logger.error(f"[AUTH] - Error processing Google user: {e}")
        flash("Error processing Google login", "error")
        return redirect(url_for("api.login"))

