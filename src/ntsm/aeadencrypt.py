#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name          : aeadencrypt.py
# Author             : Adrian.Coman
# Copyright          : 2024-present Adrian Coman. All Rights Reserved.
# About              : High-Security Vault Cipher for GIS Teams.


# =====================================================================
# IMPORT MODULES
# =====================================================================
import base64
import os
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM


__all__ = ["VaultCipher", "VaultUtils"]


# =====================================================================
# CLASSES & FUNCTIONs
# =====================================================================
class VaultUtils: # noqa: D301
    """Utility methods for Vault operations, including key generation and legacy encryption.

    This class provides a collection of static methods for generating cryptographic keys,
    standardizing legacy encryption/decryption, and generating secure passwords.

    **Summary of Methods**

    ===========================   ========================================================================
    **Method**                    **Description**
    ---------------------------   ------------------------------------------------------------------------
    :meth:`.generate_key`         Generates a high-entropy 512-bit master key and saves it to a file.
    :meth:`.generate_pair_key`    Generates an RSA key pair and saves them as PEM-encoded files.
    :meth:`.encrypt_text`         Encrypts text using legacy AES-128-CBC with Zero IV and MD5 KDF.
    :meth:`.decrypt_text`         Decrypts text using legacy AES-128-CBC with Zero IV and MD5 KDF.
    :meth:`.gen_password`         Generates a random secure password with customizable length.
    ===========================   ========================================================================

    .. code-block:: python

        USAGE EXAMPLE:

        from ntsm.aeadencrypt import VaultUtils
        
        # Generate a new master key
        key_path = VaultUtils.generate_key("./keys")
        
        # Encrypt text with a legacy key
        secret = "my_password"
        encrypted = VaultUtils.encrypt_text("secret data", secret)
    """

    @staticmethod
    def generate_key(output_dir: str) -> str:
        """Generate high-entropy 512-bit master key (recommended).

        Creates a 64-byte random key, encodes it in Base64, and saves it
        to a timestamped file within the specified directory.

        Args:
            output_dir (str): The directory where the key file will be saved.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.aeadencrypt import VaultUtils
            
            # Generate key in 'secrets' folder
            path = VaultUtils.generate_key("./secrets")
            # result: "./secrets/82c75c65_2024-05-20.key"

        Returns:
            The absolute path to the generated key file.
        """
        from datetime import date
        import uuid
        os.makedirs(output_dir, exist_ok=True)
        secret = os.urandom(64)
        secret_b64 = base64.b64encode(secret).decode("ascii")
        print(f"master key length: {len(secret)} bytes (512 bits)")

        today = date.today().strftime("%Y-%m-%d")
        uid = uuid.uuid4().hex[:8]
        filename = f"{uid}_{today}.key"

        key_path = os.path.join(output_dir, filename)
        with open(key_path, "w", encoding="ascii") as f:
            f.write(secret_b64)

        return key_path

    @staticmethod
    def generate_pair_key(output_dir: str) -> tuple[str, str]:
        """Generate an RSA key pair and save as ``*.key`` files with unique ID names.

        Creates a 4096-bit RSA key pair. Both private and public keys are saved in
        PEM format to the specified directory with unique identifiers.

        Args:
            output_dir (str): The directory where the key pair files will be saved.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.aeadencrypt import VaultUtils
            
            # Generate RSA pair
            priv, pub = VaultUtils.generate_pair_key("./keys")

        Returns:
            A tuple containing (private_key_path, public_key_path).
        """
        try:
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
        except ImportError:
            raise ImportError(
                "The 'cryptography' library is not installed. "
                "Please install it using 'pip install cryptography' to use this method."
            )
        from datetime import date
        import uuid
        os.makedirs(output_dir, exist_ok=True)
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=VaultCipher.RSA_KEY_SIZE
        )
        public_key = private_key.public_key()
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        _today = date.today().strftime("%Y-%m-%d")
        uid = str(uuid.uuid4().hex[:8])
        priv_path = os.path.join(output_dir, f"s{uid}_{_today}.key")
        pub_path = os.path.join(output_dir, f"b{uid}_{_today}.key")
        with open(priv_path, 'wb') as f:
            f.write(private_pem)
        with open(pub_path, 'wb') as f:
            f.write(public_pem)
        return priv_path, pub_path

    @staticmethod
    def encrypt_text(text_to_encrypt: str, secret_key: str) -> str:
        """Encrypt text using AES-128-CBC with a user-provided secret key and zero IV.

        Standard legacy encryption method. If the secret key is not 16 characters long,
        it is hashed using MD5 to produce a 16-byte key. Uses PKCS7 padding.

        Args:
            text_to_encrypt (str): The plaintext message to encrypt.
            secret_key (str): The key used for encryption.

        .. caution::
           **SECURITY WARNING**: This method uses MD5 for key derivation and a Zero IV.
           It is intended for legacy compatibility only and is **NOT** as secure as VaultCipher.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.aeadencrypt import VaultUtils
            
            # Encrypt text
            cipher = VaultUtils.encrypt_text("Hello World", "my_secret_key")

        Returns:
            The Base64-encoded encrypted text.
        """
        import hashlib
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.primitives import padding
        except ImportError:
            raise ImportError(
                "The 'cryptography' library is not installed. "
                "Please install it using 'pip install cryptography' to use this method."
            )
        try:
            if len(secret_key) != 16:
                key = hashlib.md5(secret_key.encode('utf-8')).digest()
            else:
                key = secret_key.encode('utf-8')

            iv = b'\x00' * 16
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            encryptor = cipher.encryptor()
            
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(text_to_encrypt.encode('utf-8')) + padder.finalize()
            
            encrypted_bytes = encryptor.update(padded_data) + encryptor.finalize()
            return base64.b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")

    @staticmethod
    def decrypt_text(encrypted_text: str, secret_key: str) -> str:
        """Decrypt a Base64-encoded ciphertext using AES-128-CBC with a user-provided secret key and zero IV.

        Standard legacy decryption method. Must use the same secret key used for encryption.
        Reverses PKCS7 padding and MD5 key derivation logic.

        Args:
            encrypted_text (str): The Base64-encoded ciphertext to decrypt.
            secret_key (str): The key used for decryption.

        .. caution::
           **SECURITY WARNING**: This method uses MD5 for key derivation and a Zero IV.
           It is intended for legacy compatibility only and is **NOT** as secure as VaultCipher.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.aeadencrypt import VaultUtils
            
            # Decrypt text
            plain = VaultUtils.decrypt_text("B64DATA...", "my_secret_key")

        Returns:
            The decrypted plaintext string.
        """
        import hashlib
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.primitives import padding
        try:
            if len(secret_key) != 16:
                key = hashlib.md5(secret_key.encode('utf-8')).digest()
            else:
                key = secret_key.encode('utf-8')

            iv = b'\x00' * 16
            encrypted_bytes = base64.b64decode(encrypted_text)
            
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            
            padded_data = decryptor.update(encrypted_bytes) + decryptor.finalize()
            
            unpadder = padding.PKCS7(128).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()
            
            return data.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    @staticmethod
    def gen_password(min_len: int, max_len: int) -> str:
        """Generate a custom random secure password.

        Creates a random password using the characters from the ``password-generator``
        library, excluding common confusing special characters.

        Args:
            min_len (int): Minimum length of the password.
            max_len (int): Maximum length of the password.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.aeadencrypt import VaultUtils
            
            # Generate a 20-25 character password
            pwd = VaultUtils.gen_password(20, 25)

        Returns:
            The generated random password.
        """
        try:
            from password_generator import PasswordGenerator
        except ImportError:
            raise ImportError(
                "The 'password-generator' library is not installed. "
                "Please install it using 'pip install password-generator' to use this method."
            )
        pwo = PasswordGenerator()
        pwo.excludeschars = "!$%^,£*.()<>#+&?"
        pwo.minlen = min_len
        pwo.maxlen = max_len
        pwo.minuchars = 1
        pwo.minlchars = 1
        pwo.minnumbers = 1
        pwo.minschars = 1
        return pwo.generate()


class VaultCipher: # noqa: D301
    """High-Security Vault Cipher using AES-256-GCM with PBKDF2-HMAC-SHA512 key derivation.

    This class implements an industrial-grade "Vault" for GIS production teams. It uses a
    long-term master key (from ENV or file) to derive unique encryption keys for every
    individual blob or file, ensuring maximum security and full AAD support.

    **Summary of Methods**

    ===========================   ========================================================================
    **Method**                    **Description**
    ---------------------------   ------------------------------------------------------------------------
    :meth:`.encrypt_text`         Encrypts string/bytes into a Base64-encoded AES-256-GCM blob.
    :meth:`.decrypt_text`         Decrypts Base64 blobs back into original UTF-8 text.
    :meth:`.encrypt_file`         Encrypts a local file on disk with per-file salt/nonce.
    :meth:`.decrypt_file`         Decrypts an encrypted file back to its original state.
    :meth:`.scrub`                Manually zeroes out the master key from memory for safety.
    :meth:`.revive`               Reloads the master key from its original source.
    :meth:`.debug_status`         Prints the current internal state (isActive, key source, etc.).
    :meth:`.verify_master_key`    Verifies if the loaded master key is valid and secure.
    ===========================   ========================================================================

    .. code-block:: python

        USAGE EXAMPLE:

        from ntsm.aeadencrypt import VaultCipher
        
        # Initialize the vault instance
        vault = VaultCipher(key_name='GIS_KEY')
        
        # Encrypt sensitive string
        encrypted = vault.encrypt_text("my secret", tags=b"doc_v1")
        
        # Decrypt back
        plain = vault.decrypt_text(encrypted, tags=b"doc_v1")
        
        # Encrypt a shapefile or zip
        vault.encrypt_file("orig.zip", "secure.dat", tags=b"backup_2025")
    """

    # ---------------------------------------------------------------------
    #  Security / Cryptographic constants
    # ---------------------------------------------------------------------
    RSA_KEY_SIZE     = 4096
    KDF_ITERATIONS   = 250_000               # OWASP
    SALT_SIZE        = 16
    NONCE_SIZE       = 12                    # GCM standard
    TAG_SIZE         = 16                    # GCM Auth Tag
    ALG_LENGTH       = 32                    # AES-256 key length
    FILE_SIZE_LIMIT  = 512 * 1024 * 1024     # 512 MiB hard limit


    def __init__(self, key_name: str = "GIS_KEY", key_path: Optional[str] = None, auto_scrub_on_exit: bool = True):
        """Initialize vault instance with a master key.

        The key is loaded with the following priority:

        1. Environment variable (recommended for production).
        2. Local file on disk (convenient for development).

        Args:
            key_name (str): Name of the environment variable. Defaults to ``'GIS_KEY'``.
            key_path (str, optional): Path to a file containing the Base64 master key.
            auto_scrub_on_exit (bool): If ``True``, zeroes keys upon destruction. Defaults to ``True``.

        .. code-block:: python

            USAGE EXAMPLE:

            # From Environment
            vault = VaultCipher(key_name="MY_APP_KEY")
            
            # From File
            vault = VaultCipher(key_path="C:/keys/master.key")

        Returns:
            Initialized VaultCipher instance.
        """
        self.env_var_name = key_name
        self.master_key_path = key_path
        self.auto_scrub_on_exit = auto_scrub_on_exit
        
        self._master_key: bytearray = bytearray()
        self._is_scrubbed: bool     = False
        self._key_source: str       = "unknown"
        
        self._load_and_prepare_master_key()


    def _load_and_prepare_master_key(self) -> None:
        """Load master key bytes from env or file and validate minimum entropy."""
        
        self._is_scrubbed = False
        key_source: bytes | None = None

        # Prefer environment variable (more secure - no disk trace)
        if self.env_var_name in os.environ:
            key_source = os.environ[self.env_var_name].encode("utf-8")
            self._key_source = f"ENV"

        # Fallback to file
        elif self.master_key_path and os.path.isfile(self.master_key_path):
            with open(self.master_key_path, "rb") as f:
                key_source = f.read().strip()
                self._key_source = f"FILE"

        if key_source is None:
            raise ValueError(
                f"No encryption key found in:\n"
                f"  • ENV: {self.env_var_name}\n"
                f"  • File: {self.master_key_path or '<not provided>'}"
            )

        # Decode base64 if it looks like base64, otherwise assume raw bytes
        try:
            decoded = base64.b64decode(key_source, validate=True)
            self._master_key = bytearray(decoded)
        except Exception:
            self._master_key = bytearray(key_source)

        if len(self._master_key) < 32:
            raise ValueError("Encryption key must be at least 32 bytes (256 bits)")
        
        if all(b == 0 for b in self._master_key):
            raise RuntimeError("Encryption key appears to be zeroed / scrubbed — possible double-init or GC issue")
        
        if self._is_scrubbed:
            raise RuntimeError("Cannot reload key: instance is already scrubbed")
          

    def _check_not_scrubbed(self) -> None:
        if self._is_scrubbed:
            raise RuntimeError(
                "This VaultCipher instance has been scrubbed (keys zeroed). "
                "Create a new instance or call .revive() to reload the key."
            )


    def _derive_aes(self, salt: bytes) -> "AESGCM":
        """Internal: derive fresh AES-GCM cipher from master key + salt.
        This eliminates all code duplication and is the correct modern approach."""
        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        except ImportError:
            raise ImportError(
                "The 'cryptography' library is not installed. "
                "Please install it using 'pip install cryptography' to use this method."
            )
        self._check_not_scrubbed()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=self.ALG_LENGTH,
            salt=salt,
            iterations=self.KDF_ITERATIONS,
        )
        key = kdf.derive(bytes(self._master_key))
        return AESGCM(key)


    def _scrub_memory(self) -> None:
        import gc
        if self._is_scrubbed:
            return
        for i in range(len(self._master_key)):
            self._master_key[i] = 0
        self._master_key.clear()
        self._is_scrubbed = True
        gc.collect()


    def __enter__(self):
        self._check_not_scrubbed()
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        if self.auto_scrub_on_exit:
            self._scrub_memory()


    def __del__(self):
        if self.auto_scrub_on_exit:
            self._scrub_memory()


    def __repr__(self) -> str:
        status = "SCRUBBED" if self._is_scrubbed else "ACTIVE"
        return (
            f"<VaultCipher {status} | "
            f"source={self._key_source} | "
            f"auto_scrub={self.auto_scrub_on_exit}>"
        )


    def scrub(self):
        """Manually zero-out the master key in memory.

        Ensures that sensitive key material is removed from memory immediately
        rather than waiting for garbage collection. Useful in notebook environments.

        .. code-block:: python

            USAGE EXAMPLE:

            vault.scrub()
            # After this, the instance can no longer encrypt/decrypt until revived.

        Returns:
            None
        """
        print("Scrubbed master key.")
        self._scrub_memory()


    def revive(self):
        """Reload the encryption key from the original source (file or env).

        Restores the ``ACTIVE`` status of a scrubbed vault by re-fetching the master
        key from its original source (disk or environment).

        .. code-block:: python

            USAGE EXAMPLE:

            vault.revive()

        Returns:
            None
        """
        print(f"Reloading encryption key from {self._key_source or 'original source'} …")
        self._load_and_prepare_master_key()
        print("Key reloaded.")


    def debug_status(self):
        """Print the current internal state of the Vault instance.

        Displays whether the vault is ``ACTIVE`` or ``SCRUBBED``, the detected key source
        (``ENV``/``FILE``), and whether auto-scrub is enabled.

        .. code-block:: python

            USAGE EXAMPLE:

            vault.debug_status()

        Returns:
            None
        """
        print(f"Status:      {'SCRUBBED' if self._is_scrubbed else 'ACTIVE'}")
        print(f"Key source:  {self._key_source}")
        print(f"Key length:  {len(self._master_key)} bytes")
        print(f"Auto-scrub:  {self.auto_scrub_on_exit}")


    def verify_master_key(self) -> bool:
        """Verify if the loaded master key is valid and has sufficient length.

        Checks if the internal master key is correctly set, has minimum 256-bit
        entropy, and hasn't been scrubbed.

        .. code-block:: python

            USAGE EXAMPLE:

            if vault.verify_master_key():
                print("Key is secure and ready.")

        Returns:
            ``True`` if the key is valid, raises an exception otherwise.
        """
        try:
            self._check_not_scrubbed()
            if len(self._master_key) < 32:
                return False
            # Check if key is not just a repeating pattern (basic entropy check)
            if all(b == self._master_key[0] for b in self._master_key):
                return False
            return True
        except Exception:
            return False


    # -------------------------------------------------------------------------
    #                         Core encryption methods
    # -------------------------------------------------------------------------
    def encrypt_text(self, plaintext: str | bytes, tags: Optional[bytes] = None) -> str:
        """Encrypt text or bytes using AES-256-GCM.

        Produces a standardized Base64 blob containing everything needed for decryption
        (salt, nonce) and the ciphertext with its authentication tag.

        Args:
            plaintext (str | bytes): The message to encrypt.
            tags (bytes, optional): Associated Data (AAD) for authentication.

        .. code-block:: python

            USAGE EXAMPLE:

            vault = VaultCipher(key_name="GIS_KEY")
            blob = vault.encrypt_text("GIS data", tags=b"project:77")

        Returns:
            Base64-encoded string: ``b64( salt + nonce + ciphertext + tag )``.
        """
        self._check_not_scrubbed()
        
        data = plaintext.encode("utf-8") if isinstance(plaintext, str) else plaintext
        salt = os.urandom(self.SALT_SIZE)
        nonce = os.urandom(self.NONCE_SIZE)
        aes = self._derive_aes(salt)
        ciphertext = aes.encrypt(nonce, data, tags)

        return base64.b64encode(salt + nonce + ciphertext).decode("ascii")


    def decrypt_text(self, encryptedtext: str | bytes, tags: Optional[bytes] = None) -> str:
        """Decrypt a Base64 blob back into original UTF-8 text.

        Validates the authentication tag using the provided Associated Data (tags).
        If the data has been tampered with, it raises ``InvalidTag``.

        Args:
            encryptedtext (str | bytes): The Base64 blob to decrypt.
            tags (bytes, optional): Must match the tags used during encryption.

        .. code-block:: python

            USAGE EXAMPLE:

            # Decrypt matching the original tags
            secret = vault.decrypt_text(blob, tags=b"project:77")

        Returns:
            The original plaintext as a UTF-8 string.
        """
        self._check_not_scrubbed()
        
        blob = base64.b64decode(encryptedtext) if isinstance(encryptedtext, str) else encryptedtext

        min_len = self.SALT_SIZE + self.NONCE_SIZE + self.TAG_SIZE
        if len(blob) < min_len:
            raise ValueError(f"Input too short to be valid encrypted text (need ≥ {min_len} bytes)")
        
        salt = blob[:self.SALT_SIZE]
        nonce = blob[self.SALT_SIZE : self.SALT_SIZE + self.NONCE_SIZE]
        data = blob[self.SALT_SIZE + self.NONCE_SIZE :]
        aes = self._derive_aes(salt)
        plaintext = aes.decrypt(nonce, data, tags)

        return plaintext.decode("utf-8")


    def encrypt_file(self, input_path: str, output_path: str, tags: Optional[bytes] = None) -> None:
        """Encrypt a local file using AES-256-GCM authenticated encryption.

        Standard file encryption flow. Enforces a 512 MiB size limit to prevent
        memory exhaustion. The output file contains the salt, nonce, and ciphertext.

        Args:
            input_path (str): Path to the original unencrypted file.
            output_path (str): Path where the encrypted result will be saved.
            tags (bytes, optional): Associated Data for file authentication.

        .. code-block:: python

            USAGE EXAMPLE:

            vault.encrypt_file("config.json", "config.dat", tags=b"v1")

        Returns:
            None
        """
        self._check_not_scrubbed()
        
        if not os.path.isfile(input_path):
            raise FileNotFoundError(input_path)

        if os.path.getsize(input_path) > self.FILE_SIZE_LIMIT:
            raise ValueError(f"File too large (> {self.FILE_SIZE_LIMIT // (1024**2)} MiB).")

        with open(input_path, "rb") as f:
            data = f.read()

        salt = os.urandom(self.SALT_SIZE)
        nonce = os.urandom(self.NONCE_SIZE)
        aes = self._derive_aes(salt)
        ct = aes.encrypt(nonce, data, tags)

        with open(output_path, "wb") as f:
            f.write(salt + nonce + ct)


    def decrypt_file(self, input_path: str, output_path: str, tags: Optional[bytes] = None) -> None:
        """Decrypt an encrypted file back to its original state.

        Validates the integrity of the file using the authentication tag and the
        provided Associated Data (tags).

        Args:
            input_path (str): Path to the encrypted file.
            output_path (str): Path where the decrypted result will be saved.
            tags (bytes, optional): Must match the tags used during encryption.

        .. code-block:: python

            USAGE EXAMPLE:

            vault.decrypt_file("config.dat", "config_restored.json", tags=b"v1")

        Returns:
            None
        """
        self._check_not_scrubbed()
        
        if not os.path.isfile(input_path):
            raise FileNotFoundError(input_path)

        with open(input_path, "rb") as f:
            blob = f.read()

        min_len = self.SALT_SIZE + self.NONCE_SIZE + self.TAG_SIZE
        if len(blob) < min_len:
            raise ValueError(f"File too short to be valid encrypted text (need ≥ {min_len} bytes)")

        salt = blob[:self.SALT_SIZE]
        nonce = blob[self.SALT_SIZE : self.SALT_SIZE + self.NONCE_SIZE]
        ct_tag = blob[self.SALT_SIZE + self.NONCE_SIZE :]
        aes = self._derive_aes(salt)
        plaintext = aes.decrypt(nonce, ct_tag, tags)

        with open(output_path, "wb") as f:
            f.write(plaintext)


