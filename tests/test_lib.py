import pytest
import os
import shutil
import tempfile
import sys
from pathlib import Path
from datetime import datetime
from types import SimpleNamespace

# Add local src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ntsm.lib import FormatTime, dict_to_ns, Files, Archive, LazyNodes, LazyListProxy

@pytest.fixture
def test_dir():
    """Fixture to create and cleanup a temporary directory for tests."""
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)

def test_dict_to_ns():
    """Test recursive dictionary to SimpleNamespace conversion."""
    d = {"a": 1, "b": {"c": 2}, "d": [3, {"e": 4}]}
    ns = dict_to_ns(d)
    assert isinstance(ns, SimpleNamespace)
    assert ns.a == 1
    assert ns.b.c == 2
    assert ns.d[0] == 3
    assert ns.d[1].e == 4

def test_lazy_list_proxy():
    """Test LazyListProxy functionality including indexing and slicing."""
    raw = [1, 2, 3]
    proxy = LazyListProxy(raw, lambda x: x * 2)
    assert len(proxy) == 3
    assert proxy[0] == 2
    assert proxy[1] == 4
    assert proxy[-1] == 6
    assert list(proxy) == [2, 4, 6]
    assert proxy[0:2] == [2, 4]

def test_lazy_nodes():
    """Test LazyNodes for attribute access and recursive lazy wrapping."""
    data = {
        "meta": {"ver": 1},
        "items": [{"id": 10}, {"id": 20}]
    }
    nodes = LazyNodes(data)
    
    # Test attribute access
    assert nodes.meta.ver == 1
    assert nodes.items[0].id == 10
    
    # Test dictionary-like access
    assert nodes["meta"]["ver"] == 1
    
    # Test contains
    assert "meta" in nodes
    
    # Test get
    assert nodes.get("meta").ver == 1
    assert nodes.get("missing", "default") == "default"
    
    # Test to_dict
    assert nodes.to_dict() == data

def test_format_time():
    """Test FormatTime utility methods."""
    dt = datetime(2025, 2, 18, 16, 0, 0)
    assert FormatTime.to_str(dt) == "2025-02-18"
    assert FormatTime.without_ms(dt) == "2025-02-18 16:00:00"
    assert FormatTime.for_files(dt) == "20250218_160000"

def test_file_operations(test_dir):
    """Test basic file system utilities."""
    test_file = os.path.join(test_dir, "test.txt")
    Files.write_to_file("hello world", test_file)
    assert os.path.exists(test_file)
    assert Files.file_exists(test_file)
    
    Files.append_to_file("\nextra", test_file)
    with open(test_file, 'r') as f:
        assert f.read() == "hello world\nextra"
        
    size = Files.get_dir_size(test_dir)
    assert size > 0

def test_archive_aes(test_dir):
    """Test password-protected AES ZIP creation and extraction."""
    src_file = os.path.join(test_dir, "data.txt")
    with open(src_file, 'w') as f:
        f.write("sensitive data")
        
    zip_name = "protected"
    password = "secret_password"
    
    zip_path = Archive.make_zip(
        source=src_file,
        dest_path=test_dir,
        archive_name=zip_name,
        password=password
    )
    assert os.path.exists(zip_path)
    
    unzip_dir = os.path.join(test_dir, "extracted")
    Archive.un_zip(
        zip_path=zip_path,
        unzip_path=unzip_dir,
        password=password
    )
    
    restored_file = os.path.join(unzip_dir, "data.txt")
    assert os.path.exists(restored_file)
    with open(restored_file, 'r') as f:
        assert f.read() == "sensitive data"

@pytest.mark.asyncio
async def test_url_validation():
    """Test security validation for URL requests."""
    from ntsm.lib import send_url_request, download
    with pytest.raises(ValueError):
        send_url_request("file:///etc/passwd")
    
    with pytest.raises(ValueError):
        await download("file:///etc/passwd", "test.txt")

@pytest.mark.asyncio
async def test_download_sanitization():
    """Test path traversal protection in file downloads."""
    from ntsm.lib import download
    with pytest.raises(ValueError):
        await download("https://example.com", "/tmp/malicious.txt")
    with pytest.raises(ValueError):
        await download("https://example.com", "../malicious.txt")

def test_zip_slip_protection(test_dir):
    """Test protection against Zip Slip vulnerability."""
    import zipfile
    import io
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as arch:
        # Create a malicious entry attempting path traversal
        arch.writestr("../../../evil.txt", "evil content")
    
    zip_path = os.path.join(test_dir, "slip.zip")
    with open(zip_path, "wb") as f:
        f.write(zip_buffer.getvalue())
        
    unzip_dir = os.path.join(test_dir, "extracted_safe")
    with pytest.raises(ValueError, match="Malicious ZIP member detected"):
        Archive.un_zip(zip_path, unzip_dir)
