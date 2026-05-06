Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <http://keepachangelog.com/>`_, 
and this project adheres to `Semantic Versioning <http://semver.org/>`_.


0.1.8 (2026-05-06)
------------------
* Added: Detailed documentation and usage examples for ``LazyAttrDict`` class and its methods.
* Added: Public export of ``LazyAttrDict`` in ``lib.__all__``.
* Fixed: Missing type hint imports (``Dict``, ``Iterable``, ``Generator``, ``Tuple``) and ``copy`` module in ``lib``.

0.1.7 (2026-03-10)
------------------
* Added: Security validation for URL schemes in ``lib.send_url_request`` and ``lib.download`` (restricted to HTTP/HTTPS).
* Added: Filename sanitization in ``lib.download`` to prevent path traversal.
* Fixed: Refactored ``aeadencrypt.VaultCipher.encrypt_file`` and ``decrypt_file`` to use streaming (chunked) IO for constant memory usage.
* Fixed: Maintained backward compatibility for ``VaultCipher`` encrypted files.
* Added: Security warnings and legacy deprecation notices to ``aeadencrypt.VaultUtils`` docstrings.
* Added: Security warning regarding disabled SSL verification in ``conn.agol`` docstring.
* Added: Filename sanitization and Zip Slip protection in ``lib.download`` and ``lib.Archive.un_zip``.
* Added: Transitioned from ``safety`` to ``pip-audit`` for dependency scanning in ``pyproject.toml``.
* Added: Refined automated security scanning with targeted ``bandit`` annotations.

0.1.6 (2026-02-26)
------------------
* Fixed: ``lib``.
* Fixed: Updated ``email address``.

0.1.5 (2026-02-23)
------------------
* Fixed: ``conn``.
* Fixed: ``aeadencrypt.VaultCipher``.

0.1.4 (2026-02-20)
------------------
* Fixed: docs.

0.1.3 (2026-02-20)
------------------
* Fixed: Sphinx docs build configuration — removed ``rst2pdf`` dependency, replaced with ``sphinx-github-alerts``.
* Fixed: Simplified ``conf.py`` theme setup (removed deprecated ``html_theme_path``).
* Fixed: Added ``docs/requirements.txt`` to ``.readthedocs.yaml`` install step.

0.1.2 (2026-02-20)
------------------
* Fixed: Corrected ``pyproject.toml`` ``classifiers`` placement and updated GitHub project URLs.
* Fixed: Replaced ``rst2pdf`` with ``sphinx-github-alerts`` in optional docs dependencies.
* Fixed: Added ``docs/requirements.txt`` for Read the Docs environment.

0.1.1 (2026-02-20)
------------------
* Added: ``.readthedocs.yaml`` configuration file for Read the Docs integration.

0.1.0 (2026-02-20)
------------------
* Initial release of ntsm package.
* Added AEAD encryption and MSAL connection modules.
