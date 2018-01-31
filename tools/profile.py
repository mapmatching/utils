# coding: utf-8
import cProfile
import StringIO
import pstats
import contextlib
import logging


@contextlib.contextmanager
def _profiled():
    pr = cProfile.Profile()
    pr.enable()
    yield
    pr.disable()
    s = StringIO.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    logging.info(s.getvalue())


def profiled(method):
    def wrapper(*args, **kwargs):
        with _profiled():
            method(*args, **kwargs)
    return wrapper
