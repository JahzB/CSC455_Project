"""
CRYPTOGRAPHIC UTILITIES FOR SECURE VOTING (ECC EDITION)
=====================================================

This module handles all encryption and decryption operations for the voting system
using Elliptic Curve Cryptography (ECC) via the ECIES scheme.

KEY FEATURES:
- **Asymmetric Encryption (ECIES):** A Public Key is used to encrypt votes, and a Private Key is used for tallying.
- **Vote Privacy:** Only the central tallying server holds the private key to decrypt the votes.
- **Voter Anonymity:** Uses SHA-256 hashing to create anonymous voter IDs.

SECURITY FEATURES:
- ECC (Curve P-256) for strong, modern asymmetric encryption.
"""

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
import hashlib
import base64
import os
import json

from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, load_pem_public_key 


class VoteCrypto:
    """
    Main encryption class for handling vote security operations using ECIES.
    """
    
    def __init__(self):
        """
        Initialize the crypto system with secure ECC keys.
        CRITICAL FIX: Store the public key in the stable PEM format.
        """
        # 1. Generate the ECC Private Key (The Secret)
        self.private_key = ec.generate_private_key(
            ec.SECP256R1()
        )
        
        # 2. Derive the Public Key Object and immediately serialize it to stable PEM bytes
        public_key_obj = self.private_key.public_key()
        self._public_key_pem = public_key_obj.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        )
        
        print("🔐 Encryption system initialized with ECC (P-256) for ECIES.")

    def encrypt_vote(self, vote_data: str) -> str:
        """Encrypt vote data using the Public Key (ECIES simulation)."""
        try:
            # 1. Ephemeral Key Generation 
            ephemeral_private_key = ec.generate_private_key(ec.SECP256R1())
            
            # 2. Load the public key from the stable PEM string
            tally_public_key = load_pem_public_key(self._public_key_pem, backend=default_backend())
            
            # 3. Shared Secret (ECDH: Exchange)
            shared_secret = ephemeral_private_key.exchange(ec.ECDH(), tally_public_key)

            # 4. Key Derivation (HKDF)
            symmetric_key = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b'ECC Vote Encryption'
            ).derive(shared_secret)

            # 5. AES-GCM Encryption
            aesgcm = AESGCM(symmetric_key)
            nonce = os.urandom(12)
            ciphertext = aesgcm.encrypt(nonce, vote_data.encode('utf-8'), None)

            # 6. Package components
            # NOTE: We package the ephemeral key as PEM for guaranteed loading reliability on the decrypt side
            eph_public_key_pem = ephemeral_private_key.public_key().public_bytes(
                encoding=Encoding.PEM,
                format=PublicFormat.SubjectPublicKeyInfo
            )

            package = {
                'ct': base64.b64encode(ciphertext).decode('utf-8'),
                'n': base64.b64encode(nonce).decode('utf-8'),
                'eph_pub_pem': base64.b64encode(eph_public_key_pem).decode('utf-8')
            }
            return json.dumps(package)
            
        except Exception as e:
            # Log the internal error for better diagnostics
            print(f"❌ Encryption internal error (Key Exchange failure): {e}") 
            raise Exception("Failed to encrypt vote data")
    
    def decrypt_vote(self, encrypted_data: str) -> str:
        """Decrypt vote data using the Private Key (Tallying Authority)."""
        try:
            package = json.loads(encrypted_data)
            ciphertext = base64.b64decode(package['ct'])
            nonce = base64.b64decode(package['n'])
            
            # Recreate ephemeral public key object from received PEM bytes
            eph_public_key_pem = base64.b64decode(package['eph_pub_pem'])
            ephemeral_public_key = load_pem_public_key(eph_public_key_pem, backend=default_backend())

            # 1. Shared Secret (ECDH)
            shared_secret = self.private_key.exchange(ec.ECDH(), ephemeral_public_key)

            # 2. Key Derivation (HKDF)
            symmetric_key = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b'ECC Vote Encryption'
            ).derive(shared_secret)

            # 3. AES-GCM Decryption
            aesgcm = AESGCM(symmetric_key)
            decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
            
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            raise Exception("Failed to decrypt vote data (Possible tampering or key mismatch)")
    
    def create_voter_hash(self, voter_info: str) -> str:
        """Create an anonymous hash for voter identification."""
        salt = "voting_anonymity_salt_2024"
        salted_info = voter_info + salt
        hash_object = hashlib.sha256(salted_info.encode('utf-8'))
        return hash_object.hexdigest()[:16]