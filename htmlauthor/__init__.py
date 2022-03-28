# -*- coding: utf-8 -*-
"""
Extract the author of web pages.
"""

import logging
from .core import extract

logging.getLogger(__name__).addHandler(logging.NullHandler())
