# coding=utf-8

import time
from datetime import tzinfo, timedelta


# 以下这段代码来自 https://docs.python.org/2/library/datetime.html#tzinfo-objects
_ZERO = timedelta(0)
_HOUR = timedelta(hours=1)

_STD_OFFSET = timedelta(seconds=-time.timezone)
if time.daylight:
    _DST_OFFSET = timedelta(seconds=-time.altzone)
else:
    _DST_OFFSET = _STD_OFFSET

_DST_DIFF = _DST_OFFSET - _STD_OFFSET


class _LocalTimezone(tzinfo):
    """local timezone"""

    def utcoffset(self, dt):
        if self._isdst(dt):
            return _DST_OFFSET
        else:
            return _STD_OFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return _DST_DIFF
        else:
            return _ZERO

    def tzname(self, dt):
        return time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (
            dt.year, dt.month, dt.day,
            dt.hour, dt.minute, dt.second,
            dt.weekday(), 0, 0)
        stamp = time.mktime(tt)
        tt = time.localtime(stamp)
        return tt.tm_isdst > 0

local_tz = _LocalTimezone()
