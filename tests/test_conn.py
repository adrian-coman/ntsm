import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add local src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ntsm.conn import vault, token, agol, hart, hbsmr, msal

class TestConn(unittest.TestCase):

    def test_vault(self):
        with patch('ntsm.aeadencrypt.VaultCipher') as mock_vault:
            vault(key_file="test.key")
            mock_vault.assert_called_once_with(key_path="test.key", key_name=None)
            
            vault(key_env="GIS_KEY")
            mock_vault.assert_called_with(key_path=None, key_name="GIS_KEY")

    @patch('arcgis.gis.GIS')
    def test_token(self, mock_gis):
        mock_instance = MagicMock()
        mock_instance.users.me.username = "test_user"
        mock_gis.return_value = mock_instance
        
        conn = token(token="valid_token")
        self.assertIsNotNone(conn)
        mock_gis.assert_called_once_with(token="valid_token", referer="https://www.arcgis.com")

    @patch('arcgis.gis.GIS')
    def test_agol(self, mock_gis):
        mock_instance = MagicMock()
        mock_instance.users.me.username = "agol_user"
        mock_gis.return_value = mock_instance
        
        conn = agol(url="https://agol.com", user="admin", password="password")
        self.assertIsNotNone(conn)
        mock_gis.assert_called_once()

    def test_hart(self):
        with patch('requests.auth.HTTPBasicAuth') as mock_auth:
            url, auth = hart(url="https://api.com", user="user", password="pwd")
            self.assertEqual(url, "https://api.com")
            self.assertIsNotNone(auth)

    @patch('requests.get')
    def test_hbsmr(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200)
        conn = hbsmr(url="https://hbsmr.com", user="user", password="pwd")
        self.assertIsNotNone(conn)
        mock_get.assert_called_once()

    def test_msal(self):
        with patch('ntsm.lib.EmailMsal') as mock_msal:
            conn = msal(tenant_id="t", client_id="c", client_email="e", client_secret="s")
            self.assertIsNotNone(conn)
            mock_msal.assert_called_once()

if __name__ == '__main__':
    unittest.main()
