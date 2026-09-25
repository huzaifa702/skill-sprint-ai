# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PythonAnywhere WSGI Configuration for SkillSprint AI
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 1. In PythonAnywhere Web tab, set Working directory to: /home/<username>/skill-sprint-ai
# 2. Set Virtualenv path to: /home/<username>/.virtualenvs/skillsprint-env
# 3. Paste this file content into your WSGI configuration file:
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import sys
import os

# Expand path to project directory
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application
