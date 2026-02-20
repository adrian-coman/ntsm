
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name          : conn.py
# Author             : Adrian.Coman
# Copyright          : 2024-present Adrian Coman. All Rights Reserved.
# About              : Connection module, transition and backward compatibility version.


# IMPORT MODULES
import os
from typing import Any

# ===============================================================
#           START: DO NOT CHANGE UNTIL THE END MESSAGE
# ===============================================================

def vault(key_file: str = None, key_env: str = None) -> Any:
    """Initialize and return a VaultCipher instance for encryption/decryption.

    Sets up a secure vault using either a physical master key file
    or an environment variable.

    Args:
        key_file (str, optional): Absolute path to the master key file.
        key_env (str, optional): Name of the environment variable containing the key.

    .. code-block:: python

        from ntsm.conn import vault
        # via environment variable
        v = vault(key_env="GIS_KEY")
        # OR via local file
        v = vault(key_file="C:/keys/prod.key")

    Returns:
        An instance of VaultCipher.
    """
    from ntsm.aeadencrypt import VaultCipher
    return VaultCipher(master_key=key_file, key_name=key_env)


def token(token: str, debug: bool = False) -> Any:
    """Initialize and return an ArcGIS GIS connection using a token.

    Args:
        token (str): The ArcGIS authentication token.
        debug (bool): If ``True``, prints connection status. Defaults to ``False``.

    .. code-block:: python

        from ntsm.conn import token
        gis = token(token="YOUR_ARCGIS_TOKEN", debug=True)

    Returns:
        An authenticated GIS object if successful, otherwise ``None``.
    """
    if not token:
        return None

    try:
        try:
            from arcgis.gis import GIS
        except ImportError:
            raise ImportError("The 'arcgis' library is not installed. Please install it with 'pip install arcgis'.")

        conn = GIS(token=token, referer="https://www.arcgis.com")
        username = conn.users.me.username
        
        if username:
            if debug: print(f"TOKEN in use - {username}.")
            return conn
    except Exception as e:
        if debug: print(f"TOKEN connection failed: {e}")
    
    return None


def agol(url: str, user: str, password: str, debug: bool = False) -> Any:
    """Initialize and return an ArcGIS Online GIS connection using credentials.

    Args:
        url (str): The target AGOL URL.
        user (str): The AGOL username.
        password (str): The user password.
        debug (bool): If ``True``, prints connection status. Defaults to ``False``.

    .. code-block:: python

        from ntsm.conn import agol
        gis = agol(url="https://nt.maps.arcgis.com", user="username", password="password", debug=True)

    Returns:
        An authenticated AGOL GIS object if successful, otherwise ``None``.
    """
    if not all([url, user, password]):
        return None

    try:
        try:
            from arcgis.gis import GIS
        except ImportError:
            raise ImportError("The 'arcgis' library is not installed. Please install it with 'pip install arcgis'.")

        conn = GIS(url=url, username=user, password=password, verify_cert=False)
        username = conn.users.me.username
        
        if username:
            if debug: print(f"AGOL in use - {username}.")
            return conn
    except Exception as e:
        if debug: print(f"AGOL connection failed: {e}")
    
    return None


def hart(url: str, user: str, password: str, debug: bool = False) -> Any:
    """Initialize and return a HART API connection tuple (URL, HTTPBasicAuth).

    Args:
        url (str): The base HART API URL.
        user (str): The user username.
        password (str): The user password.
        debug (bool): If ``True``, prints connection status. Defaults to ``False``.

    .. code-block:: python

        from ntsm.conn import hart
        import requests
        url, auth = hart(url="API_URL", user="user", password="pwd")
        response = requests.get(url, auth=auth)

    Returns:
        Tuple of ``(api_url, auth_object)`` if successful, otherwise ``None``.
    """
    if not all([url, user, password]):
        return None

    try:
        try:
            from requests.auth import HTTPBasicAuth
        except ImportError:
            raise ImportError("The 'requests' library is not installed. Please install it with 'pip install requests'.")

        auth = HTTPBasicAuth(user, password)
        if debug: print(f"HART API in use - {user}.")
        return url, auth
    except Exception as e:
        if debug: print(f"HART connection failed: {e}")
            
    return None


def hbsmr(url: str, user: str, password: str, debug: bool = False) -> Any:
    """Initialize and return a HBSMR API connection response.

    Args:
        url (str): The HBSMR API endpoint.
        user (str): The user username.
        password (str): The user password.
        debug (bool): If ``True``, prints connection status. Defaults to ``False``.

    .. code-block:: python

        from ntsm.conn import hbsmr
        resp = hbsmr(url="API_URL", user="user", password="pwd")
        if resp:
            data = resp.json()

    Returns:
        The response object from the HBSMR API if successful, otherwise ``None``.
    """
    if not all([url, user, password]):
        return None

    try:
        import base64
        try:
            import requests
        except ImportError:
            raise ImportError("The 'requests' library is not installed. Please install it with 'pip install requests'.")
        
        creds = base64.b64encode(f"{user}:{password}".encode()).decode()
        headers = {"Authorization": f"Basic {creds}"}
        
        resp = requests.get(url, headers=headers, allow_redirects=True)
        if resp:
            if debug: print("HBSMR API in use.")
            return resp
    except Exception as e:
        if debug: print(f"HBSMR connection failed: {e}")
            
    return None


def msal(tenant_id: str, client_id: str, client_email: str, client_secret: str, debug: bool = False) -> Any:
    """Initialize and return an EmailMsal connection object.

    Args:
        tenant_id (str): Azure AD Tenant ID.
        client_id (str): Azure AD Client ID.
        client_email (str): The mailbox used to send email.
        client_secret (str): The client secret.
        debug (bool): If ``True``, prints connection status. Defaults to ``False``.

    .. code-block:: python

        from ntsm.conn import msal
        mail = msal(tenant_id="...", client_id="...", client_email="...", client_secret="...")
        mail.send_email(to="test@example.com", subject="Hello", body="Test")

    Returns:
        An authenticated ``EmailMsal`` instance if successful, otherwise ``None``.
    """
    if not all([tenant_id, client_id, client_email, client_secret]):
        return None

    try:
        from ntsm.lib import EmailMsal
        
        conn = EmailMsal(
            tenant_id=tenant_id,
            client_id=client_id,
            client_email=client_email,
            client_secret=client_secret
        )
        
        if debug: print(f"MSAL EMAIL in use - {client_email}.")
        return conn
    except Exception as e:
        if debug: print(f"EMAIL connection failed: {e}")
            
    return None

# ===============================================================
#                           END MESSAGE
# ===============================================================



