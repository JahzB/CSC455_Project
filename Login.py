"""
LOGIN MODULE FOR SECURE VOTING SYSTEM
=====================================

This file serves as an alternative login handler or can be integrated with the main Flask app.

HOW THIS MODULE WORKS:
- Provides additional login functionality and utilities
- Can be used for command-line login testing
- Offers password validation and user management helpers
- Integrates with the main app.py Flask application

CONNECTIONS TO OTHER COMPONENTS:
- Works alongside app.py for user authentication
- Uses crypto_utils.py for secure password handling
- Can import and extend the main application functionality
- Provides testing utilities for the login system

SECURITY FEATURES:
- Password strength validation
- Account lockout protection (future enhancement)
- Login attempt logging
- Session management helpers
"""

import bcrypt
import getpass
import sys
from datetime import datetime

class LoginManager:
    """
    Additional login management class for enhanced security features.
    
    This class provides:
    - Password strength validation
    - Login attempt tracking
    - Security utilities
    - Command-line interface for testing
    """
    
    def __init__(self):
        """Initialize the login manager with security settings."""
        self.max_login_attempts = 3
        self.login_attempts = {}  # Track failed attempts by username
        print("🔐 Login Manager initialized")
    
    def validate_password_strength(self, password):
        """
        Validate password meets security requirements.
        
        Requirements:
        - At least 6 characters long
        - Contains at least one number
        - Contains at least one uppercase letter
        - Contains at least one lowercase letter
        
        Args:
            password (str): Password to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        return True, "Password meets security requirements"
    
    def hash_password(self, password):
        """
        Create a secure hash of the password using bcrypt.
        
        Args:
            password (str): Plain text password
            
        Returns:
            bytes: Hashed password
        """
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    def verify_password(self, password, hashed_password):
        """
        Verify a password against its hash.
        
        Args:
            password (str): Plain text password
            hashed_password (bytes): Stored password hash
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    
    def track_login_attempt(self, username, success=False):
        """
        Track login attempts for security monitoring.
        
        Args:
            username (str): Username attempting to login
            success (bool): Whether the login was successful
        """
        if username not in self.login_attempts:
            self.login_attempts[username] = {
                'count': 0,
                'last_attempt': None,
                'locked': False
            }
        
        attempt_data = self.login_attempts[username]
        attempt_data['last_attempt'] = datetime.now()
        
        if success:
            # Reset failed attempts on successful login
            attempt_data['count'] = 0
            attempt_data['locked'] = False
            print(f"✅ Successful login for {username}")
        else:
            # Increment failed attempts
            attempt_data['count'] += 1
            print(f"❌ Failed login attempt {attempt_data['count']} for {username}")
            
            # Lock account after max attempts
            if attempt_data['count'] >= self.max_login_attempts:
                attempt_data['locked'] = True
                print(f"🔒 Account {username} has been locked due to too many failed attempts")
    
    def is_account_locked(self, username):
        """
        Check if an account is locked due to failed login attempts.
        
        Args:
            username (str): Username to check
            
        Returns:
            bool: True if account is locked, False otherwise
        """
        if username in self.login_attempts:
            return self.login_attempts[username].get('locked', False)
        return False
    
    def unlock_account(self, username):
        """
        Unlock a previously locked account (admin function).
        
        Args:
            username (str): Username to unlock
        """
        if username in self.login_attempts:
            self.login_attempts[username]['locked'] = False
            self.login_attempts[username]['count'] = 0
            print(f"🔓 Account {username} has been unlocked")


def command_line_login_test():
    """
    Command-line interface for testing login functionality.
    This function allows testing the login system from the terminal.
    """
    print("\n" + "="*50)
    print("🇺🇸 SECURE VOTING SYSTEM - LOGIN TEST")
    print("="*50)
    
    login_mgr = LoginManager()
    
    while True:
        print("\nOptions:")
        print("1. Test password validation")
        print("2. Create password hash")
        print("3. Verify password")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            print("\n--- Password Strength Test ---")
            password = getpass.getpass("Enter password to test: ")
            is_valid, message = login_mgr.validate_password_strength(password)
            print(f"Result: {'✅ Valid' if is_valid else '❌ Invalid'}")
            print(f"Message: {message}")
            
        elif choice == "2":
            print("\n--- Password Hash Creation ---")
            password = getpass.getpass("Enter password to hash: ")
            password_hash = login_mgr.hash_password(password)
            print(f"Hash: {password_hash.decode('utf-8')}")
            
        elif choice == "3":
            print("\n--- Password Verification ---")
            password = getpass.getpass("Enter password: ")
            hash_input = input("Enter hash to verify against: ").encode('utf-8')
            try:
                is_match = login_mgr.verify_password(password, hash_input)
                print(f"Result: {'✅ Match' if is_match else '❌ No match'}")
            except Exception as e:
                print(f"❌ Error: {e}")
                
        elif choice == "4":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")


# Integration function for main Flask app
def integrate_with_flask_app(app):
    """
    Integrate additional login security features with the main Flask app.
    
    Args:
        app: Flask application instance
    """
    login_mgr = LoginManager()
    
    # Add login manager to app context
    app.login_manager = login_mgr
    
    print("🔗 Login manager integrated with Flask app")
    return login_mgr


if __name__ == "__main__":
    """
    Run command-line login testing when file is executed directly.
    """
    command_line_login_test()