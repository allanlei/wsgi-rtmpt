# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function

from flask import current_app


def get_interval(failed, consecutive=None):
    """
    Increase interval every CONSECUTIVE fails in a row
    """
    if consecutive is None:
        consecutive = current_app.config['RTMP_FAIL_RAMPUP']
    intervals = current_app.config['RMPT_INTERVALS']
    return intervals[min(len(intervals) - 1, int(max(0, failed/consecutive)))]
