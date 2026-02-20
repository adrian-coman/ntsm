import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ntsm.conn import vault_conn, token_conn, agol_conn, hart_conn, hbsmr_conn, msal_conn

class TestConn(unittest.TestCase):

    def test_vault_conn(self):
        with patch('ntsm.aeadencrypt.VaultCipher') as mock_vault:
            vault_conn(key_file="test.key")
            mock_vault.assert_called_once_with(master_key="test.key", key_name=None)
            
            vault_conn(key_env="GIS_KEY")
            mock_vault.assert_called_with(master_key=None, key_name="GIS_KEY")

    @patch('arcgis.gis.GIS')
    def test_token_conn(self, mock_gis):
        mock_instance = MagicMock()
        mock_instance.users.me.username = "test_user"
        mock_gis.return_value = mock_instance
        
        conn = token_conn(token="valid_token")
        self.assertIsNotNone(conn)
        mock_gis.assert_called_once_with(token="valid_token", referer="https://www.arcgis.com")

    @patch('arcgis.gis.GIS')
    def test_agol_conn(self, mock_gis):
        mock_instance = MagicMock()
        mock_instance.users.me.username = "agol_user"
        mock_gis.return_value = mock_instance
        
        conn = agol_conn(url="https://agol.com", user="admin", password="password")
        self.assertIsNotNone(conn)
        mock_gis.assert_called_once()

    def test_hart_conn(self):
        with patch('requests.auth.HTTPBasicAuth') as mock_auth:
            url, auth = hart_conn(url="https://api.com", user="user", password="pwd")
            self.assertEqual(url, "https://api.com")
            self.assertIsNotNone(auth)

    @patch('requests.get')
    def test_hbsmr_conn(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200)
        conn = hbsmr_conn(url="https://hbsmr.com", user="user", password="pwd")
        self.assertIsNotNone(conn)
        mock_get.assert_called_once()

    def test_msal_conn(self):
        with patch('ntsm.lib.EmailMsal') as mock_msal:
            conn = msal_conn(tenant_id="t", client_id="c", client_email="e", client_secret="s")
            self.assertIsNotNone(conn)
            mock_msal.assert_called_once()

if __name__ == '__main__':
    unittest.main()
