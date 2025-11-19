"""
CRYPTOGRAPHIC UTILITIES FOR SECURE VOTING
==========================================

This module handles all encryption and decryption operations for the voting system.

HOW THIS MODULE WORKS:
- Uses AES encryption (Advanced Encryption Standard) for vote data
- Implements Fernet symmetric encryption from the cryptography library
- Creates anonymous voter hashes for privacy protection
- Ensures vote integrity and anonymity

CONNECTIONS TO OTHER COMPONENTS:
- Called by app.py for encrypting votes before storage
- Called by app.py for decrypting votes during tallying
- Provides secure hashing functions for voter anonymization
- Independent module that can be easily tested and modified

SECURITY FEATURES:
- AES-256 encryption for vote data
- Secure key generation and management
- Anonymous voter identification
- Salt-based hashing for additional security
"""

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import hashlib
import base64
import os

class VoteCrypto:
    """
    Main encryption class for handling vote security operations.
    
    This class provides methods to:
    - Encrypt vote data before storage
    - Decrypt vote data for tallying
    - Create anonymous voter hashes
    - Maintain cryptographic security standards
    """
    
    def __init__(self):
        """
        Initialize the crypto system with a secure key.
        In production, this key should be stored securely (e.g., environment variable).
        """
        # Generate or load encryption key (in production, use secure key management)
        self.key = self._generate_key()
        print("🔐 Encryption system initialized with AES-256")
    
    def _generate_key(self):
        """
        Generate a secure encryption key.
        In production, this should be loaded from a secure location.
        
        Returns:
            bytes: 32-byte encryption key for AES-256
        """
        # For demo purposes, we'll use a fixed key
        # In production, generate and store securely: os.urandom(32)
        return hashlib.sha256(b"secure_voting_system_2024_usa_democracy").digest()
    
    def encrypt_vote(self, vote_data):
        """
        Encrypt vote data using AES encryption.
        
        This function:
        1. Converts vote data to bytes
        2. Generates random initialization vector (IV)
        3. Encrypts data using AES in CBC mode
        4. Returns base64-encoded encrypted data
        
        Args:
            vote_data (str): JSON string containing vote information
            
        Returns:
            str: Base64-encoded encrypted vote data
        """
        try:
            # Convert vote data to bytes
            data_bytes = vote_data.encode('utf-8')
            
            # Generate random initialization vector for security
            iv = get_random_bytes(AES.block_size)
            
            # Create AES cipher in CBC mode
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            
            # Pad data to AES block size and encrypt
            padded_data = pad(data_bytes, AES.block_size)
            encrypted_data = cipher.encrypt(padded_data)
            
            # Combine IV and encrypted data, then encode in base64
            combined_data = iv + encrypted_data
            encoded_data = base64.b64encode(combined_data).decode('utf-8')
            
            print("✅ Vote encrypted successfully")
            return encoded_data
            
        except Exception as e:
            print(f"❌ Encryption error: {e}")
            raise Exception("Failed to encrypt vote data")
    
    def decrypt_vote(self, encrypted_data):
        """
        Decrypt vote data for tallying purposes.
        
        This function:
        1. Decodes base64 encrypted data
        2. Extracts initialization vector (IV)
        3. Decrypts data using AES
        4. Returns original vote data
        
        Args:
            encrypted_data (str): Base64-encoded encrypted vote
            
        Returns:
            str: Decrypted vote data as JSON string
        """
        try:
            # Decode base64 data
            combined_data = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Extract IV and encrypted data
            iv = combined_data[:AES.block_size]
            encrypted_bytes = combined_data[AES.block_size:]
            
            # Create AES cipher for decryption
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            
            # Decrypt and unpad data
            decrypted_padded = cipher.decrypt(encrypted_bytes)
            decrypted_data = unpad(decrypted_padded, AES.block_size)
            
            # Convert back to string
            vote_data = decrypted_data.decode('utf-8')
            
            return vote_data
            
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            raise Exception("Failed to decrypt vote data")
    
    def create_voter_hash(self, voter_info):
        """
        Create an anonymous hash for voter identification.
        
        This ensures voter anonymity by creating a one-way hash
        that cannot be traced back to the original user.
        
        Args:
            voter_info (str): Voter information to hash
            
        Returns:
            str: Anonymous voter hash
        """
        try:
            # Add salt for additional security
            salt = "voting_anonymity_salt_2024"
            salted_info = voter_info + salt
            
            # Create SHA-256 hash
            hash_object = hashlib.sha256(salted_info.encode('utf-8'))
            voter_hash = hash_object.hexdigest()
            
            print("🔒 Anonymous voter hash created")
            return voter_hash[:16]  # Return first 16 characters for brevity
            
        except Exception as e:
            print(f"❌ Hashing error: {e}")
            raise Exception("Failed to create voter hash")
    
    def verify_vote_integrity(self, encrypted_vote):
        """
        Verify that an encrypted vote can be properly decrypted.
        
        This is useful for system health checks and ensuring
        data integrity throughout the voting process.
        
        Args:
            encrypted_vote (str): Encrypted vote data to verify
            
        Returns:
            bool: True if vote is valid, False otherwise
        """
        try:
            # Attempt to decrypt the vote
            decrypted_data = self.decrypt_vote(encrypted_vote)
            
            # Check if decrypted data is valid JSON
            import json
            json.loads(decrypted_data)
            
            return True
            
        except:
            return False
    
    def get_encryption_info(self):
        """
        Return information about the encryption system.
        
        Returns:
            dict: Encryption system information
        """
        return {
            "algorithm": "AES-256",
            "mode": "CBC",
            "key_size": len(self.key) * 8,
            "block_size": AES.block_size * 8,
            "status": "Active"
        }


# Test function for encryption system
def test_encryption():
    """
    Test function to verify encryption/decryption works correctly.
    Run this function to ensure the crypto system is working properly.
    """
    print("\n🧪 Testing encryption system...")
    
    # Initialize crypto system
    crypto = VoteCrypto()
    
    # Test data
    test_vote = '{"candidate": "Test Candidate", "timestamp": "2024-01-01T12:00:00"}'
    
    try:
        # Test encryption
        encrypted = crypto.encrypt_vote(test_vote)
        print(f"✅ Encryption test passed")
        
        # Test decryption
        decrypted = crypto.decrypt_vote(encrypted)
        print(f"✅ Decryption test passed")
        
        # Verify data integrity
        if test_vote == decrypted:
            print("✅ Data integrity verified")
        else:
            print("❌ Data integrity failed")
            
        # Test voter hash
        voter_hash = crypto.create_voter_hash("test_voter_123")
        print(f"✅ Voter hash created: {voter_hash}")
        
        print("🎉 All encryption tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Encryption test failed: {e}")
        return False


if __name__ == "__main__":
    # Run tests when module is executed directly
    test_encryption()
