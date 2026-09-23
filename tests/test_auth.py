import unittest
from database import hash_password_pbkdf2, verify_password

class TestAuthenticationSecurity(unittest.TestCase):
    
    def test_pbkdf2_hashing(self):
        """Test that PBKDF2 generates a unique salted hash every time."""
        password = "secure_patient_password"
        hash1 = hash_password_pbkdf2(password)
        hash2 = hash_password_pbkdf2(password)
        
        # Hashes should be different due to the os.urandom salt
        self.assertNotEqual(hash1, hash2)
        # But both should verify successfully
        self.assertTrue(verify_password(hash1, password))
        self.assertTrue(verify_password(hash2, password))
        
    def test_invalid_password(self):
        """Test that incorrect passwords are rejected."""
        password = "my_password"
        hashed = hash_password_pbkdf2(password)
        self.assertFalse(verify_password(hashed, "wrong_password"))
        
    def test_legacy_hash_fallback(self):
        """Test that legacy unsalted SHA256 hashes still verify properly."""
        import hashlib
        legacy_pass = "old_password"
        legacy_hash = hashlib.sha256(legacy_pass.encode()).hexdigest()
        self.assertTrue(verify_password(legacy_hash, legacy_pass))

if __name__ == '__main__':
    unittest.main()