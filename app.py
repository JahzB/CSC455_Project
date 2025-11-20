"""
SECURE VOTING SYSTEM SIMULATION - MAIN APPLICATION (ECC + BLOCKCHAIN EDITION)
============================================================================

This is the main Flask application file, upgraded to use:
1. ECC (ECIES) for vote encryption.
2. A custom Blockchain ledger for immutable storage.
3. In-memory storage for user authentication status (replicates original design).

SECURITY FEATURES:
- **ECC/ECIES:** Asymmetric encryption provides strong confidentiality.
- **Blockchain:** Immutability and verifiability via SHA-256 chaining.
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
import bcrypt
import json
import os
import hashlib
from datetime import datetime
from time import time

from crypto_utils import VoteCrypto     # ECC Encryption
from Login import LoginManager          # Login security utilities
from blockchain_ledger import Blockchain # Immutable Ledger

# --- CONFIGURATION ---
app = Flask(__name__)
app.secret_key = 'voting_democracy_2024_secure_key_usa'


@app.template_filter('hash')
def hash_filter(data, algorithm='sha256'):
    """Custom filter to hash data for display purposes"""
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    data_str = str(data).encode('utf-8')
    if algorithm == 'sha256':
        return hashlib.sha256(data_str).hexdigest()
    return data_str.hex()

vote_crypto = VoteCrypto()
blockchain = Blockchain() # Initialize the Blockchain Ledger
login_manager = type('LoginManager', (object,), {'validate_password_strength': lambda self, p: (True, "")})() # Mock instantiation for utility access

# In-memory storage for demo
# NOTE: User data is NOT persistent across server restarts.
users_db = {} 

# Voting options
VOTING_OPTIONS = [
    "Candidate A - Democratic Party",
    "Candidate B - Republican Party", 
    "Candidate C - Independent",
    "Abstain"
]

VOTING_QUOTE = "The right of citizens of the United States to vote shall not be denied or abridged by the United States or by any State on account of race, color, or previous condition of servitude. - 15th Amendment"


# FLASK ROUTES 

@app.route('/')
def home():
    """HOME PAGE ROUTE"""
    return render_template('home.html', quote=VOTING_QUOTE)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """LOGIN PAGE ROUTE - Checks user credentials against in-memory database."""
    from Login import LoginManager
    login_manager = LoginManager()

    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']
        
        if username in users_db:
            stored_hash = users_db[username]['password_hash']
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
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
    """REGISTRATION PAGE ROUTE - Stores new user account in-memory."""
    from Login import LoginManager
    login_manager = LoginManager()

    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if username in users_db:
            flash('Username already exists. Please choose another.', 'error')
            return redirect(url_for('register'))
        
        is_valid_strength, strength_message = login_manager.validate_password_strength(password)
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
        elif password != confirm_password:
            flash('Passwords do not match.', 'error')
        elif not is_valid_strength:
            flash(f'Password is too weak: {strength_message}', 'error')
        else:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            users_db[username] = {
                'password_hash': password_hash,
                'has_voted': False,
                'registration_date': datetime.now().isoformat()
            }
            
            flash('Registration successful! Please login to continue.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html', quote=VOTING_QUOTE)


@app.route('/vote', methods=['GET', 'POST'])
def vote():
    """VOTING PAGE ROUTE - Records vote as a transaction and mines a new block."""
    if 'logged_in' not in session:
        flash('Please login to access the voting system.', 'error')
        return redirect(url_for('login'))
    
    username = session['username']
    
    if users_db.get(username, {}).get('has_voted', False):
        flash('You have already cast your vote. Thank yourself for participating!', 'info')
        return redirect(url_for('results'))
    
    if request.method == 'POST':
        
        selected_candidate = request.form.get('candidate')
        
        if not selected_candidate:
      
            flash('Error: Please select a candidate before submitting your vote.', 'error')
            return redirect(url_for('vote'))

        if selected_candidate in VOTING_OPTIONS:
            # 1. Create and Encrypt Vote Data (using ECC)
            vote_data_dict = {'candidate': selected_candidate, 'timestamp': datetime.now().isoformat()}
            encrypted_vote = vote_crypto.encrypt_vote(json.dumps(vote_data_dict))
            voter_hash = vote_crypto.create_voter_hash(username + str(time()))
            
            # 2. Add Transaction (Encrypted Vote) to the Block
            blockchain.new_vote_transaction(encrypted_vote, voter_hash)
            
            # 3. Mine the Block (Proof-of-Vote Simulation)
            last_block = blockchain.last_block
            last_proof = last_block['proof']
            
            # The mining step is CPU intensive for demonstration
            proof = blockchain.proof_of_vote(last_proof)

            # 4. Create the New Block and Add to the Chain
            previous_hash = blockchain.hash(last_block)
            block = blockchain.new_block(proof, previous_hash)
            
            # 5. Mark user as having voted (in-memory)
            users_db[username]['has_voted'] = True
            
            flash(f'Your vote was recorded in Block #{block["index"]} and secured by Proof-of-Vote.', 'success')
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
    RESULTS PAGE ROUTE - Traverses the Blockchain, validates blocks, and tallies votes.
    """
    if 'logged_in' not in session:
        flash('Please login to view results.', 'error')
        return redirect(url_for('login'))
    
    # Check chain integrity first
    if not blockchain.is_chain_valid(blockchain.chain):
        flash('🚨 WARNING: The blockchain ledger integrity has been compromised! Results may be inaccurate.', 'error')
    
    # Decrypt and tally votes by traversing the immutable chain
    vote_counts = {candidate: 0 for candidate in VOTING_OPTIONS}
    total_votes = 0
    
    # Start at index 1 to skip the genesis block
    for block in blockchain.chain[1:]:
        for encrypted_vote_entry in block['votes']:
            try:
                encrypted_data = encrypted_vote_entry.get('encrypted_vote')
                if not encrypted_data: continue

                # Decrypt vote (using ECC Private Key)
                decrypted_data = vote_crypto.decrypt_vote(encrypted_data)
                vote_data = json.loads(decrypted_data)
                
                # Count the vote
                candidate = vote_data.get('candidate')
                if candidate in vote_counts:
                    vote_counts[candidate] += 1
                    total_votes += 1
            except Exception as e:
                # Votes that cannot be decrypted are skipped (treated as invalid/corrupted/tampered)
                print(f"Error processing vote from block {block['index']}: {e}")
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
                         total_users=len(users_db),
                         quote=VOTING_QUOTE)


@app.route('/logout')
def logout():
    """LOGOUT ROUTE"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))


@app.route('/admin')
def admin():
    """ADMIN DASHBOARD - Retrieves user and vote counts from in-memory/Blockchain."""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    total_users = len(users_db)
    users_voted = sum(1 for user in users_db.values() if user['has_voted'])
    # Votes cast is the total number of transactions in the blockchain (excluding genesis)
    votes_cast = sum(len(block['votes']) for block in blockchain.chain[1:])
    
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
        'not_voted_percentage': round(not_voted_percentage, 1),
        'chain_length': len(blockchain.chain)
    }
    
    # Calculate hashes for each block without modifying the original blocks
    block_hashes = []
    for block in blockchain.chain:
        block_hashes.append(blockchain.hash(block))
    
    # Pass blockchain data for admin view
    chain_data = {
        'chain': blockchain.chain,
        'block_hashes': block_hashes,
        'length': len(blockchain.chain),
        'is_valid': blockchain.is_chain_valid(blockchain.chain)
    }
    
    return render_template('admin.html', stats=stats, chain=chain_data, quote=VOTING_QUOTE)


@app.route('/chain_view')
def chain_view():
    """
    BLOCKCHAIN VIEW ROUTE
    - Displays the raw, immutable ledger for verification purposes.
    """
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # Calculate hashes for each block without modifying the original blocks
    block_hashes = []
    for block in blockchain.chain:
        block_hashes.append(blockchain.hash(block))
    
    response = {
        'chain': blockchain.chain,
        'block_hashes': block_hashes,
        'length': len(blockchain.chain),
        'is_valid': blockchain.is_chain_valid(blockchain.chain)
    }
    
    return render_template('chain_view.html', 
                           chain=response['chain'],
                           block_hashes=response['block_hashes'],
                           length=response['length'],
                           is_valid=response['is_valid'],
                           quote=VOTING_QUOTE)


if __name__ == '__main__':
    """APPLICATION ENTRY POINT"""
    print("🇺🇸 Starting Hybrid ECC + Blockchain Voting System...")
    print("🔐 ECC Encryption system initialized")
    print("⛓️  Blockchain Ledger initialized.")
    print("🗳️  Ready to accept votes! User data is IN-MEMORY (lost on restart).")
    app.run(debug=True, host='127.0.0.1', port=5000)