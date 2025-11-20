"""
BLOCKCHAIN LEDGER FOR SECURE VOTING
===================================

This module implements the custom blockchain structure used to store encrypted votes immutably.
It includes classes for the individual Block and the managing Blockchain structure.

KEY FEATURES:
- **Block Chaining:** Uses SHA-256 to link blocks via cryptographic hashes.
- **Proof-of-Vote (PoV):** Simulates mining difficulty to secure each block.
- **Immutability:** Once a block is added, its contents and hash cannot be changed without invalidating the chain.
"""

import hashlib
import json
from time import time
from typing import Dict, List, Any

# Define the difficulty target for the Proof-of-Vote simulation (4 leading zeros)
DIFFICULTY_TARGET = "0000"

class Blockchain:
    """
    Manages the chain, transactions (encrypted votes), and consensus mechanisms.
    """

    def __init__(self):
        self.chain: List[Dict[str, Any]] = []
        self.current_transactions: List[Dict[str, Any]] = []

        # Create the Genesis block (the very first block in the chain)
        self.new_block(proof=100, previous_hash='1')
        print("⛓️ Genesis Block created.")

    @property
    def last_block(self) -> Dict[str, Any]:
        """Returns the last block in the chain."""
        return self.chain[-1]

    @staticmethod
    def hash(block: Dict[str, Any]) -> str:
        """
        Creates a SHA-256 hash of a Block.
        
        Note: We must ensure the Dictionary is Ordered, or we'll have inconsistent hashes.
        We sort the dictionary keys before dumping to JSON.
        """
        # We ensure the dictionary is sorted by key for consistent hashing
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def new_block(self, proof: int, previous_hash: str | None = None) -> Dict[str, Any]:
        """
        Creates a new Block and adds it to the chain.
        
        Args:
            proof (int): The Proof-of-Vote calculated by the mining algorithm.
            previous_hash (str): Hash of the previous Block.
            
        Returns:
            Dict: The newly created Block.
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'votes': self.current_transactions, # The list of encrypted votes
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions (votes)
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_vote_transaction(self, encrypted_vote: str, voter_hash: str) -> int:
        """
        Adds a new encrypted vote (transaction) to the list of pending votes.
        
        Args:
            encrypted_vote (str): The ECC encrypted vote data.
            voter_hash (str): The anonymous hash of the voter.
            
        Returns:
            int: The index of the Block that the vote will be added to.
        """
        self.current_transactions.append({
            'encrypted_vote': encrypted_vote,
            'voter_hash': voter_hash,
            'submission_time': time(),
        })

        # Return the index of the block this vote will be included in
        return self.last_block['index'] + 1

    def proof_of_vote(self, last_proof: int) -> int:
        """
        Simplified Proof-of-Vote algorithm simulation (finding a hash starting with DIFFICULTY_TARGET).
        
        This loop is computationally intensive and simulates the 'mining' process.
        
        Args:
            last_proof (int): The proof from the previous block.
            
        Returns:
            int: The calculated proof that satisfies the difficulty target.
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        """
        Validates the proof against the difficulty target.
        
        Args:
            last_proof (int): The proof from the previous block.
            proof (int): The current proof candidate being tested.
            
        Returns:
            bool: True if the hash starts with the required DIFFICULTY_TARGET.
        """
        # Combine the two proofs (e.g., "12345" + "1")
        guess = f'{last_proof}{proof}'.encode()
        
        # Hash the combination using SHA-256
        guess_hash = hashlib.sha256(guess).hexdigest()
        
        # Check the difficulty target (e.g., 4 leading zeros)
        return guess_hash[:len(DIFFICULTY_TARGET)] == DIFFICULTY_TARGET

    def is_chain_valid(self, chain: List[Dict[str, Any]]) -> bool:
        """
        Determines if a given blockchain is valid by checking hashes and proofs.
        
        Args:
            chain (List): The blockchain to validate.
            
        Returns:
            bool: True if the chain is valid, False otherwise.
        """
        current_index = 1
        
        while current_index < len(chain):
            block = chain[current_index]
            last_block = chain[current_index - 1]
            
            # 1. Check that the hash of the previous block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # 2. Check that the Proof-of-Vote is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            current_index += 1
            
        return True