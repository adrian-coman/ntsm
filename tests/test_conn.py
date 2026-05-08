import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add local src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ntsm.conn import vault, token, agol, hart, hbsmr, msal

def test_vault_config():
    """Test connection vault configuration for key resolution."""
    with patch('ntsm.aeadencrypt.VaultCipher') as mock_vault:
        vault(key_file="test.key")
        mock_vault.assert_called_once_with(key_path="test.key", key_name=None)
        
        vault(key_env="GIS_KEY")
        mock_vault.assert_called_with(key_path=None, key_name="GIS_KEY")

@patch('arcgis.gis.GIS')
def test_token_conn(mock_gis):
    """Test ArcGIS token-based connection."""
    mock_instance = MagicMock()
    mock_instance.users.me.username = "test_user"
    mock_gis.return_value = mock_instance
    
    conn = token(token="valid_token")
    assert conn is not None
    mock_gis.assert_called_once_with(token="valid_token", referer="https://www.arcgis.com")

@patch('arcgis.gis.GIS')
def test_agol_conn(mock_gis):
    """Test AGOL credentials-based connection."""
    mock_instance = MagicMock()
    mock_instance.users.me.username = "agol_user"
    mock_gis.return_value = mock_instance
    
    conn = agol(url="https://agol.com", user="admin", password="password")
    assert conn is not None
    mock_gis.assert_called_once()

def test_hart_auth():
    """Test HART basic auth construction."""
    with patch('requests.auth.HTTPBasicAuth') as mock_auth:
        url, auth = hart(url="https://api.com", user="user", password="pwd")
        assert url == "https://api.com"
        assert auth is not None

@patch('requests.get')
def test_hbsmr_conn(mock_get):
    """Test HBSMR connection validation."""
    mock_get.return_value = MagicMock(status_code=200)
    conn = hbsmr(url="https://hbsmr.com", user="user", password="pwd")
    assert conn is not None
    mock_get.assert_called_once()

def test_msal_conn():
    """Test MSAL connection wrapper."""
    with patch('ntsm.lib.EmailMsal') as mock_msal:
        conn = msal(tenant_id="t", client_id="c", client_email="e", client_secret="s")
        assert conn is not None
        mock_msal.assert_called_once()
