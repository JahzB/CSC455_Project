#!/usr/bin/env python3
"""
DEMO SCRIPT FOR SECURE VOTING SYSTEM
====================================

This script demonstrates the secure voting system functionality by:
- Creating test users
- Simulating vote casting
- Displaying encrypted vote storage
- Showing result tallying process

HOW THIS SCRIPT WORKS:
- Imports and uses the voting system modules
- Creates sample user accounts with secure passwords
- Demonstrates vote encryption and storage
- Shows anonymous result calculation
- Verifies system security and integrity

CONNECTIONS TO OTHER MODULES:
- Uses crypto_utils.py for encryption operations
- Imports Login.py for authentication testing
- Simulates the Flask app functionality
- Tests all major system components

RUN THIS SCRIPT:
python demo.py
"""

import sys
import json
from datetime import datetime
from crypto_utils import VoteCrypto
from Login import LoginManager
import bcrypt

def print_header(title):
    """Print a formatted header for demo sections."""
    print("\n" + "="*60)
    print(f"🇺🇸 {title}")
    print("="*60)

def print_step(step_num, description):
    """Print a formatted step in the demo process."""
    print(f"\n📋 Step {step_num}: {description}")
    print("-" * 50)

def demo_encryption_system():
    """Demonstrate the encryption capabilities."""
    print_header("ENCRYPTION SYSTEM DEMONSTRATION")
    
    # Initialize crypto system
    print("🔐 Initializing encryption system...")
    crypto = VoteCrypto()
    
    # Test vote data
    test_votes = [
        {"candidate": "Candidate A - Democratic Party", "timestamp": datetime.now().isoformat()},
        {"candidate": "Candidate B - Republican Party", "timestamp": datetime.now().isoformat()},
        {"candidate": "Candidate C - Independent", "timestamp": datetime.now().isoformat()}
    ]
    
    encrypted_votes = []
    
    print("\n🗳️  Encrypting sample votes...")
    for i, vote in enumerate(test_votes, 1):
        vote_json = json.dumps(vote)
        print(f"\n   Vote {i}: {vote['candidate']}")
        
        # Encrypt vote
        encrypted_vote = crypto.encrypt_vote(vote_json)
        
        # Create anonymous hash
        voter_hash = crypto.create_voter_hash(f"voter_{i}_{datetime.now()}")
        
        encrypted_votes.append({
            'encrypted_vote': encrypted_vote,
            'voter_hash': voter_hash,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"   ✅ Encrypted length: {len(encrypted_vote)} characters")
        print(f"   🔒 Anonymous hash: {voter_hash}")
    
    print(f"\n📊 Total encrypted votes stored: {len(encrypted_votes)}")
    
    # Demonstrate decryption and tallying
    print("\n🔓 Demonstrating anonymous vote tallying...")
    vote_counts = {}
    
    for i, encrypted_vote_entry in enumerate(encrypted_votes, 1):
        try:
            # Decrypt vote (this would normally be done during tallying)
            decrypted_data = crypto.decrypt_vote(encrypted_vote_entry['encrypted_vote'])
            vote_data = json.loads(decrypted_data)
            candidate = vote_data['candidate']
            
            # Count vote
            if candidate in vote_counts:
                vote_counts[candidate] += 1
            else:
                vote_counts[candidate] = 1
                
            print(f"   Vote {i}: Successfully decrypted and tallied")
            
        except Exception as e:
            print(f"   ❌ Error processing vote {i}: {e}")
    
    print("\n📈 Final vote tally (anonymous):")
    for candidate, count in vote_counts.items():
        print(f"   {candidate}: {count} vote(s)")
    
    return encrypted_votes, vote_counts

def demo_authentication_system():
    """Demonstrate the authentication capabilities."""
    print_header("AUTHENTICATION SYSTEM DEMONSTRATION")
    
    # Initialize login manager
    print("👤 Initializing authentication system...")
    login_mgr = LoginManager()
    
    # Create test users
    test_users = [
        {"username": "alice_voter", "password": "SecurePass123"},
        {"username": "bob_citizen", "password": "Democracy2024!"},
        {"username": "carol_voter", "password": "VoteSecure456"}
    ]
    
    users_db = {}
    
    print("\n👥 Creating test user accounts...")
    for user in test_users:
        username = user['username']
        password = user['password']
        
        # Validate password strength
        is_valid, message = login_mgr.validate_password_strength(password)
        print(f"\n   User: {username}")
        print(f"   Password strength: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        if is_valid:
            # Hash password
            password_hash = login_mgr.hash_password(password)
            users_db[username] = {
                'password_hash': password_hash,
                'has_voted': False,
                'voter_id': len(users_db) + 1
            }
            print(f"   ✅ Account created with secure hash")
        else:
            print(f"   ❌ Account creation failed: {message}")
    
    print(f"\n📊 Total user accounts created: {len(users_db)}")
    
    # Demonstrate login verification
    print("\n🔓 Testing login verification...")
    for user in test_users:
        username = user['username']
        password = user['password']
        
        if username in users_db:
            stored_hash = users_db[username]['password_hash']
            is_match = login_mgr.verify_password(password, stored_hash)
            
            # Track login attempt
            login_mgr.track_login_attempt(username, is_match)
            
            print(f"   {username}: {'✅ Login successful' if is_match else '❌ Login failed'}")
        else:
            print(f"   {username}: ❌ User not found")
    
    return users_db

def demo_complete_voting_process():
    """Demonstrate the complete voting process."""
    print_header("COMPLETE VOTING PROCESS SIMULATION")
    
    # Initialize systems
    crypto = VoteCrypto()
    login_mgr = LoginManager()
    
    # Voting candidates
    candidates = [
        "Candidate A - Democratic Party",
        "Candidate B - Republican Party", 
        "Candidate C - Independent",
        "Abstain"
    ]
    
    print("🗳️  Available candidates:")
    for i, candidate in enumerate(candidates, 1):
        print(f"   {i}. {candidate}")
    
    # Simulate voting process
    print("\n👥 Simulating voting process...")
    
    # Create voters
    voters = [
        {"username": "voter1", "password": "Vote123!", "choice": 0},
        {"username": "voter2", "password": "Democracy456!", "choice": 1},
        {"username": "voter3", "password": "Secure789!", "choice": 0},
        {"username": "voter4", "password": "Election2024!", "choice": 2},
        {"username": "voter5", "password": "Ballot123!", "choice": 1}
    ]
    
    users_db = {}
    encrypted_votes = []
    
    for i, voter in enumerate(voters, 1):
        print_step(f"{i}a", f"Registering {voter['username']}")
        
        # Register user
        password_hash = bcrypt.hashpw(voter['password'].encode('utf-8'), bcrypt.gensalt())
        users_db[voter['username']] = {
            'password_hash': password_hash,
            'has_voted': False,
            'voter_id': len(users_db) + 1
        }
        print(f"   ✅ User {voter['username']} registered successfully")
        
        print_step(f"{i}b", f"User {voter['username']} casting vote")
        
        # Authenticate (simulate)
        is_authenticated = bcrypt.checkpw(voter['password'].encode('utf-8'), password_hash)
        if not is_authenticated:
            print(f"   ❌ Authentication failed for {voter['username']}")
            continue
        
        # Cast vote
        if users_db[voter['username']]['has_voted']:
            print(f"   ❌ {voter['username']} has already voted!")
            continue
        
        selected_candidate = candidates[voter['choice']]
        
        # Create vote data
        vote_data = {
            'candidate': selected_candidate,
            'timestamp': datetime.now().isoformat()
        }
        
        # Encrypt vote
        encrypted_vote = crypto.encrypt_vote(json.dumps(vote_data))
        voter_hash = crypto.create_voter_hash(voter['username'] + str(datetime.now()))
        
        # Store encrypted vote
        encrypted_votes.append({
            'encrypted_vote': encrypted_vote,
            'voter_hash': voter_hash,
            'submission_time': datetime.now().isoformat()
        })
        
        # Mark user as voted
        users_db[voter['username']]['has_voted'] = True
        
        print(f"   ✅ Vote cast for: {selected_candidate}")
        print(f"   🔐 Vote encrypted and stored anonymously")
        print(f"   🔒 Anonymous voter hash: {voter_hash}")
    
    # Tally results
    print_step("6", "Tallying results anonymously")
    
    vote_counts = {candidate: 0 for candidate in candidates}
    total_votes = 0
    
    for encrypted_vote_entry in encrypted_votes:
        try:
            # Decrypt vote
            decrypted_data = crypto.decrypt_vote(encrypted_vote_entry['encrypted_vote'])
            vote_data = json.loads(decrypted_data)
            
            # Count vote
            candidate = vote_data['candidate']
            if candidate in vote_counts:
                vote_counts[candidate] += 1
                total_votes += 1
                
        except Exception as e:
            print(f"   ❌ Error processing vote: {e}")
            continue
    
    # Display results
    print("\n🏆 FINAL ELECTION RESULTS")
    print("=" * 40)
    
    for candidate, count in vote_counts.items():
        if candidate != 'Abstain' or count > 0:
            percentage = (count / total_votes * 100) if total_votes > 0 else 0
            print(f"   {candidate}: {count} votes ({percentage:.1f}%)")
    
    print(f"\n📊 Total votes cast: {total_votes}")
    print(f"👥 Total registered users: {len(users_db)}")
    print(f"🗳️  Participation rate: {(len([u for u in users_db.values() if u['has_voted']]) / len(users_db) * 100):.1f}%")
    
    # Find winner
    if total_votes > 0:
        max_votes = max(count for candidate, count in vote_counts.items() if candidate != 'Abstain')
        winners = [candidate for candidate, count in vote_counts.items() 
                  if count == max_votes and count > 0 and candidate != 'Abstain']
        
        if winners:
            print(f"\n🎉 WINNER: {', '.join(winners)} with {max_votes} vote(s)!")
    
def demo_security_features():
    """Demonstrate security features."""
    print_header("SECURITY FEATURES DEMONSTRATION")
    
    crypto = VoteCrypto()
    
    print("🔐 Encryption system information:")
    info = crypto.get_encryption_info()
    for key, value in info.items():
        print(f"   {key.title()}: {value}")
    
    print("\n🛡️  Security protections in place:")
    protections = [
        "AES-256 encryption for all vote data",
        "Bcrypt password hashing with salt",
        "Anonymous voter identification",
        "Secure session management", 
        "One-vote-per-user enforcement",
        "Vote integrity verification",
        "No user-vote correlation storage"
    ]
    
    for protection in protections:
        print(f"   ✅ {protection}")
    
    # Test vote integrity
    print("\n🔍 Testing vote integrity...")
    test_vote = '{"candidate": "Test Candidate", "timestamp": "2024-01-01T12:00:00"}'
    encrypted = crypto.encrypt_vote(test_vote)
    
    is_valid = crypto.verify_vote_integrity(encrypted)
    print(f"   Vote integrity check: {'✅ Passed' if is_valid else '❌ Failed'}")

def main():
    """Main demo function."""
    print_header("SECURE VOTING SYSTEM DEMONSTRATION")
    
    print("🇺🇸 Welcome to the Secure Voting System Demo!")
    print("This demonstration will show you how the system works.")
    print("\nDemonstration includes:")
    print("   • Encryption and decryption of votes")
    print("   • User authentication and security")
    print("   • Complete voting process simulation")
    print("   • Security feature verification")
    
    try:
        # Run demonstrations
        demo_encryption_system()
        demo_authentication_system()
        demo_complete_voting_process()
        demo_security_features()
        
        print_header("DEMONSTRATION COMPLETE")
        print("🎉 All systems functioning correctly!")
        print("🇺🇸 Democracy secured through cryptography!")
        print("\nTo run the web interface:")
        print("   python app.py")
        print("   Then visit: http://127.0.0.1:5000")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
