import os
import sys
import unittest
import base64
import shutil
import tempfile

# Ensure the local src directory is in sys.path so we can import 'ntsm'
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from ntsm.aeadencrypt import VaultCipher, VaultUtils

class TestVaultUtils(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_generate_key(self):
        key_path = VaultUtils.generate_key(self.test_dir)
        self.assertTrue(os.path.exists(key_path))
        with open(key_path, "r") as f:
            content = f.read()
            # Should be base64 encoded
            decoded = base64.b64decode(content)
            self.assertEqual(len(decoded), 64)

    def test_generate_pair_key(self):
        priv, pub = VaultUtils.generate_pair_key(self.test_dir)
        self.assertTrue(os.path.exists(priv))
        self.assertTrue(os.path.exists(pub))
        with open(priv, "rb") as f:
            self.assertIn(b"PRIVATE KEY", f.read())
        with open(pub, "rb") as f:
            self.assertIn(b"PUBLIC KEY", f.read())

    def test_legacy_encryption_roundtrip(self):
        plain = "Hello Legacy World"
        secret = "my_legacy_secret"
        encrypted = VaultUtils.encrypt_text(plain, secret)
        decrypted = VaultUtils.decrypt_text(encrypted, secret)
        self.assertEqual(plain, decrypted)

    def test_password_generation(self):
        # This test might skip if password-generator is not installed
        try:
            pwd = VaultUtils.gen_password(10, 15)
            self.assertTrue(10 <= len(pwd) <= 15)
        except ImportError:
            self.skipTest("password-generator not installed")

class TestVaultCipher(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.master_key = os.urandom(32)
        self.master_key_b64 = base64.b64encode(self.master_key).decode("ascii")
        
        self.key_file = os.path.join(self.test_dir, "master.key")
        with open(self.key_file, "w") as f:
            f.write(self.master_key_b64)
            
        os.environ["UNIT_TEST_KEY"] = self.master_key_b64

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        if "UNIT_TEST_KEY" in os.environ:
            del os.environ["UNIT_TEST_KEY"]

    def test_init_from_env(self):
        vault = VaultCipher(key_name="UNIT_TEST_KEY")
        self.assertTrue(vault.verify_master_key())
        self.assertEqual(vault._key_source, "ENV")

    def test_init_from_file(self):
        # Unset env to force file
        if "UNIT_TEST_KEY" in os.environ:
            del os.environ["UNIT_TEST_KEY"]
        vault = VaultCipher(key_name="UNIT_TEST_KEY", key_path=self.key_file)
        self.assertTrue(vault.verify_master_key())
        self.assertEqual(vault._key_source, "FILE")

    def test_text_encryption_roundtrip(self):
        vault = VaultCipher(key_name="UNIT_TEST_KEY")
        plain = "Sensitive Data 123"
        tags = b"owner:adrian"
        
        encrypted = vault.encrypt_text(plain, tags=tags)
        decrypted = vault.decrypt_text(encrypted, tags=tags)
        
        self.assertEqual(plain, decrypted)
        
        # Test failure with wrong tags
        with self.assertRaises(Exception):
            vault.decrypt_text(encrypted, tags=b"owner:someone_else")

    def test_file_encryption_roundtrip(self):
        vault = VaultCipher(key_name="UNIT_TEST_KEY")
        plain_path = os.path.join(self.test_dir, "data.txt")
        enc_path = os.path.join(self.test_dir, "data.enc")
        dec_path = os.path.join(self.test_dir, "data.dec")
        
        content = b"Binary data \x00\xff" * 100
        with open(plain_path, "wb") as f:
            f.write(content)
            
        vault.encrypt_file(plain_path, enc_path, tags=b"file_test")
        vault.decrypt_file(enc_path, dec_path, tags=b"file_test")
        
        with open(dec_path, "rb") as f:
            self.assertEqual(f.read(), content)

    def test_memory_scrubbing(self):
        vault = VaultCipher(key_name="UNIT_TEST_KEY")
        self.assertTrue(vault.verify_master_key())
        vault.scrub()
        self.assertFalse(vault.verify_master_key())
        with self.assertRaises(RuntimeError):
            vault.encrypt_text("test")

    def test_revive(self):
        vault = VaultCipher(key_name="UNIT_TEST_KEY")
        vault.scrub()
        vault.revive()
        self.assertTrue(vault.verify_master_key())

    def test_tampered_data(self):
        vault = VaultCipher(key_name="UNIT_TEST_KEY")
        encrypted = vault.encrypt_text("test")
        # Tamper with the raw data (Base64)
        tampered = encrypted[:-5] + "AAAAA"
        with self.assertRaises(Exception):
            vault.decrypt_text(tampered)

if __name__ == "__main__":
    unittest.main()
