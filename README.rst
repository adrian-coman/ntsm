========================
NTSM - Vault & Utilities
========================

.. image:: https://img.shields.io/pypi/v/ntsm.svg
    :target: https://pypi.org/project/ntsm/
    :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/ntsm.svg
    :target: https://pypi.org/project/ntsm/
    :alt: Supported Python Versions

.. image:: https://readthedocs.org/projects/ntsm/badge/?version=latest
    :target: https://ntsm.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
    :alt: License: MIT


.. image:: https://img.shields.io/badge/status-beta-orange.svg
    :target: https://pypi.org/project/ntsm/
    :alt: Project Status: Beta


The **NTSM** package serves as a central hub for GIS teams, providing a consistent and secure method for managing sensitive credentials across various platforms. Its primary objective is to eliminate hardcoded secrets and unify the connectivity patterns for frequently used APIs like ArcGIS Online or MSAL. 

**Disclaimer & Attribution**
----------------------------
This project is an evolved library that incorporates various third-party code snippets and open-source logic. While primary development and architecture are steered by the author(s), many components have been refined, optimized, and adjusted using different AI agents to meet specific production requirements. 

.. note::
   This package is a **"transition and backward compatibility"** version and not yet a stable release; it should be used with appropriate caution.

Key Features
------------
* **Vault Security**: AES-256-GCM encryption with PBKDF2-HMAC-SHA512 key derivation.
* **Standardized Connections**: Unified interface for ArcGIS, MSAL and more.
* **Productivity Utilities**: Standardized logging, file handling, archiving, and more.

Installation
------------
Install the latest version from PyPI:

.. code-block:: bash

   pip install ntsm

Quick Start
-----------

.. code-block:: python

    from ntsm.conn import vault
    # Initialize vault via environment variable
    v = vault(key_env="GIS_KEY")

    from ntsm.lib import setup_logging
    logger = setup_logging("my_app", "./logs")
    logger.info("Application started")

Module Examples
---------------

Secure Vault (aeadencrypt)
~~~~~~~~~~~~~~~~~~~~~~~~~~
Modern encryption for sensitive data.

.. code-block:: python

    from ntsm.aeadencrypt import VaultCipher
    v = VaultCipher(key_name="MY_KEY")
    encrypted = v.encrypt("secret message")
    decrypted = v.decrypt(encrypted)

    # Legacy AES-128-CBC
    from ntsm.aeadencrypt import VaultUtils
    enc = VaultUtils.encrypt_text("hello", "secret")

Connections (conn)
~~~~~~~~~~~~~~~~~~
Easy access to common services.

.. code-block:: python

    from ntsm.conn import agol, msal

    # ArcGIS Online
    gis = agol(url="https://nt.maps.arcgis.com", user="u", password="p")

    # MSAL Email
    mail = msal(tenant_id="...", client_id="...", client_email="...", client_secret="...")

Library Utilities (lib)
~~~~~~~~~~~~~~~~~~~~~~~
A wide range of helper functions and classes.

.. code-block:: python

    from ntsm.lib import Files, Archive, FormatTime

    # File & Folder management
    Files.copy_dir("src", "dst")
    Archive.make_zip("data")

    # Time helpers
    from datetime import datetime
    t_str = FormatTime.to_str(datetime.now())

Package Structure
-----------------

* **ntsm.aeadencrypt**: ``VaultCipher`` (AES-256-GCM), ``VaultUtils`` (Legacy support).
* **ntsm.conn**: ``vault``, ``agol``, ``token``, ``msal``, and more.
* **ntsm.lib**: ``Email``, ``Files``, ``Archive``, ``setup_logging``, ``timer_wrap``, and more.

Full Documentation
------------------
Access documentation locally or online:

.. code-block:: bash

    # Open the interactive documentation viewer
    ntsmdocs

Online documentation is hosted at `Read the Docs <https://ntsm.readthedocs.io/>`_.

Contact & Support
-----------------
* **Author**: Adrian Coman
* **Email**: adrian.coman@proton.me
* **Project Status**: Beta