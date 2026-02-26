#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name          : lib.py
# Author             : Adrian.Coman
# Copyright          : 2024-present Adrian Coman. All Rights Reserved.
# About              : Custom library collection for GIS Teams.


# =====================================================================
# IMPORT MODULES
# =====================================================================
import os
import shutil
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Callable, Any, Literal, Union, List, Optional


__all__ = [
    'check_py_env',
    'get_project_paths',
    'send_url_request',
    'download',
    'timer_wrap',
    'truncate_decimals',
    'dict_to_ns',
    'setup_logging',
    'FormatTime',
    'Email',
    'EmailMsal',
    'Files',
    'Archive',
    'Args',
    'DS'
]

# =====================================================================
# CLASSES & FUNCTIONs
# =====================================================================
def check_py_env() -> str:
    """Identify the current Python execution environment.

    Determines if the script is running within an interactive Jupyter Notebook 
    (or similar IPython-based environment) or a standard Python interpreter.

    .. code-block:: python

        USAGE EXAMPLE:

        from ntsm.lib import check_py_env
        
        # Get environment type
        env_type = check_py_env()
        
        if env_type == "Jupyter":
            print("Running in a Notebook - Enabling Rich Outputs")
        else:
            print("Running in standard Python - Console mode")

    Returns:
        ``'Jupyter'`` if in a notebook environment, otherwise ``'Python'``.
    """ 
    try:
        # Try to import IPython functionality
        from IPython import get_ipython
        
        # get_ipython() returns None if not in an IPython session
        shell = get_ipython()
        
        if shell is None:
            return "Python"
            
        if 'IPKernelApp' in shell.config:
            return "Jupyter"
        
        return "Python"
        
    except (ImportError, NameError, AttributeError):
        return "Python"


def get_project_paths(file_ref: str) -> tuple[str, str]:
    """Calculate the absolute execution path and the workspace root directory.

    This utility standardizes path resolution regardless of whether the code is 
    running as a standard Python script or within an interactive Jupyter 
    notebook environment.

    Args:
        file_ref (str): Typically ``__file__`` when called from a script.
            Used to determine the directory of the executing file.

    .. code-block:: python

        USAGE EXAMPLE:

        from ntsm.lib import get_project_paths
        
        # When called from 'C:/Project/src/worker.py':
        path, wks = get_project_paths(__file__)
        
        # path -> 'C:/Project/src'
        # wks  -> 'C:/Project'

    Returns:
        Tuple of ``(execution_path, workspace_root)``.
    """
    # Check environment via your helper
    if check_py_env() == "Jupyter":
        path = os.getcwd()
    else:
        path = os.path.dirname(os.path.realpath(file_ref))
    
    # Workspace is assumed to be one level up from the execution path
    wks = os.path.dirname(path)
    
    return path, wks


def send_url_request(request: Any)-> Any:
    """Send an HTTP request and return the JSON response.

    Args:
        request: A ``urllib.request.Request`` object or a URL string.

    .. code-block:: python

        USAGE EXAMPLE:

        # import module
        from ntsm.lib import send_url_request

        # create request
        url = 'https://api.example.com/data'
        
        # get json data
        data = send_url_request(url)

    Returns:
        The parsed JSON data from the server response.
    """

    import urllib
    
    response = urllib.request.urlopen(request)
    readResponse = response.read()
    jsonResponse = json.loads(readResponse)
    return jsonResponse


async def download(url: str, filename: str) -> None:
    """Download a file from a URL to the local file system (Universal Async).

    Automatically detects the environment:

    1. In **Browser (Pyodide)**: Uses ``pyfetch``.
    2. In **Desktop/Server**: Uses ``urllib`` wrapped in a thread to prevent blocking.

    Args:
        url (str): The URL address of the file to download.
        filename (str): The local path/filename to save the file.

    .. code-block:: python

        USAGE EXAMPLE:

        import asyncio
        from ntsm.lib import download

        url = 'https://example.com/data.zip'
        path = './data.zip'
        
        # In a notebook, just use:
        await download(url, path)

    Returns:
        None
    """
    try:
        # --- 1. Browser Approach (Pyodide) ---
        from pyodide.http import pyfetch
        
        response = await pyfetch(url)
        if response.status == 200:
            with open(filename, "wb") as f:
                f.write(await response.bytes())
        else:
            raise RuntimeWarning(f"Download failed: Status {response.status}")

    except ImportError:
        # --- 2. Desktop Approach (urllib) ---
        import urllib.request
        import asyncio

        # We use run_in_executor so the sync urllib call doesn't freeze the async loop
        def sync_download():
            with urllib.request.urlopen(url) as response:
                with open(filename, "wb") as f:
                    f.write(response.read())

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, sync_download)


def timer_wrap(func:Callable)->Callable:
    """Decorator that calculates and prints the execution time of a function.

    Args:
        func (Callable): The function to be wrapped for timing.

    .. code-block:: python

        USAGE EXAMPLE:

        # import module
        from ntsm.lib import timer_wrap

        @timer_wrap
        def my_process():
            time.sleep(1)
            return "Done"
        
        # execution will print: - function 'my_process' took: 1.0000 sec
        result = my_process()

    Returns:
        The wrapper function that executes the timing logic.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        results = func(*args, **kwargs)
        end_time = time.time()
        text_time = f"- function {func.__name__!r} took: {end_time-start_time:.4f} sec"
        print(text_time)
        return results
    return wrapper


def truncate_decimals(n: float|int, d: int = 0)->float|int:
    """Truncate a number to a specified number of decimal places.

    Args:
        n (float | int): The number to be truncated.
        d (int): Decimal places to keep. Defaults to ``0`` (integer-like result).

    .. code-block:: python

        USAGE EXAMPLE:

        # import module
        from ntsm.lib import truncate_decimals
        
        # truncate to 4 decimals
        val = 123.456789
        result = truncate_decimals(val, 4)
        # result: 123.4567

    Returns:
        The number truncated to the requested decimal places.
    """
    multiplier = 10 ** d
    num_out = int(n * multiplier) / multiplier
    return num_out


def dict_to_ns(in_dict: Any) -> Any:
    """Recursively convert a dictionary and its nested structures into a SimpleNamespace.

    Transforms a standard dictionary into a ``SimpleNamespace``, 
    enabling dot-notation access (e.g., ``obj.key``) at all nested levels.

    Args:
        in_dict: The dictionary or list to convert.
            Non-collection types are returned unchanged.

    .. code-block:: python

        USAGE EXAMPLE:

        from ntsm.lib import dict_to_ns
        
        data = {
            "project": "OSM_Query",
            "settings": {"threads": 4, "timeout": 30},
            "workers": [{"id": 1}, {"id": 2}]
        }
        
        ns = dict_to_ns(data)
        
        # Access nested data with dots
        print(ns.settings.threads)  # Output: 4
        print(ns.workers[0].id)     # Output: 1

    Returns:
        The converted structure as a ``SimpleNamespace``, a list of namespaces, or the original value.
    """ 
    from types import SimpleNamespace
    
    if isinstance(in_dict, dict):
        return SimpleNamespace(**{k: dict_to_ns(v) for k, v in in_dict.items()})
    elif isinstance(in_dict, list):
        return [dict_to_ns(i) for i in in_dict]
    return in_dict


def setup_logging(log_name: str, log_dir: str, level: Literal["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"] = "INFO") -> Any:
    """Initialize a standardized Loguru logger with custom naming and storage.

    Configures a file-based logger with automatic rotation and compression.
    Removes the default system handler so logs are directed only to the file.

    **Level Behaviors:**

    * **DEBUG**: Maximum detail. Enables ``backtrace`` and ``diagnose``.
    * **INFO**: Standard operation without diagnostic overhead.
    * **WARNING/ERROR/CRITICAL**: Enables ``catch`` to prevent log failures from crashing the app.

    Args:
        log_name (str): Filename for the log (e.g., ``'worker_01'``).
            The ``.log`` extension is appended automatically.
        log_dir (str): Directory path where logs should be saved.
        level (str): Logging threshold. Defaults to ``"INFO"``.

    .. code-block:: python

        USAGE EXAMPLE:

        from ntsm.lib import setup_logging
        from pathlib import Path 
        
        # Setup a specific log for a worker
        log_name = Path(__file__).stem
        log_path = Path(__wks__) / 'log' 
        Log = setup_logging(log_name, log_path, level="DEBUG")
        
        Log.info("Logger initialized and ready.")
        Log.debug("Deep diagnostic info is captured here.")  
        
        try:
            1/0
        except Exception:
            Log.exception("This captures the stack trace automatically.")

    Returns:
        A pre-configured Loguru logger instance.
    """
    
    try:
        from loguru import logger
    except ImportError:
        raise ImportError(
            "The 'loguru' library is not installed. "
            "Please install it using 'pip install loguru' to use this method."
        )
    
    # Ensure file extension is handled correctly
    if not log_name.endswith(".log"):
        log_name = f"{log_name}.log"
        
    log_path = os.path.join(log_dir, log_name)

    # Ensure the directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Define common configuration
    log_config = {
        "sink": log_path,
        "rotation": "1 MB",
        "compression": "zip",
        "level": level,
        "mode": "a",
        "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    }

    # High-Detail Debugging: Only for DEBUG
    if level == "DEBUG":
        log_config["backtrace"] = True
        log_config["diagnose"] = True

    # Production Safety: For WARNING, ERROR, and CRITICAL
    if level in ["WARNING", "ERROR", "CRITICAL"]:
        log_config["catch"] = True

    # Configure Loguru
    logger.remove()
    logger.add(**log_config)
    
    logger.info(f"--- Session Started: {log_name} ---")
    return logger


class FormatTime: # noqa: D301
    """A collection of static methods for standardized datetime formatting and time calculations.

    This class provides a centralized suite of utilities to convert Python ``datetime`` objects 
    into specific string formats required for various environments such as OpenStreetMap (OSM), 
    Esri Geodatabases (GDB), logging systems, and file naming conventions.

    **Summary of Methods**

    =========================   ========================================================================
    **Method**                  **Description**
    -------------------------   ------------------------------------------------------------------------
    :meth:`.time_difference`    Calculates the delta between two time points as ``hh:mm:ss``.
    :meth:`.timer_now`           Calculates elapsed time from a previous point until the current moment.
    :meth:`.without_ms`         Returns a standard timestamp string without millisecond fractions.
    :meth:`.to_str`             The base formatting method supporting custom ``strftime`` patterns.
    :meth:`.from_osm`           Cleans OSM ISO-8601 strings into SQL-friendly timestamps.
    :meth:`.for_osm`            Formats datetime objects for OSM Overpass API queries.
    :meth:`.for_log`            Formats datetime for standard logs (YYYY-MM-DD HH:MM:SS).
    :meth:`.for_gdb`            Formats datetime specifically for Esri GDB (DD/MM/YYYY HH:MM:SS).
    :meth:`.for_files`          Formats datetime for safe and sortable filenames (YYYYMMDD_HHMMSS).
    =========================   ========================================================================

    .. code-block:: python

        USAGE EXAMPLE:

        from ntsm.lib import FormatTime as ft
        from datetime import datetime

        now = datetime.now()
        
        # Quick formatting for a filename
        fname = f"backup_{ft.for_files(now)}.zip"
        
        # Calculate process duration
        start = datetime.now()
        # ... some code ...
        duration = ft.timer_now(start)
    """
    
    @staticmethod
    def time_difference(time_start:datetime, time_end:datetime)->str:
        """Calculate the time difference between two datetime objects.

        Args:
            time_start (datetime): The starting time point.
            time_end (datetime): The ending time point.

        .. code-block:: python

            USAGE EXAMPLE:

            # import module
            from ntsm.lib import FormatTime as ft
            
            # calculate difference
            start = datetime.now()
            end = start + timedelta(hours=1, minutes=30, seconds=15)
            
            processing_time = ft.time_difference(start, end)
            # result: "1:30:15"

        Returns:
            Time difference formatted as a string (``hh:mm:ss``).
        """
        time_diff = time_end - time_start
        return str(time_diff).split(".")[0]

    @staticmethod
    def timer_now(time_in:datetime)->str:
        """Calculate the time difference between a provided timestamp and the current moment.

        Useful for tracking interim or partial processing times during 
        long-running tasks by comparing the current system time against a start point.

        Args:
            time_in (datetime): The previous timestamp to compare against now.

        .. code-block:: python

            USAGE EXAMPLE:

            # import module
            from datetime import datetime
            import time
            from ntsm.lib import FormatTime
            
            # mark start
            start_point = datetime.now()
            
            # simulate work
            time.sleep(2)
            
            # get interim time
            elapsed = FormatTime.timer_now(start_point)
            # result: "0:00:02"

        Returns:
            Time difference formatted as a string (``hh:mm:ss``).
        """

        time_end = datetime.now()
        time_diff = time_end - time_in
        time_out = str(time_diff).split(".")[0]
        return f"{time_out}"
     
    @staticmethod
    def without_ms(time_in:datetime)->str:
        """Convert a datetime object to a string while removing millisecond precision.

        Note:
            This is an underlying custom formatting logic derived from :meth:`~ntsm.lib.FormatTime.to_str`.

        Args:
            time_in (datetime): The datetime object to be converted.

        .. code-block:: python

            USAGE EXAMPLE:

            # import module
            from datetime import datetime
            from ntsm.lib import FormatTime
            
            # format without milliseconds
            now = datetime.now() 
            # e.g., 2024-05-20 14:30:05.123456
            
            clean_time = FormatTime.without_ms(now)
            # result: "2024-05-20 14:30:05"

        Returns:
            Date and time string without milliseconds.
        """
        return str(time_in).split(".")[0]

    @staticmethod
    def to_str(time_in:datetime, format:str="%Y-%m-%d")->str:
        """Format a datetime object as a text string using a custom ``strftime`` pattern.

        Args:
            time_in (datetime): The datetime object to be formatted.
            format (str): The ``strftime`` format string. Defaults to ``"%Y-%m-%d"``.

        .. code-block:: python

            USAGE EXAMPLE:

            # import module
            from ntsm.lib import FormatTime
            
            # format date
            now = datetime.now()
            date_str = FormatTime.to_str(now)
            # result: "2024-05-20"

        Returns:
            Date formatted as a string (default: ``YYYY-MM-DD``).
        """
        return time_in.strftime(format)

    @staticmethod
    def from_osm(time_in:datetime)->str:
        """Convert an OSM ISO-8601 timestamp string to a SQL-friendly text format.

        Converts (e.g., ``"2023-10-27T10:30:00Z"``) into ``"2023-10-27 10:30:00"``.

        Args:
            time_in (str): The OSM-formatted timestamp string (ISO-8601).

        .. code-block:: python

            USAGE EXAMPLE:

            # import module
            from ntsm.lib import FormatTime
            
            # format from OSM string
            osm_val = "2024-05-20T14:30:05Z"
            clean_val = FormatTime.from_osm(osm_val)
            # result: "2024-05-20 14:30:05"

        Returns:
            A cleaned date-time string.
        """
        return time_in.replace("T", " ").replace("Z", "")

    @staticmethod
    def for_osm(time_in:datetime)->str:
        """Format a datetime object for OpenStreetMap (OSM) Overpass API queries.

        Produces the specific ISO-8601 string format ``"YYYY-MM-DDTHH:MM:SSZ"``.

        Args:
            time_in (datetime): The datetime object to be formatted.

        .. code-block:: python

            USAGE EXAMPLE:

            # import module
            from ntsm.lib import FormatTime
            
            # format for OSM
            now = datetime.now()
            osm_timestamp = FormatTime.for_osm(now)
            # result: '"2024-05-20T14:30:05Z"'

        Returns:
            Date and time formatted as an OSM-compatible string.
        """
        return time_in.strftime('"%Y-%m-%d{0}%H:%M:%S{1}"'.format("T", "Z"))

    @staticmethod
    def for_log(time_in:datetime)->str:
        """Format a datetime object as a standard log/DB timestamp (``YYYY-MM-DD HH:MM:SS``).

        Note:
            This is an underlying custom formatting logic derived from :meth:`~ntsm.lib.FormatTime.to_str`.

        Args:
            time_in (datetime): The datetime object to be formatted.

        .. code-block:: python

            USAGE EXAMPLE:

            # import module
            from ntsm.lib import FormatTime
            
            # format for log
            now = datetime.now()
            log_time = FormatTime.for_log(now)
            # result: "2024-05-20 14:30:05"

        Returns:
            The formatted time string.
        """
        return time_in.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def for_gdb(time_in:datetime)->str:
        """Format a datetime object for Esri Geodatabase (GDB) inserts (``DD/MM/YYYY HH:MM:SS``).

        Note:
            This is an underlying custom formatting logic derived from :meth:`~ntsm.lib.FormatTime.to_str`.

        Args:
            time_in (datetime): The datetime object to be formatted.

        .. code-block:: python

            USAGE EXAMPLE:

            # import module
            from ntsm.lib import FormatTime
            
            # format for GDB
            now = datetime.now()
            gdb_timestamp = FormatTime.for_gdb(now)
            # result: "20/05/2024 14:30:05"

        Returns:
            Date and time formatted as a GDB-compatible string.
        """
        return time_in.strftime("%d/%m/%Y %H:%M:%S")

    @staticmethod
    def for_files(time_in:datetime)->str:
        """Format a datetime object as a filename-safe string (``YYYYMMDD_HHMMSS``).

        Produces a sortable timestamp that avoids characters prohibited by operating
        systems (like colons or slashes), ideal for log files or exports.

        Note:
            This is an underlying custom formatting logic derived from :meth:`~ntsm.lib.FormatTime.to_str`.

        Args:
            time_in (datetime): The datetime object to be formatted.

        .. code-block:: python

            USAGE EXAMPLE:

            # import module
            from ntsm.lib import FormatTime
            
            # format for filename
            now = datetime.now()
            file_suffix = FormatTime.for_files(now)
            
            filename = f"report_{file_suffix}_data.csv"
            # result: "report_20240520_143005_data.csv"

        Returns:
            Date and time formatted as a filename-safe string.
        """
        return time_in.strftime("%Y%m%d_%H%M%S")


class Email: # noqa: D301
    """Standardized SMTP client for persistent email configurations.

    Stores server credentials and connection settings, allowing 
    for multiple email transmissions without re-passing sensitive configuration.

    **Summary of Methods**

    =========================   ========================================================================
    **Method**                  **Description**
    -------------------------   ------------------------------------------------------------------------
    :meth:`.send`               The primary interface for sending text/HTML emails with CC, BCC, and files.
    =========================   ========================================================================

    Args:
        srv_name (str): Server address (e.g., ``'smtp.office365.com'``).
        srv_port (int): Server port (e.g., ``587`` for TLS, ``465`` for SSL).
        acc_sender (str): The authenticated sender email address.
        acc_password (str): The account password or App Password.

    .. code-block:: python

        USAGE EXAMPLE:

        from ntsm.lib import Email

        # 1. Initialize once with server credentials
        mailer = Email('smtp.office365.com', 587, 'bot@nt.org.uk', 'app_password_123')

        # 2. Send complex email with multiple recipients, CC, and BCC
        mailer.send(
            recipient=['manager_01@nt.org.uk', 'manager_02@nt.org.uk'],  # List of primary recipients
            subject='Weekly GIS Audit - All Regions',
            body='<h1>Audit Complete</h1><p>Reports for all regions are attached.</p>',
            cc=['supervisor@nt.org.uk'],                                # Visible Carbon Copy
            bcc=['audit_logs@nt.org.uk', 'admin_backup@nt.org.uk'],     # Hidden Blind Carbon Copy
            attachments=['C:/Data/Region_A.csv', 'C:/Data/Region_B.csv'],
            is_html=True
        )
    """

    def __init__(self, srv_name: str, srv_port: int, acc_sender: str, acc_password: str):
        """Initialize the SMTP server settings and credentials.

        Args:
            srv_name (str): Server address (e.g., ``'smtp.office365.com'``).
            srv_port (int): Server port (e.g., ``587`` for TLS or ``465`` for SSL).
            acc_sender (str): The authenticated sender email address.
            acc_password (str): The account password or App Password.
        """
        self._srv_name = srv_name
        self._srv_port = srv_port
        self._acc_sender = acc_sender
        self._acc_password = acc_password

    def send(self, recipient: Union[str, list], subject: str, body: str, cc: Union[str, list] = None, bcc: Union[str, list] = None, attachments: Union[str, list] = None, is_html: bool = True) -> bool:
        """Execute a comprehensive email transmission with lazy-loaded dependencies.

        Handles ``To``, ``Cc``, and ``Bcc`` addressing logic, automatic MIME creation 
        for attachments, and secure delivery via SSL or STARTTLS based on port.

        Args:
            recipient (str | list): Primary ``"To"`` recipient(s).
            subject (str): The subject line of the email.
            body (str): The content/body of the email.
            cc (str | list, optional): Carbon Copy recipients (visible to all).
            bcc (str | list, optional): Blind Carbon Copy recipients (hidden).
            attachments (str | list, optional): Absolute file path(s) to attach.
            is_html (bool): Renders body as HTML if ``True``. Defaults to ``True``.

        Returns:
            ``True`` if the email was sent successfully, ``False`` otherwise.
        """
        # --- Method-Level Lazy Imports ---
        import smtplib
        import ssl
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email.mime.text import MIMEText
        from email.utils import formatdate
        from email import encoders
        from pathlib import Path
        # NOTE: If your organization uses self-signed certificates, consider passing a 
        # custom SSL context to server_class() instead of globally disabling verification.

        # 1. Normalize Address Inputs
        def _to_list(addr):
            if not addr: return []
            return [addr] if isinstance(addr, str) else addr

        list_to = _to_list(recipient)
        list_cc = _to_list(cc)
        list_bcc = _to_list(bcc)
        all_envelope_recipients = list_to + list_cc + list_bcc

        if not all_envelope_recipients:
            return False

        # 2. Build MIME Container
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self._acc_sender
        msg['To'] = ", ".join(list_to)
        if list_cc:
            msg['Cc'] = ", ".join(list_cc)
        msg['Date'] = formatdate(localtime=True)

        # Attach Body
        msg.attach(MIMEText(body, 'html' if is_html else 'plain'))

        # 3. Process Attachments
        if attachments:
            file_list = [attachments] if isinstance(attachments, str) else attachments
            for file_path in file_list:
                path = Path(file_path)
                if path.is_file():
                    try:
                        with open(path, "rb") as f:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f"attachment; filename={path.name}")
                        msg.attach(part)
                    except Exception as e:
                        print(f"Warning: Failed to attach {path.name}: {e}")

        # 4. Secure Transmission
        try:
            context = ssl.create_default_context()
            
            # Use SMTP_SSL for port 465, standard SMTP + STARTTLS for others (like 587)
            if self._srv_port == 465:
                server_class = smtplib.SMTP_SSL
            else:
                server_class = smtplib.SMTP

            with server_class(self._srv_name, self._srv_port) as server:
                if self._srv_port != 465:
                    server.starttls(context=context)
                
                server.login(self._acc_sender, self._acc_password)
                server.sendmail(self._acc_sender, all_envelope_recipients, msg.as_string())
            
            return True
        except Exception as e:
            print(f"Email Error: {e}")
            return False


class EmailMsal: # noqa: D301
    """Send emails using Microsoft Graph API (OAuth 2.0/MSAL) with persistent authentication.

    Uses the Microsoft Authentication Library (MSAL) to acquire tokens 
    from Azure AD and sends emails via the Graph API REST endpoint. Ideal for 
    applications registered in Azure that require modern authentication (OAuth 2.0).

    **Summary of Methods**

    =========================   ========================================================================
    **Method**                  **Description**
    -------------------------   ------------------------------------------------------------------------
    :meth:`.send`               The primary interface for sending Graph API emails with CC, BCC, and files.
    =========================   ========================================================================

    Args:
        tenant_id (str): Azure AD tenant ID (Directory ID).
        client_id (str): Azure AD application (Client) ID.
        client_secret (str): Azure AD application client secret.
        client_email (str): The mailbox address used to send the email.

    .. code-block:: python

        USAGE EXAMPLE:

        from ntsm.lib import EmailMsal
        
        # 1. Initialize with Azure App Registration details
        ms_mailer = EmailMsal(
            tenant_id='your-tenant-id',
            client_id='your-client-id',
            client_secret='your-secret',
            client_email="automation@nt.org.uk"
        )
        
        # 2. Send complex email with multiple recipients and attachments
        ms_mailer.send(
            recipient=['manager@nt.org.uk', 'lead@nt.org.uk'],
            subject="Automated Azure Report",
            body="<h1>Task Complete</h1><p>The Graph API transmission was successful.</p>",
            cc=['supervisor@nt.org.uk'],
            bcc='audit_archive@nt.org.uk',
            attachments=['C:/Reports/Audit.pdf'],
            is_html=True
        )
    """

    def __init__(self, tenant_id: str, client_id: str, client_secret: str, client_email: str):
        """Initialize Azure AD credentials and set the authority endpoint.

        Args:
            tenant_id (str): Azure AD tenant ID.
            client_id (str): Azure AD application (Client) ID.
            client_secret (str): Azure AD application client secret.
            client_email (str): The mailbox address used to send email.
        """
        self._tenant_id = tenant_id
        self._client_id = client_id
        self._client_secret = client_secret
        self._client_email = client_email
        self._authority = f"https://login.microsoftonline.com/{self._tenant_id}"
        self._scopes = ["https://graph.microsoft.com/.default"]

    def _get_access_token(self) -> str:
        """Acquire a bearer token from Azure AD using the client credentials flow (Lazy Load).

        Returns:
            A valid access token for Microsoft Graph API.

        Raises:
            Exception: If token acquisition fails.
        """
        try:
            import msal
        except ImportError:
            raise ImportError(
                "The 'msal' library is not installed. "
                "Please install it using 'pip install msal' to use this method."
            )
        
        app = msal.ConfidentialClientApplication(
            self._client_id,
            authority=self._authority,
            client_credential=self._client_secret
        )                

        result = app.acquire_token_for_client(scopes=self._scopes)
        
        if "access_token" in result:
            return result["access_token"]
        else:
            raise Exception(f"MSAL Token Failure: {result.get('error_description')}")

    def send(self, recipient: Union[str, list], subject: str, body: str, cc: Union[str, list] = None, bcc: Union[str, list] = None, attachments: Union[str, list] = None, is_html: bool = True) -> bool:
        """Execute an email transmission via Microsoft Graph API (Lazy Load).

        Handles OAuth 2.0 token acquisition, MIME-to-JSON conversion for 
        attachments, and RESTful delivery through the Graph API endpoint.

        Args:
            recipient (str | list): Primary ``"To"`` recipient(s).
            subject (str): The subject line of the email.
            body (str): The content/body of the email.
            cc (str | list, optional): Carbon Copy recipients (visible to all).
            bcc (str | list, optional): Blind Carbon Copy recipients (hidden).
            attachments (str | list, optional): Absolute file path(s) to attach.
            is_html (bool): Renders body as HTML if ``True``. Defaults to ``True``.

        Returns:
            ``True`` if the Graph API accepted the message (HTTP 202), ``False`` otherwise.
        """
        
        try:
            import requests
        except ImportError:
            raise ImportError(
                "The 'requests' library is not installed. "
                "Please install it using 'pip install requests' to use this method."
            )
        import base64

        # 1. Normalize Addresses for JSON Structure
        def _to_recipient_dict(addr):
            if not addr: return []
            addrs = [addr] if isinstance(addr, str) else addr
            return [{"emailAddress": {"address": a}} for a in addrs]

        # 2. Build Graph API JSON Payload
        email_data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML" if is_html else "Text", 
                    "content": body
                },
                "toRecipients": _to_recipient_dict(recipient),
                "ccRecipients": _to_recipient_dict(cc),
                "bccRecipients": _to_recipient_dict(bcc),
                "attachments": []
            }
        }
        
        # 3. Process Attachments
        if attachments:
            file_list = [attachments] if isinstance(attachments, str) else attachments
            for file_path in file_list:
                path = Path(file_path)
                if path.is_file():
                    try:
                        with open(path, 'rb') as f:
                            content_bytes = base64.b64encode(f.read()).decode('utf-8')
                        
                        email_data["message"]["attachments"].append({
                            "@odata.type": "#microsoft.graph.fileAttachment",
                            "name": path.name,
                            "contentType": "application/octet-stream",
                            "contentBytes": content_bytes
                        })
                    except Exception as e:
                        print(f"Warning: Failed to encode attachment {path.name}: {e}")

        # 4. Payload Size Check (Graph API Payload limit is 4MB for simple send)
        total_payload_size = len(json.dumps(email_data))
        if total_payload_size > 4 * 1024 * 1024:
            print(f"Warning: Total email payload size ({total_payload_size / 1024 / 1024:.2f}MB) exceeds 4MB limit.")
            print("Consider sending smaller attachments or using the large-file upload session API.")

        # 5. Authenticate and Post
        try:
            token = self._get_access_token()
            endpoint = f"https://graph.microsoft.com/v1.0/users/{self._client_email}/sendMail"
            headers = {
                "Authorization": f"Bearer {token}", 
                "Content-Type": "application/json"
            }
            
            response = requests.post(endpoint, json=email_data, headers=headers)
            
            if response.status_code == 202:
                return True
            else:
                print(f"Graph API Error ({response.status_code}): {response.text}")
                return False
        except Exception as e:
            print(f"Transmission Error: {e}")
            return False


class Files: # noqa: D301
    """A high-performance utility class for robust file and directory management.

    The ``Files`` class provides a suite of static methods designed for production-grade 
    automation, specifically optimized for GIS (Esri FGDB) workflows and large-scale 
    data synchronization. It handles common failure points such as file locks, 
    interrupted transfers, and directory-level verification.

    **Summary of Methods**

    ===================================  ======================================================================
    **Method**                           **Description**
    -----------------------------------  ----------------------------------------------------------------------
    :meth:`.copy_dir`                    Syncs directories with resume logic and size-based verification.
    :meth:`.rem_files`                   Purges files based on age, extension, and recursion.
    :meth:`.files_path_as_list`          Generates filtered lists of absolute file paths.
    :meth:`.rem_files_from_list`         Iterates and deletes a provided list of file paths.
    :meth:`.write_to_file`               Saves a string to a file, ensuring parent directories exist.
    :meth:`.append_to_file`              Appends text content to the end of an existing file.
    :meth:`.file_to_type`                Parses files into dictionaries, JSON, or dot-notation objects.
    :meth:`.get_dir_size`                High-speed byte-size calculation for directories.
    :meth:`.append_dict_to_csv`          Appends data to CSV with automated header/encoding management.
    :meth:`.erase_if_exists`             Removal of files or folders with retry logic.
    :meth:`.file_exists`                 High-speed specific validation of file existence.
    ===================================  ======================================================================

    .. code-block:: python

        USAGE EXAMPLE:

        from ntsm.lib import Files

        # 1. Sync a 30GB Geodatabase (Silent, Resume-capable)
        dest = Files.copy_dir("C:/Data/Project.gdb", "D:/Backups")

        # 2. Cleanup old logs (Older than 30 days, specific extensions)
        Files.rem_files("C:/Logs", max_days=30, file_exts=['log', 'tmp'], recursive=True)

        # 3. Safe removal of a scratch directory
        Files.erase_if_exists("C:/Temp/scratch_workspace", retries=5)

    """

    @staticmethod
    def rem_files(dir_path: str, max_days: int = 0, file_exts: Optional[List[str]] = None, recursive: bool = False) -> None:
        """Remove files from a directory with advanced filtering.

        Manages storage by purging old files. Can target specific file extensions
        and search recursively through subdirectories.

        Args:
            dir_path (str): The full path to the directory to clean.
            max_days (int): Only delete files older than this many days.
                Defaults to ``0`` (deletes all matching files).
            file_exts (list, optional): Filter by extensions (e.g., ``['log', 'tmp']``).
                If ``None``, all file types are considered.
            recursive (bool): If ``True``, searches subdirectories. Defaults to ``False``.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.lib import Files

            # Clean all .log and .txt files older than 7 days
            Files.rem_files(
                dir_path="C:/Project/logs", 
                max_days=7, 
                file_exts=['log', 'txt'], 
                recursive=True
            )

        Raises:
            NotADirectoryError: If the provided ``dir_path`` does not exist.
        """

        root_dir = Path(dir_path)
        if not root_dir.is_dir():
            raise NotADirectoryError(f"Directory not found: {dir_path}")

        cutoff_date = datetime.now() - timedelta(days=max_days)

        # Pre-process extensions: ensure they start with a dot for endswith()
        if file_exts:
            # Convert ['log'] to ('.log',) to be safe
            valid_exts = tuple(ext if ext.startswith('.') else f'.{ext}' for ext in file_exts)
        else:
            valid_exts = "" # endswith("") always returns True

        search_pattern = "**/*" if recursive else "*"

        for file_path in root_dir.glob(search_pattern):
            if not file_path.is_file():
                continue

            # Case-insensitive extension check
            if not file_path.suffix.lower().endswith(valid_exts):
                continue

            # Filter by time
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mtime <= cutoff_date:
                try:
                    file_path.unlink()
                except OSError as e:
                    print(f"Permission denied or error deleting {file_path}: {e}")

    @staticmethod
    def files_path_as_list(dir_path: str, file_exts: Optional[List[str]] = None, recursive: bool = False) -> List[str]:
        """Generate a list of full file paths from a directory with advanced filtering.

        Scans a directory and returns a list of paths, optionally filtering
        by file extensions and searching through subdirectories.

        Args:
            dir_path (str): The full path to the target directory.
            file_exts (list, optional): Filter by extensions (e.g., ``['csv', 'xlsx']``).
                If ``None``, all file types are returned.
            recursive (bool): If ``True``, performs a recursive search. Defaults to ``False``.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.lib import Files
            
            # Get all PDF and DOCX files in a folder
            my_files = Files.files_path_as_list("C:/Docs", file_exts=['pdf', 'docx'])

        Returns:
            A list of absolute file paths as strings.

        Raises:
            NotADirectoryError: If the provided ``dir_path`` is invalid.
        """
        
        root = Path(dir_path)
        if not root.is_dir():
            raise NotADirectoryError(f"Directory not found: {dir_path}")

        # Standardize extensions: ensure they start with dots
        if file_exts:
            valid_exts = tuple(ext if ext.startswith('.') else f'.{ext}' for ext in file_exts)
        else:
            valid_exts = "" # endswith("") returns True for all

        # Define search pattern
        pattern = "**/*" if recursive else "*"
        
        # Build the list using a list comprehension for better performance
        file_list = [
            str(p.absolute()) 
            for p in root.glob(pattern) 
            if p.is_file() and p.name.lower().endswith(valid_exts)
        ]

        return file_list

    @staticmethod
    def rem_files_from_list(file_paths: List[str]) -> None:
        """Iterate through a list of file paths and delete each file.

        Designed to work seamlessly with the output of :meth:`.files_path_as_list_adv`.
        Includes safety checks to ensure the file exists before attempting deletion.

        Args:
            file_paths (list): A list of absolute file paths to be removed.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.lib import Files
            
            # Get and then delete a list of temp files
            tmp_files = Files.files_path_as_list("./temp", file_exts=['tmp'])
            Files.rem_files_from_list(file_paths=tmp_files)

        Raises:
            OSError: If a file cannot be deleted due to system permissions.
        """
        
        if not file_paths:
            return

        for path in file_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError as e:
                    print(f"Error: Could not delete {path}. Reason: {e}")

    @staticmethod
    def write_to_file(content: str, file_path: str) -> None:
        """Save a string to a text file, overwriting any existing content.

        Ensures the target directory exists before writing and 
        uses UTF-8 encoding. If the file does not exist, it will be created.

        Args:
            content (str): The text content to be saved.
            file_path (str): The full destination path for the file.

        Raises:
            OSError: If the file cannot be written due to disk or permission issues.

        .. code-block:: python

            USAGE EXAMPLE:

            Files.write_to_file(report, "./output/report.txt")

        """
        
        if not isinstance(content, str) or not isinstance(file_path, str):
            raise TypeError("Both 'content' and 'file_path' must be strings.")

        # Ensure the directory exists so we don't crash
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise OSError(f"Failed to write to {file_path}: {e}")

    @staticmethod
    def append_to_file(content: str, file_path: str) -> None:
        """Append new text content to the end of an existing file.

        Adds a string to the current EOF without modifying existing data.
        Requires the file to already exist to prevent accidental file creation.

        Args:
            content (str): The text content to append.
            file_path (str): The full path to the existing file.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.lib import Files
            # Add a new entry to an existing log
            Files.append_to_file("New entry: Processing step 2 completed.", "./logs/audit.log")

        Raises:
            FileNotFoundError: If the specified ``file_path`` does not exist.
            OSError: If the file cannot be written to due to permissions.
        """
        
        if not isinstance(content, str) or not isinstance(file_path, str):
            raise TypeError("Both 'content' and 'file_path' must be strings.")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Cannot append to non-existent file: {file_path}")

        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise OSError(f"Failed to append data to {file_path}: {e}")

    @staticmethod
    def file_to_type(file_path: str, output_type: Literal["dict", "json", "obj"] = "dict") -> Any:
        """Read a file and convert its content to a specific Python data structure.

        Supports parsing standard Python literals, JSON strings, and converting
        the result into a dot-accessible object (``SimpleNamespace``).

        Args:
            file_path (str): The full path to the file to be read.
            output_type (str): Defines how the content is parsed:

                * ``"dict"``: Parses Python literals using ``ast.literal_eval``.
                * ``"json"``: Parses content as standard JSON.
                * ``"obj"``: Parses and converts to a recursive ``SimpleNamespace``.

                Defaults to ``"dict"``.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.lib import Files
            
            # Read a Python dictionary file
            data = Files.file_to_type("config.txt", output_type="dict")
            
            # Read a JSON file as an object for dot-notation access
            config = Files.file_to_type("settings.json", output_type="obj")
            print(config.database.port)

        Returns:
            The parsed content in the requested format.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file content is not valid for the requested type.
        """
        
        import ast
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"The file does not exist: {file_path}")

        try:
            content = path.read_text(encoding='utf-8')

            # 1. Parse content based on type
            if output_type == "json":
                data = json.loads(content)
            else:
                # ast.literal_eval is safer than eval() for dict strings
                data = ast.literal_eval(content)

            # 2. Handle object conversion if requested
            if output_type == "obj":
                # Using the recursive dict_to_ns logic we discussed
                from ntsm.lib import dict_to_ns 
                return dict_to_ns(data)
            
            return data

        except (ValueError, SyntaxError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to parse {file_path} as {output_type}: {e}")
        except Exception as e:
            raise OSError(f"Error reading {file_path}: {e}")

    @staticmethod
    def get_dir_size(path: Union[str, Path], recursive: bool = True) -> int:
        """Calculate the total size of a directory in bytes.

        High-speed scan primarily used for pre-copy estimation and post-copy
        verification to ensure data integrity in large-scale file transfers.

        Args:
            path (str | Path): The path to the directory.
            recursive (bool): If ``True``, includes all subdirectories. Defaults to ``True``.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.lib import Files
            from pathlib import Path
            
            size_bytes = Files.get_dir_size("C:/Data/Production.gdb")
            size_gb = size_bytes / (1024**3)
            print(f"Total size: {size_gb:.2f} GB")

        Returns:
            Total size in bytes. Returns ``0`` if the path does not exist.
        """
        folder = Path(path)
        if not folder.is_dir():
            return 0

        pattern = "**/*" if recursive else "*"
        # Generator expression for memory efficiency on large file counts
        return sum(f.stat().st_size for f in folder.glob(pattern) if f.is_file())
    
    @staticmethod
    def copy_dir(source: str, destination: str, overwrite: bool = True, recursive: bool = True, retries: int = 3, verify: bool = True, debug: bool = False) -> str:
        """Copy a directory with resume capability, fail-over, and size-based verification.

        Optimized for large structures like Esri FGDBs. Allows resuming interrupted
        transfers by comparing file sizes and timestamps, ensuring data integrity
        without unnecessary re-copying of existing data.

        Args:
            source (str): The full path of the source folder to copy.
            destination (str): The parent directory where the copy will be saved.
            overwrite (bool): If ``True``, wipes the destination before starting. Defaults to ``True``.
            recursive (bool): If ``True``, copies all subdirectories. Defaults to ``True``.
            retries (int): Number of attempts per file if locks are found. Defaults to ``3``.
            verify (bool): Performs a final byte-size comparison. Defaults to ``True``.
            debug (bool): If ``True``, prints progress and status updates. Defaults to ``False``.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.lib import Files
            
            # Copy directory with all subfolders, without overwriting 
            # existing data, and verify the copy
            new_path = Files.copy_dir(
                source="C:/Data/Project.gdb", 
                destination="D:/Backups",
                overwrite=False
            )

        Returns:
            The absolute path to the synced destination folder.

        Raises:
            FileNotFoundError: If the source path does not exist.
            OSError: If verification fails or files remain locked after retries.
        """
        
        src_path = Path(source)
        if not src_path.is_dir():
            raise FileNotFoundError(f"Source directory not found: {source}")

        final_dest = Path(destination) / src_path.name

        # 1. Handle Overwrite
        if final_dest.exists() and overwrite:
            try:
                shutil.rmtree(final_dest)
            except OSError as e:
                raise OSError(f"Could not remove existing destination {final_dest}: {e}")

        final_dest.mkdir(parents=True, exist_ok=True)

        # 2. Pre-scan logic - Only calculate total size if needed for Progress or Verify
        search_pattern = "**/*" if recursive else "*"
        items_to_copy = list(src_path.glob(search_pattern))
        
        total_size_bytes = 0
        if debug or verify:
            total_size_bytes = Files.get_dir_size(src_path, recursive)
        
        processed_size = 0
        last_print_time = time.time()

        if debug:
            size_gb = total_size_bytes / (1024**3)
            print(f"Starting copy: {src_path.name} ({size_gb:.2f} GB)")

        # 3. Iterate and Sync
        for item in items_to_copy:
            rel_path = item.relative_to(src_path)
            dest_item = final_dest / rel_path

            if item.is_dir():
                if recursive:
                    dest_item.mkdir(exist_ok=True)
                continue

            item_stat = item.stat()
            item_size = item_stat.st_size

            # 4. Resume Logic: Size + Timestamp check
            if dest_item.exists():
                dest_stat = dest_item.stat()
                if dest_stat.st_size == item_size and \
                   abs(dest_stat.st_mtime - item_stat.st_mtime) < 1:
                    processed_size += item_size
                    continue

            # 5. Granular Fail-over
            for attempt in range(retries):
                try:
                    shutil.copy2(item, dest_item)
                    processed_size += item_size
                    break 
                except (OSError, IOError) as e:
                    if attempt < retries - 1:
                        time.sleep(2)
                    else:
                        raise OSError(f"Failed to copy {item} after {retries} attempts: {e}")

            # 6. Progress Tracking (Conditional on Debug)
            if debug:
                current_time = time.time()
                if current_time - last_print_time >= 3:
                    pct = (processed_size / total_size_bytes * 100) if total_size_bytes > 0 else 100
                    curr_gb = processed_size / (1024**3)
                    total_gb = total_size_bytes / (1024**3)
                    print(f"progress: {pct:.1f}% | {curr_gb:.2f} / {total_gb:.2f} GB processed...")
                    last_print_time = current_time

        # 7. Final Size-Based Verification
        if verify:
            dest_size = Files.get_dir_size(final_dest, recursive)
            if total_size_bytes != dest_size:
                raise OSError(f"Verification Failed: Source ({total_size_bytes}b) != Dest ({dest_size}b)")
        
        if debug:
            print(f"Copy Successful: {final_dest.name} is verified.")
            
        return str(final_dest.absolute())
    
    @staticmethod
    def append_dict_to_csv(csv_path: str, data_dict: dict, field_names: list) -> None:
        """Append a dictionary as a new row to a CSV file, adding a header if needed.

        Uses ``csv.DictWriter`` to ensure data is mapped correctly to columns.
        If newly created, automatically writes field names as the first row (header).

        Args:
            csv_path (str): The full path to the CSV file.
            data_dict (dict): The data to append (keys must match ``field_names``).
            field_names (list): A list of strings defining the CSV column order.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.lib import Files
            
            fields = ['timestamp', 'status', 'user']
            entry = {'timestamp': '2026-02-17', 'status': 'Success', 'user': 'Admin'}
            
            Files.append_dict_to_csv("log.csv", entry, fields)

        Raises:
            OSError: If the file is locked or the path is invalid.
        """
        import csv

        # Ensure the directory exists
        parent_dir = os.path.dirname(csv_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        # Check if we need to write a header (file is new or empty)
        write_header = not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0

        try:
            # utf-8-sig ensures Excel opens the CSV with correct encoding
            with open(csv_path, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=field_names)
                
                if write_header:
                    writer.writeheader()
                
                writer.writerow(data_dict)
        except Exception as e:
            raise OSError(f"Failed to append row to CSV {csv_path}: {e}")
            
    @staticmethod
    def erase_if_exists(path: str, retries: int = 3, debug: bool = False) -> bool:
        """Remove a file or an entire directory tree if it exists on the system.

        Identifies whether the target is a file or directory and applies the
        appropriate removal command. Includes a retry mechanism to handle
        temporary file locks common in GIS workflows.

        Args:
            path (str): The absolute path to the file or directory.
            retries (int): Number of attempts if the path is locked. Defaults to ``3``.
            debug (bool): If ``True``, prints status updates on removal. Defaults to ``False``.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.lib import Files
            
            # Silently and safely remove a temp folder or file
            Files.erase_if_exists("C:/Temp/scratch.gdb")

        Returns:
            ``True`` if the path was removed or did not exist, ``False`` if removal failed.
        """
        target = Path(path)
        if not target.exists():
            if debug:
                print(f"Erase skipped: {path} does not exist.")
            return True

        for attempt in range(retries):
            try:
                if target.is_file() or target.is_symlink():
                    target.unlink()
                elif target.is_dir():
                    shutil.rmtree(target)
                
                if debug:
                    print(f"Successfully erased: {path}")
                return True

            except OSError as e:
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                else:
                    if debug:
                        print(f"Error: Failed to erase {path}. Reason: {e}")
                    return False
        return False
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """Verify if a specific file exists and is accessible on the system.

        Unlike a general path check, this specifically validates that 
        the target is a file (not a directory). Designed for high-speed 
        validation within complex production pipelines.

        Args:
            file_path (str): The absolute or relative path to the file.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.lib import Files
            
            if Files.file_exists("C:/Config/settings.json"):
                # Proceed with processing
                pass

        Returns:
            ``True`` if the file exists and is a file; ``False`` otherwise.
        """
        if not file_path:
            return False
            
        return os.path.isfile(file_path)

    
class Archive: # noqa: D301
    """A professional utility class for managing file archives and compression.

    The ``Archive`` class provides robust, production tools for creating and 
    extracting ZIP archives. It features advanced filtering by file age, size, 
    and extension, and includes secure password support for encrypted archives.

    **Summary of Methods**

    =============================  ========================================================================
    **Method**                     **Description**
    -----------------------------  ------------------------------------------------------------------------
    :meth:`.make_zip`              Unified archive tool with size/age filtering and source cleanup.
    :meth:`.un_zip`                Extracts ZIP archives with password support and auto-folder creation.
    :meth:`.rem_zip`               Advanced purge tool for ZIPs based on age and size thresholds.
    =============================  ========================================================================

    .. code-block:: python

        USAGE EXAMPLE:

        from ntsm.lib import Archive

        # 1. Archive a directory (only .csv files) and delete source after success
        Archive.make_zip(
            source='C:/Data/Logs', 
            archive_name='Log_Backup',
            file_exts=['csv'],
            delete_source=True
        )

        # 2. Archive a single file only if it exceeds 5MB
        Archive.make_zip(
            source='C:/Temp/report.pdf', 
            max_size_mb=5.0,
            add_timestamp=True
        )

        # 3. Unzip a password-protected archive
        Archive.un_zip(
            zip_path='C:/Backups/SecureData.zip', 
            password='MySecretPassword'
        )

        # 4. Clean up: Delete ZIPs older than 30 days OR larger than 1GB
        Archive.rem_zip('C:/Backups', max_days=30, min_size_mb=1024.0)

    """
    
    @staticmethod
    def make_zip(source: str, dest_path: str = None, archive_name: str = None, add_timestamp: bool = False, password: str = None, max_days: int = 0, max_size_mb: float = 0, file_exts: Optional[List[str]] = None, delete_source: bool = False, debug: bool = False) -> str:
        """Create a compressed ZIP archive with advanced size, age, and type filtering.

        Handles archiving for both directories and individual files. 
        If the source is a directory and ``delete_source`` is ``True``, the entire 
        directory is removed after a successful ZIP operation.

        Args:
            source (str): The file or directory path to archive.
            dest_path (str, optional): Directory where the ZIP will be saved.
                Defaults to the source's parent location.
            archive_name (str, optional): ZIP filename (no extension).
                Defaults to the source name.
            add_timestamp (bool): If ``True``, appends ``YYYYMMDD_HHMMSS`` to the name.
            password (str, optional): Applies a password to the ZIP archive.
            max_days (int): Only archive files modified X+ days ago.
            max_size_mb (float): Only archive if file (or total) exceeds X MB.
            file_exts (list, optional): Filter by extensions (e.g., ``['log', 'txt']``).
            delete_source (bool): Deletes the source (file or directory) after compression.
            debug (bool): If ``True``, prints processing status.

        .. code-block:: python

            USAGE EXAMPLES:

            from ntsm.lib import Archive

            # 1. Archive a directory of old logs and delete the source folder
            Archive.make_zip(
                source="C:/Project/Logs",
                dest_path="D:/Backups",
                max_days=30,
                file_exts=['log'],
                delete_source=True
            )

            # 2. Archive a single large file only if it exceeds 100MB
            Archive.make_zip(
                source="C:/Data/heavy_output.csv",
                archive_name="HeavyData_Backup",
                add_timestamp=True,
                max_size_mb=100.0,
                delete_source=True
            )

        Returns:
            The absolute path to the created ZIP archive, or an empty string if skipped.
        """
        
        try:
            import pyzipper
        except ImportError:
            if password:
                raise ImportError(
                    "Password-protected ZIP archives require the 'pyzipper' library. "
                    "Please install it using 'pip install pyzipper' to use this method."
                )
        import zipfile
        
        src_path = Path(source)
        if not src_path.exists():
            raise FileNotFoundError(f"Source not found: {source}")

        # 1. Resolve Destination and Filename
        target_dir = Path(dest_path) if dest_path else src_path.parent
        target_dir.mkdir(parents=True, exist_ok=True)
        
        base_name = archive_name if archive_name else src_path.stem
        if add_timestamp:
            base_name = f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        zip_fp = target_dir / f"{base_name}.zip"

        # 2. Filter Setup
        cutoff_date = datetime.now() - timedelta(days=int(max_days))
        valid_exts = tuple(ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
                           for ext in file_exts) if file_exts else ""
        
        files_to_zip = []
        
        # 3. Collect Files
        if src_path.is_file():
            files_to_zip.append(src_path)
        else:
            for item in src_path.rglob("*"):
                if item.is_file() and item != zip_fp:
                    files_to_zip.append(item)

        # 4. Filter Implementation
        filtered_files = []
        for f in files_to_zip:
            if valid_exts and not f.suffix.lower().endswith(valid_exts):
                continue
            if datetime.fromtimestamp(f.stat().st_mtime) > cutoff_date:
                continue
            filtered_files.append(f)

        if not filtered_files:
            return ""

        # 5. Threshold Validation
        total_size_mb = sum(f.stat().st_size for f in filtered_files) / (1024 * 1024)
        if total_size_mb < max_size_mb:
            if debug:
                print(f"Skipping: Total size ({total_size_mb:.2f} MB) < threshold ({max_size_mb} MB)")
            return ""

        # 6. Archive Execution
        try:
            if password:
                # Use AESZipFile for strong encryption
                with pyzipper.AESZipFile(zip_fp, 'w', compression=pyzipper.ZIP_LZMA) as zw:
                    # Set encryption parameters before writing
                    zw.setpassword(password.encode('utf-8'))
                    zw.setencryption(pyzipper.WZ_AES, nbits=256)
                    
                    for f in filtered_files:
                        arc_path = f.relative_to(src_path) if src_path.is_dir() else f.name
                        # Files are now encrypted as they are written
                        zw.write(f, arcname=arc_path)
            else:
                # Standard ZIP for public files (no external library needed)
                with zipfile.ZipFile(zip_fp, 'w', zipfile.ZIP_DEFLATED) as zw:
                    for f in filtered_files:
                        arc_path = f.relative_to(src_path) if src_path.is_dir() else f.name
                        zw.write(f, arcname=arc_path)
            
            if debug:
                print(f"Archive created: {zip_fp}")

            # 7. Comprehensive Cleanup
            if delete_source:
                import shutil
                if src_path.is_file():
                    src_path.unlink()
                else:
                    shutil.rmtree(src_path, ignore_errors=True)

        except ImportError:
            raise ImportError("Please install pyzipper to use password protection: pip install pyzipper")
        except Exception as e:
            raise OSError(f"Archive creation failed: {e}")

        return str(zip_fp.absolute())

    
    @staticmethod
    def rem_zip(zip_path: str, max_days: int = 0, min_size_mb: float = 0, recursive: bool = False, debug: bool = False) -> List[str]:
        """Erase ZIP archives from a directory based on age OR size criteria.

        Priority logic:

        1. If both ``max_days`` and ``min_size_mb`` are ``0``, every ZIP is deleted.
        2. If only ``max_days`` > 0, deletes ZIPs older than X days.
        3. If only ``min_size_mb`` > 0, deletes ZIPs larger than X MB.
        4. If both are > 0, deletes if **either** condition is met.

        Args:
            zip_path (str): Directory path containing ZIP archives.
            max_days (int): Delete ZIPs older than X days. Defaults to ``0``.
            min_size_mb (float): Delete ZIPs larger than X MB. Defaults to ``0``.
            recursive (bool): If ``True``, searches subdirectories for ZIPs.
            debug (bool): If ``True``, prints the paths of deleted files.

        .. code-block:: python

            USAGE EXAMPLES:

            from ntsm.lib import Archive

            # Delete EVERY zip in the folder
            Archive.rem_zip("C:/Temp/Zips")

            # Delete if older than 7 days OR larger than 100MB
            Archive.rem_zip("C:/Backups", max_days=7, min_size_mb=100.0)

        Returns:
            A list of absolute paths that were successfully removed.
        """
        
        target_dir = Path(zip_path)
        if not target_dir.is_dir():
            raise NotADirectoryError(f"Directory not found: {zip_path}")

        # 1. Setup Filters
        cutoff_date = datetime.now() - timedelta(days=int(max_days))
        deleted_files = []
        
        # 2. Define Search Pattern
        search_pattern = "**/*.zip" if recursive else "*.zip"
        
        # 3. Iterate and Remove
        for zip_file in target_dir.glob(search_pattern):
            try:
                stats = zip_file.stat()
                
                # Logic
                meets_age = (datetime.fromtimestamp(stats.st_mtime) <= cutoff_date) if max_days > 0 else False
                meets_size = (stats.st_size / (1024 * 1024) >= min_size_mb) if min_size_mb > 0 else False
                
                # Final Trigger: [Both are 0 (Delete All)] OR [Age condition met] OR [Size condition met]
                if (max_days == 0 and min_size_mb == 0) or (meets_age or meets_size):
                    zip_file.unlink()
                    deleted_files.append(str(zip_file.absolute()))
                    
                    if debug:
                        print(f"Deleted: {zip_file.name}")
                        
            except OSError as e:
                if debug:
                    print(f"Failed to delete {zip_file}: {e}")
                continue

        return deleted_files                                    
    
    
    @staticmethod
    def un_zip(zip_path: str, unzip_path: str = None, password: str = None, debug: bool = False) -> str:
        """Extract a ZIP archive to a specified directory with optional password support.

        Args:
            zip_path (str): Absolute path to the ``.zip`` file.
            unzip_path (str, optional): Directory where files will be extracted.
                If ``None``, creates a folder named after the ZIP in the same directory.
            password (str, optional): Password for encrypted ZIP archives.
            debug (bool): If ``True``, prints extraction status.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.lib import Archive

            # Extract a protected archive to a specific folder
            Archive.un_zip(
                zip_path="C:/Backups/Project.zip", 
                unzip_path="C:/Restored", 
                password="SecurePassword123"
            )

        Returns:
            The absolute path to the directory where files were extracted.

        Raises:
            ValueError: If the file is not a valid ZIP archive.
        """
        
        try:
            import pyzipper
        except ImportError:
            if password:
                raise ImportError(
                    "Extracting password-protected archives requires the 'pyzipper' library. "
                    "Please install it using 'pip install pyzipper' to use this method."
                )
        import zipfile
        
        zip_file = Path(zip_path)
        if not zipfile.is_zipfile(zip_path):
            raise ValueError(f"File is not a valid ZIP archive: {zip_path}")

        # 1. Resolve Extraction Path
        if unzip_path:
            target_dir = Path(unzip_path)
        else:
            # Default: Create a folder with the same name as the zip file
            target_dir = zip_file.parent / zip_file.stem
            
        target_dir.mkdir(parents=True, exist_ok=True)

        # 2. Extract Logic
        try:
            if password:
                # Use pyzipper for AES-protected ZIPs
                with pyzipper.AESZipFile(zip_path, 'r') as arch:
                    arch.setpassword(password.encode('utf-8'))
                    arch.extractall(path=target_dir)
            else:
                # Standard zipfile for non-protected ZIPs
                with zipfile.ZipFile(zip_path, 'r') as arch:
                    arch.extractall(path=target_dir)
                
            if debug:
                print(f"Successfully extracted to: {target_dir}")
                
        except RuntimeError as e:
            if "password" in str(e).lower():
                raise RuntimeError(f"Failed to extract {zip_file.name}: Incorrect or missing password.")
            raise e
        except Exception as e:
            raise OSError(f"Failed to unzip {zip_path}: {e}")

        return str(target_dir.absolute())
    

class Args: # noqa: D301
    """A centralized utility for command-line argument parsing.

    The ``Args`` class provides a pre-configured ``argparse.ArgumentParser`` 
    instance, optimized for GIS and automation scripts. It uses 
    ``RawTextHelpFormatter`` to ensure that multi-line help descriptions 
    and examples are rendered correctly in the console.

    **Summary of Methods**

    =============================  ========================================================================
    **Property / Method**          **Description**
    -----------------------------  ------------------------------------------------------------------------
    :attr:`.parser`                The core ``argparse.ArgumentParser`` instance.
    =============================  ========================================================================

    .. code-block:: python

        USAGE EXAMPLE:

        from ntsm.lib import Args

        # 1. Access the pre-configured parser
        parser = Args.parser

        # 2. Add custom arguments
        parser.add_argument("--t", type=str, choices=['one', 'two', 'three'], default='one', required=True, help="Deployment Type")
        parser.add_argument("--path", type=str, required=True, help="Input directory path")
        parser.add_argument("--force", action='store_true', help="Ignore safety locks")

        # 3. Parse and use
        args = parser.parse_args()
        
        # 4. Read parsed arguments values
        choice = args.t
        path = args.path
        force = args.force
        
        print(f"Running in {choice} mode at {path}")

    """
    import argparse

    # Initialize the parser with professional defaults
    parser = argparse.ArgumentParser(
        description="Argument Parser",
        formatter_class=argparse.RawTextHelpFormatter
    )


class DS: # noqa: D301
    """Advanced utilities for manipulating Python Data Structures.

    Currently focused on high-performance dictionary filtering and sorting, 
    especially for complex dictionaries containing nested lists or tuples.

    **Summary of Methods**

    =============================  ========================================================================
    **Method**                     **Description**
    -----------------------------  ------------------------------------------------------------------------
    :meth:`.filter_by_value`       Filters a dictionary based on equality/inequality of its values.
    :meth:`.filter_by_list_index`  Filters a dictionary of lists based on a specific index and value.
    :meth:`.sort_by_key`           Returns a new dictionary sorted by its keys (Asc/Desc).
    :meth:`.sort_by_value`         Returns a new dictionary sorted by its values (Asc/Desc).
    :meth:`.sort_by_list_index`    Returns a new dictionary sorted by an element within list values (Asc/Desc).
    =============================  ========================================================================

    .. code-block:: python

        USAGE EXAMPLE:

        from ntsm.lib import DS

        # Input: { 'Key': [Val0, Val1, Val2] }
        in_dict = {'ab': ['1', '2', '3'], 
                   'ac': ['4', '5', '6'], 
                   'ad': ['1', '7', '8']}
        
        # 1. Filter dictionary by value at list index 0
        # Get items where index 0 is equal to '1'
        out_dict = DS.filter_by_list_index(in_dict, 0, '1', equal=True)
        # Result: {'ab': [`'1'`, '2', '3'], 'ad': [`'1'`, '7', '8']}
        
        # 2. Filter for inequality
        # Get items where index 0 is NOT '1'
        out_dict = DS.filter_by_list_index(in_dict, 0, '1', equal=False)
        # Result: {'ac': ['4', '5', '6']}
        
        # 3. Sort dictionary by list index 0 (Ascending)
        sorted_dict = DS.sort_by_list_index(in_dict, 0, reverse=False)
        # Result: {'ab': ['1', '2', '3'], 'ad': ['1', '7', '8'], 'ac': ['4', '5', '6']}

    """
    
    
    @staticmethod
    def filter_by_value(dict_in: dict, dict_value: Any, equal: bool = True) -> dict:
        """Filter a dictionary based on a specific value.

        Args:
            dict_in (dict): The dictionary to be filtered.
            dict_value: The value to compare against.
            equal (bool): If ``True``, keeps items that match the value.
                If ``False``, keeps items that do **not** match. Defaults to ``True``.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.lib import DS

            data = {'status': 'active', 'user': 'admin', 'flag': 'active'}

            # Filter for equality
            active_items = DS.filter_by_value(data, 'active')
            # Result: {'status': 'active', 'flag': 'active'}

            # Filter for inequality
            non_active = DS.filter_by_value(data, 'active', equal=False)
            # Result: {'user': 'admin'}

        Returns:
            A new dictionary containing the filtered items.
        """
        if not dict_in:
            return {}

        if equal:
            return {k: v for k, v in dict_in.items() if v == dict_value}
        
        return {k: v for k, v in dict_in.items() if v != dict_value}
    
    
    @staticmethod
    def filter_by_list_index(dict_in: dict, list_idx: int, list_val: Any, equal: bool = True) -> dict:
        """Filter a dictionary where values are lists, based on an item at a specific index.

        Args:
            dict_in (dict): Dictionary where values are lists.
            list_idx (int): The index within the list to check.
            list_val: The value to compare against.
            equal (bool): If ``True``, returns items where ``list[idx] == list_val``.
                If ``False``, returns items where ``list[idx] != list_val``. Defaults to ``True``.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.lib import DS

            # Data: { 'ID': [Name, Status, Priority] }
            data = {
                101: ['Task_A', 'Active', 1],
                102: ['Task_B', 'Pending', 2],
                103: ['Task_C', 'Active', 3]
            }

            # Filter where Status (index 1) is 'Active'
            active_tasks = DS.filter_by_list_index(data, 1, 'Active')
            # Result: {101: ['Task_A', 'Active', 1], 103: ['Task_C', 'Active', 3]}

        Returns:
            A new dictionary containing the filtered items.
        """
        if not dict_in:
            return {}

        dict_out = {}
        for k, v in dict_in.items():
            # Safety check: Ensure value is a list/tuple and index exists
            if not isinstance(v, (list, tuple)) or len(v) <= list_idx:
                continue
            
            # Comparison logic
            if equal:
                if v[list_idx] == list_val:
                    dict_out[k] = v
            else:
                if v[list_idx] != list_val:
                    dict_out[k] = v

        return dict_out


    @staticmethod
    def sort_by_key(dict_in: dict, reverse: bool = False) -> dict:
        """Sort a dictionary alphabetically or numerically based on its keys.

        Args:
            dict_in (dict): The dictionary to be sorted.
            reverse (bool): If ``False``, sorts ascending (A-Z, 0-9).
                If ``True``, sorts descending (Z-A, 9-0). Defaults to ``False``.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.lib import DS

            data = {'z': 100, 'a': 5, 'm': 50}

            # Sort Ascending
            sorted_data = DS.sort_by_key(data)
            # Result: {'a': 5, 'm': 50, 'z': 100}

            # Sort Descending
            desc_data = DS.sort_by_key(data, reverse=True)
            # Result: {'z': 100, 'm': 50, 'a': 5}

        Returns:
            A new dictionary with keys in the specified order.
        """
        if not dict_in:
            return {}

        return {k: dict_in[k] for k in sorted(dict_in.keys(), reverse=reverse)}


    @staticmethod
    def sort_by_value(dict_in: dict, reverse: bool = False) -> dict:
        """Sort a dictionary based on its values rather than its keys.

        Args:
            dict_in (dict): The dictionary to be sorted.
            reverse (bool): If ``False``, sorts values ascending.
                If ``True``, sorts values descending. Defaults to ``False``.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.lib import DS

            data = {'Item_A': 50, 'Item_B': 10, 'Item_C': 30}

            # Sort by values (Smallest to Largest)
            sorted_data = DS.sort_by_value(data)
            # Result: {'Item_B': 10, 'Item_C': 30, 'Item_A': 50}

        Returns:
            A new dictionary with items sorted by value.
        """
        if not dict_in:
            return {}

        return dict(sorted(dict_in.items(), key=lambda x: x[1], reverse=reverse))


    @staticmethod
    def sort_by_list_index(dict_in: dict, list_idx: int, reverse: bool = False) -> dict:
        """Sort a dictionary of lists based on an element at a specific index.

        Args:
            dict_in (dict): Dictionary where values are lists or tuples.
            list_idx (int): The index within the list to sort by.
            reverse (bool): If ``False``, sorts ascending. If ``True``, sorts descending.
                Defaults to ``False``.

        .. code-block:: python

            USAGE EXAMPLE:

            from ntsm.lib import DS

            # Data: { 'ID': [Name, Score] }
            data = {
                1: ['User_A', 85],
                2: ['User_B', 92],
                3: ['User_C', 78]
            }

            # Sort by Score (index 1) descending
            leaderboard = DS.sort_by_list_index(data, 1, reverse=True)
            # Result: {2: ['User_B', 92], 1: ['User_A', 85], 3: ['User_C', 78]}

        Returns:
            A new dictionary sorted by the chosen list element.

        Raises:
            ValueError: If values aren't lists or the index is out of range.
        """
        if not dict_in:
            return {}

        try:
            # Sorts using the element at list_idx within each value
            return dict(sorted(dict_in.items(), key=lambda x: x[1][list_idx], reverse=reverse))
        except (IndexError, TypeError) as e:
            raise ValueError(f"Sorting failed: Ensure all dict values are lists of sufficient length. Error: {e}")


