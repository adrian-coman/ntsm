import unittest
import os
import shutil
import tempfile
import sys
from pathlib import Path
from datetime import datetime
from types import SimpleNamespace

# Add current directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ntsm.lib import FormatTime, dict_to_ns, Files, Archive

class TestLib(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    def test_dict_to_ns(self):
        d = {"a": 1, "b": {"c": 2}, "d": [3, {"e": 4}]}
        ns = dict_to_ns(d)
        self.assertIsInstance(ns, SimpleNamespace)
        self.assertEqual(ns.a, 1)
        self.assertEqual(ns.b.c, 2)
        self.assertEqual(ns.d[0], 3)
        self.assertEqual(ns.d[1].e, 4)

    def test_format_time(self):
        dt = datetime(2025, 2, 18, 16, 0, 0)
        self.assertEqual(FormatTime.to_str(dt), "2025-02-18")
        self.assertEqual(FormatTime.without_ms(dt), "2025-02-18 16:00:00")
        self.assertEqual(FormatTime.for_files(dt), "20250218_160000")

    def test_file_operations(self):
        # Write
        test_file = os.path.join(self.test_dir, "test.txt")
        Files.write_to_file("hello world", test_file)
        self.assertTrue(os.path.exists(test_file))
        
        # Files exist
        self.assertTrue(Files.file_exists(test_file))
        
        # Append
        Files.append_to_file("\nextra", test_file)
        with open(test_file, 'r') as f:
            self.assertEqual(f.read(), "hello world\nextra")
            
        # Size
        size = Files.get_dir_size(self.test_dir)
        self.assertGreater(size, 0)

    def test_archive_aes(self):
        # Create a source file
        src_file = os.path.join(self.test_dir, "data.txt")
        with open(src_file, 'w') as f:
            f.write("sensitive data")
            
        zip_name = "protected"
        password = "secret_password"
        
        # Test ZIP creation (AES)
        zip_path = Archive.create_zip(
            source=src_file,
            dest_path=self.test_dir,
            archive_name=zip_name,
            password=password
        )
        self.assertTrue(os.path.exists(zip_path))
        
        # Test UNZIP (AES)
        unzip_dir = os.path.join(self.test_dir, "extracted")
        extracted_path = Archive.un_zip(
            zip_path=zip_path,
            unzip_path=unzip_dir,
            password=password
        )
        
        # Verify content
        restored_file = os.path.join(unzip_dir, "data.txt")
        self.assertTrue(os.path.exists(restored_file))
        with open(restored_file, 'r') as f:
            self.assertEqual(f.read(), "sensitive data")

if __name__ == '__main__':
    unittest.main()
