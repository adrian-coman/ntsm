Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <http://keepachangelog.com/>`_, 
and this project adheres to `Semantic Versioning <http://semver.org/>`_.

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
