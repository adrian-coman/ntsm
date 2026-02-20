Help & Troubleshooting
======================

This document provides guidance on setting up and troubleshooting the NTSM package.

Installation
------------

NTSM can be installed directly from PyPI or from the local repository.

.. code-block:: bash

    # Standard installation
    pip install ntsm

    # Local development installation
    pip install -e .

Package Dependencies
~~~~~~~~~~~~~~~~~~~~
NTSM relies on the following core libraries:

* ``cryptography``: For high-security Vault operations.
* ``requests``: For API connections.
* ``msal``: For Azure/Microsoft authentication.
* ``loguru``: For standardized logging.

**Note:** The ``arcgis`` library is optional but required for ``agol`` and ``token`` connections. Use ``pip install arcgis`` separately if needed.

Secure Vault Setup
------------------

The recommended way to use the Vault is via an environment variable to avoid storing keys in files.

Windows (Cmd)
~~~~~~~~~~~~~
.. code-block:: bat

    set GIS_KEY=your_master_key_here

Windows (PowerShell)
~~~~~~~~~~~~~~~~~~~~
.. code-block:: powershell

    $env:GIS_KEY = "your_master_key_here"

Linux/macOS (Bash)
~~~~~~~~~~~~~~~~~~
.. code-block:: bash

    export GIS_KEY="your_master_key_here"

Common Issues
-------------

ImportError: No module named 'arcgis'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ArcGIS library is large and is not included in the default NTSM installation to keep the package lightweight. 
**Solution:** Run ``pip install arcgis``.

Vault decryption fails
~~~~~~~~~~~~~~~~~~~~~~
* **Cause 1**: The ``GIS_KEY`` environment variable is missing or has an extra newline.
* **Cause 2**: You are using the modern ``VaultCipher`` on a string encrypted with the legacy ``VaultUtils.encrypt_text``.
* **Solution**: Ensure your keys match the cipher type.

Documentation
-------------

To view the complete API reference, use the built-in documentation viewer:

.. code-block:: bash

    ntsmdocs

Support
-------

If you encounter bugs or have suggestions:

1. Check the existing documentation using ``ntsmdocs``.
2. Follow the **Contact & Support** section in the **README** for direct contact details.
