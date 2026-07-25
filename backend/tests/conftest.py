"""
conftest.py — Pytest shared fixtures for Pramiti OS test suite.
Loaded automatically by pytest before any test module runs.
"""
import sys
import os
import pytest

# Ensure backend root is always on the path for all test modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
