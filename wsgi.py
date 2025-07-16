#!/usr/bin/env python
"""
WSGI config for TastyBites project.

This module contains the WSGI application used by PythonAnywhere's
web servers. It exposes the WSGI callable as a module-level variable
named ``application``.

For more information on this file, see
https://help.pythonanywhere.com/pages/Flask/
"""

import os
import sys

# Add your project directory to Python path
path = '/home/raza786/tastybites/'
if path not in sys.path:
    sys.path.insert(0, path)

from backend.app import app as application

if __name__ == "__main__":
    application.run()
