import pytest
import os
import sys
import base64
import shutil
import tempfile

# Ensure local src directory is in sys.path so we can import 'ntsm'
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from ntsm.aeadencrypt import VaultCipher, VaultUtils

@pytest.fixture
def test_dir():
    """Fixture to create and cleanup a temporary directory for tests."""
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)

@pytest.fixture
def master_key():
    """Fixture to generate a random 32-byte master key."""
    return os.urandom(32)

@pytest.fixture
def master_key_b64(master_key):
    """Fixture to generate a base64 encoded master key."""
    return base64.b64encode(master_key).decode("ascii")

class TestVaultUtils:
    def test_generate_key(self, test_dir):
        """Test random key generation."""
        key_path = VaultUtils.generate_key(test_dir)
        assert os.path.exists(key_path)
        with open(key_path, "r") as f:
            content = f.read()
            # Should be base64 encoded
            decoded = base64.b64decode(content)
            assert len(decoded) == 64

    def test_generate_pair_key(self, test_dir):
        """Test RSA pair key generation."""
        priv, pub = VaultUtils.generate_pair_key(test_dir)
        assert os.path.exists(priv)
        assert os.path.exists(pub)
        with open(priv, "rb") as f:
            assert b"PRIVATE KEY" in f.read()
        with open(pub, "rb") as f:
            assert b"PUBLIC KEY" in f.read()

    def test_legacy_encryption_roundtrip(self):
        """Test legacy text encryption/decryption."""
        plain = "Hello Legacy World"
        secret = "my_legacy_secret"
        encrypted = VaultUtils.encrypt_text(plain, secret)
        decrypted = VaultUtils.decrypt_text(encrypted, secret)
        assert plain == decrypted

    def test_password_generation(self):
        """Test secure password generation utility."""
        try:
            pwd = VaultUtils.gen_password(10, 15)
            assert 10 <= len(pwd) <= 15
        except ImportError:
            pytest.skip("password-generator not installed")

class TestVaultCipher:
    @pytest.fixture(autouse=True)
    def setup_env(self, master_key_b64):
        """Automatically setup and teardown environment variables for tests."""
        os.environ["UNIT_TEST_KEY"] = master_key_b64
        yield
        if "UNIT_TEST_KEY" in os.environ:
            del os.environ["UNIT_TEST_KEY"]

    def test_init_from_env(self):
        """Test VaultCipher initialization from environment variable."""
        vault = VaultCipher(key_name="UNIT_TEST_KEY")
        assert vault.verify_master_key()
        assert vault._key_source == "ENV"

    def test_init_from_file(self, test_dir, master_key_b64):
        """Test VaultCipher initialization from a key file."""
        if "UNIT_TEST_KEY" in os.environ:
            del os.environ["UNIT_TEST_KEY"]
        key_file = os.path.join(test_dir, "master.key")
        with open(key_file, "w") as f:
            f.write(master_key_b64)
        
        vault = VaultCipher(key_name="UNIT_TEST_KEY", key_path=key_file)
        assert vault.verify_master_key()
        assert vault._key_source == "FILE"

    def test_text_encryption_roundtrip(self):
        """Test AEAD text encryption and decryption with tags."""
        vault = VaultCipher(key_name="UNIT_TEST_KEY")
        plain = "Sensitive Data 123"
        tags = b"owner:adrian"
        
        encrypted = vault.encrypt_text(plain, tags=tags)
        decrypted = vault.decrypt_text(encrypted, tags=tags)
        
        assert plain == decrypted
        
        # Test failure with wrong tags
        with pytest.raises(Exception):
            vault.decrypt_text(encrypted, tags=b"owner:someone_else")

    def test_file_encryption_roundtrip(self, test_dir):
        """Test AEAD file encryption and decryption."""
        vault = VaultCipher(key_name="UNIT_TEST_KEY")
        plain_path = os.path.join(test_dir, "data.txt")
        enc_path = os.path.join(test_dir, "data.enc")
        dec_path = os.path.join(test_dir, "data.dec")
        
        content = b"Binary data \x00\xff" * 100
        with open(plain_path, "wb") as f:
            f.write(content)
            
        vault.encrypt_file(plain_path, enc_path, tags=b"file_test")
        vault.decrypt_file(enc_path, dec_path, tags=b"file_test")
        
        with open(dec_path, "rb") as f:
            assert f.read() == content

    def test_memory_scrubbing(self):
        """Test memory scrubbing to clear sensitive keys."""
        vault = VaultCipher(key_name="UNIT_TEST_KEY")
        assert vault.verify_master_key()
        vault.scrub()
        assert not vault.verify_master_key()
        with pytest.raises(RuntimeError):
            vault.encrypt_text("test")

    def test_revive(self):
        """Test reviving a scrubbed VaultCipher."""
        vault = VaultCipher(key_name="UNIT_TEST_KEY")
        vault.scrub()
        vault.revive()
        assert vault.verify_master_key()

    def test_tampered_data(self):
        """Test detection of tampered encrypted data."""
        vault = VaultCipher(key_name="UNIT_TEST_KEY")
        encrypted = vault.encrypt_text("test")
        # Tamper with the raw data (Base64)
        tampered = encrypted[:-5] + "AAAAA"
        with pytest.raises(Exception):
            vault.decrypt_text(tampered)
