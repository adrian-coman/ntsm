import webbrowser

def _read():
    """Opens the official Read the Docs page."""
    url = "https://ntsm.readthedocs.io/en/latest/"
    print(f"Opening documentation: {url}")
    webbrowser.open(url, new=2)

if __name__ == "__main__":
    _read()