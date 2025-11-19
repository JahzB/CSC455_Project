"""
SECURE VOTING SYSTEM SIMULATION - MAIN APPLICATION
==================================================

This is the main Flask application file that serves as the central hub for the secure voting system.

HOW THIS PAGE WORKS:
- Acts as the web server backend using Flask framework
- Handles routing between different pages (login, registration, voting, results)
- Manages session security and user authentication
- Coordinates with the encryption module for secure vote handling
- Stores encrypted votes and manages vote tallying

CONNECTIONS TO OTHER PAGES:
- Routes to Login.py for user authentication
- Routes to register.html for new user registration  
- Routes to vote.html for the actual voting interface
- Routes to results.html for displaying vote tallies
- Connects to crypto_utils.py for encryption/decryption operations
- Uses templates in /templates/ folder for HTML pages

SECURITY FEATURES:
- Session management with secure cookies
- Password hashing with bcrypt
- Vote encryption before storage
- Anonymous vote tallying
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import bcrypt
import json
import os
from datetime import datetime
from crypto_utils import VoteCrypto  # Custom encryption module for votes

# Initialize Flask application with American flag theme
app = Flask(__name__)
app.secret_key = 'voting_democracy_2024_secure_key_usa'  # Secret key for session management

# Initialize vote encryption system
vote_crypto = VoteCrypto()

# In-memory storage for demo (in production, use a proper database)
# Structure: {'username': {'password_hash': hash, 'has_voted': boolean, 'voter_id': id}}
users_db = {}

# Encrypted votes storage - each vote is encrypted before storage
# Structure: [{'encrypted_vote': encrypted_data, 'timestamp': time, 'voter_hash': anonymous_id}]
encrypted_votes = []

# Voting options - can be modified for different elections
VOTING_OPTIONS = [
    "Candidate A - Democratic Party",
    "Candidate B - Republican Party", 
    "Candidate C - Independent",
    "Abstain"
]

# Constitutional quote about voting rights
VOTING_QUOTE = "The right of citizens of the United States to vote shall not be denied or abridged by the United States or by any State on account of race, color, or previous condition of servitude. - 15th Amendment"


@app.route('/')
def home():
    """
    HOME PAGE ROUTE
    - Landing page that welcomes users to the voting system
    - Displays patriotic theme with American flag
    - Provides navigation to login or register
    - Shows voting quote and system information
    """
    return render_template('home.html', quote=VOTING_QUOTE)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    LOGIN PAGE ROUTE
    - Handles user authentication
    - GET: displays login form
    - POST: processes login credentials and creates secure session
    - Redirects authenticated users to voting page
    - Uses bcrypt for secure password verification
    """
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']
        
        # Check if user exists and password is correct
        if username in users_db:
            stored_hash = users_db[username]['password_hash']
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                # Create secure session
                session['username'] = username
                session['logged_in'] = True
                flash('Login successful! Welcome to the secure voting system.', 'success')
                return redirect(url_for('vote'))
            else:
                flash('Invalid password. Please try again.', 'error')
        else:
            flash('Username not found. Please register first.', 'error')
    
    return render_template('login.html', quote=VOTING_QUOTE)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    REGISTRATION PAGE ROUTE  
    - Handles new user registration
    - GET: displays registration form
    - POST: creates new user account with encrypted password
    - Validates username uniqueness
    - Uses bcrypt for secure password hashing
    """
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validate input
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
        elif password != confirm_password:
            flash('Passwords do not match.', 'error')
        elif username in users_db:
            flash('Username already exists. Please choose another.', 'error')
        else:
            # Hash password securely
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Store user data
            users_db[username] = {
                'password_hash': password_hash,
                'has_voted': False,
                'voter_id': len(users_db) + 1,
                'registration_date': datetime.now().isoformat()
            }
            
            flash('Registration successful! Please login to continue.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html', quote=VOTING_QUOTE)


@app.route('/vote', methods=['GET', 'POST'])
def vote():
    """
    VOTING PAGE ROUTE
    - Main voting interface for authenticated users
    - GET: displays voting form with candidates
    - POST: processes encrypted vote submission
    - Prevents double voting by the same user
    - Encrypts votes before storage for anonymity
    """
    # Check if user is logged in
    if 'logged_in' not in session:
        flash('Please login to access the voting system.', 'error')
        return redirect(url_for('login'))
    
    username = session['username']
    
    # Check if user has already voted
    if users_db[username]['has_voted']:
        flash('You have already cast your vote. Thank you for participating!', 'info')
        return redirect(url_for('results'))
    
    if request.method == 'POST':
        selected_candidate = request.form['candidate']
        
        if selected_candidate in VOTING_OPTIONS:
            # Create vote data
            vote_data = {
                'candidate': selected_candidate,
                'timestamp': datetime.now().isoformat()
            }
            
            # Encrypt the vote for anonymity
            encrypted_vote = vote_crypto.encrypt_vote(json.dumps(vote_data))
            
            # Create anonymous voter hash (not tied to username)
            voter_hash = vote_crypto.create_voter_hash(username + str(datetime.now()))
            
            # Store encrypted vote
            encrypted_votes.append({
                'encrypted_vote': encrypted_vote,
                'voter_hash': voter_hash,
                'submission_time': datetime.now().isoformat()
            })
            
            # Mark user as having voted
            users_db[username]['has_voted'] = True
            
            flash('Your vote has been securely recorded! Thank you for voting.', 'success')
            return redirect(url_for('results'))
        else:
            flash('Invalid candidate selection.', 'error')
    
    return render_template('vote.html', 
                         candidates=VOTING_OPTIONS, 
                         quote=VOTING_QUOTE,
                         username=username)


@app.route('/results')
def results():
    """
    RESULTS PAGE ROUTE
    - Displays vote tallies without revealing individual votes
    - Decrypts and counts votes anonymously
    - Shows real-time voting statistics
    - Accessible to all authenticated users
    - Maintains voter anonymity while showing aggregated results
    """
    # Check if user is logged in
    if 'logged_in' not in session:
        flash('Please login to view results.', 'error')
        return redirect(url_for('login'))
    
    # Decrypt and tally votes
    vote_counts = {candidate: 0 for candidate in VOTING_OPTIONS}
    total_votes = 0
    
    for encrypted_vote_entry in encrypted_votes:
        try:
            # Decrypt vote
            decrypted_data = vote_crypto.decrypt_vote(encrypted_vote_entry['encrypted_vote'])
            vote_data = json.loads(decrypted_data)
            
            # Count the vote
            candidate = vote_data['candidate']
            if candidate in vote_counts:
                vote_counts[candidate] += 1
                total_votes += 1
        except Exception as e:
            print(f"Error processing vote: {e}")
            continue
    
    # Calculate percentages
    vote_percentages = {}
    if total_votes > 0:
        for candidate, count in vote_counts.items():
            vote_percentages[candidate] = round((count / total_votes) * 100, 1)
    else:
        vote_percentages = {candidate: 0 for candidate in VOTING_OPTIONS}
    
    return render_template('results.html',
                         vote_counts=vote_counts,
                         vote_percentages=vote_percentages,
                         total_votes=total_votes,
                         quote=VOTING_QUOTE)


@app.route('/logout')
def logout():
    """
    LOGOUT ROUTE
    - Clears user session securely
    - Redirects to home page
    - Displays logout confirmation message
    """
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))


@app.route('/admin')
def admin():
    """
    ADMIN DASHBOARD (Optional)
    - Shows system statistics for administrators
    - Displays number of registered users and votes cast
    - Does not reveal individual vote details
    - Useful for monitoring system health
    """
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # Calculate participation percentages
    total_users = len(users_db)
    users_voted = sum(1 for user in users_db.values() if user['has_voted'])
    votes_cast = len(encrypted_votes)
    
    # Calculate percentages safely
    turnout_rate = (users_voted / total_users * 100) if total_users > 0 else 0
    voted_percentage = (users_voted / total_users * 100) if total_users > 0 else 0
    not_voted_percentage = ((total_users - users_voted) / total_users * 100) if total_users > 0 else 100
    
    stats = {
        'total_users': total_users,
        'votes_cast': votes_cast,
        'users_voted': users_voted,
        'turnout_rate': round(turnout_rate, 1),
        'voted_percentage': round(voted_percentage, 1),
        'not_voted_percentage': round(not_voted_percentage, 1)
    }
    
    return render_template('admin.html', stats=stats, quote=VOTING_QUOTE)


if __name__ == '__main__':
    """
    APPLICATION ENTRY POINT
    - Runs the Flask development server
    - Debug mode enabled for development
    - Server accessible on localhost:5000
    """
    print("🇺🇸 Starting Secure Voting System...")
    print("🔐 Encryption system initialized")
    print("🗳️  Ready to accept votes!")
    app.run(debug=True, host='127.0.0.1', port=5000)
