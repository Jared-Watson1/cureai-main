from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session
from jared_bot import jared_bot, getArticlesInfo
from dotenv import load_dotenv
from database import get_user_info, add_payment_info, add_user_basic_info
from encryption import decrypt
import os
import stripe
import re
import json

load_dotenv()


def is_valid_email(email):
    email_pattern = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
    return bool(email_pattern.match(email))


def is_unique_username(username):
    return username not in users


def is_valid_password(password):
    return len(password) >= 10


app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.getenv("FLASK_SECRET_KEY")
with open("temp_users.json", 'r') as f:
    users = json.load(f)

# Replace with your Stripe Secret key
stripe.api_key = os.getenv("STRIPE_API_KEY")


@app.route("/plan", methods=["GET", "POST"])
def select_plan():
    # stripe_api_key = os.getenv("STRIPE_API_KEY")

    if request.method == "POST":
        # Your existing POST handling code
        pass

    return render_template("payment.html")


@app.route('/contactus')
def contactus():
    return render_template('contactus.html')


@app.route("/setup-payment", methods=["GET", "POST"])
def payment():
    stripe_api_key = os.getenv("STRIPE_API_KEY") # use publishable api key to handle server side to collect payment information

    if request.method == "POST":
        # Your existing POST handling code
        pass

    return render_template("setuppayment.html", stripe_api_key=stripe_api_key)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = get_user_info(username)

        if user:
            if user['password'] == password:
                session['username'] = username
                session['signed_in'] = True
                return redirect(url_for('index'))
            else:
                flash('Incorrect password. Please try again.')
        else:
            flash('Username does not exist. Please try again or sign up.')

    return render_template('signin.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if not is_valid_email(email):
            flash("Please enter a valid email address.")
        elif not is_unique_username(username):
            flash("Username is already taken. Please choose a different one.")
        elif not is_valid_password(password):
            flash("Password must be at least 10 characters long.")
        else:
            # Register the new user
            add_user_basic_info(username, email, password)
            session['signed_in'] = True
            return redirect(url_for('index'))

    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('signin'))


@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('signed_in', False):
        flash('You must be signed in to access this page.')
        return redirect(url_for('signin'))

    if request.method == 'POST':
        question = request.form.get('question').strip()
        answer, pmids = get_ai_answer(question)
        titles = getArticlesInfo(pmids)
        pmid_title_pairs = zip(pmids, titles)
        return render_template('index.html', question=question, answer=answer, pmid_title_pairs=pmid_title_pairs)
    return render_template('index.html')


def get_ai_answer(question):
    # Replace this function with your actual AI function or API call
    response, pubmed_ids = jared_bot(question)

    # Create the PubMed links
    pubmed_links = [
        f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}" for pubmed_id in pubmed_ids]

    return response, pubmed_links


@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('assets', filename)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
