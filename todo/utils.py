# -*- coding: utf-8 -*-
import time


def log(*args, **kwargs):
    format_ = '%Y/%m/%d %H:%M:%S'
    value = time.localtime(int(time.time()))
    dt = time.strftime(format_, value)
    print(dt, *args, **kwargs)
