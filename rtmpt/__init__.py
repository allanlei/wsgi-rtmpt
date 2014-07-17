# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals, print_function

import os
import sys


VERSION = (1, 0, 0)

__all__ = ['BASE_DIR', 'LIBS_ROOT']

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LIBS_ROOT = os.path.join(BASE_DIR, 'libs')

sys.path.extend([
    LIBS_ROOT,
])
