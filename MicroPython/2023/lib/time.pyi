"""
time related functions. See: https://docs.micropython.org/en/v1.20.0/library/time.html

|see_cpython_module| :mod:`python:time` https://docs.python.org/3/library/time.html .

The ``time`` module provides functions for getting the current time and date,
measuring time intervals, and for delays.

**Time Epoch**: Unix port uses standard for POSIX systems epoch of
1970-01-01 00:00:00 UTC. However, some embedded ports use epoch of
2000-01-01 00:00:00 UTC. Epoch year may be determined with ``gmtime(0)[0]``.

**Maintaining actual calendar date/time**: This requires a
Real Time Clock (RTC). On systems with underlying OS (including some
RTOS), an RTC may be implicit. Setting and maintaining actual calendar
time is responsibility of OS/RTOS and is done outside of MicroPython,
it just uses OS API to query date/time. On baremetal ports however
system time depends on ``machine.RTC()`` object. The current calendar time
may be set using ``machine.RTC().datetime(tuple)`` function, and maintained
by following means:

* By a backup battery (which may be an additional, optional component for
  a particular board).
* Using networked time protocol (requires setup by a port/user).
* Set manually by a user on each power-up (many boards then maintain
  RTC time across hard resets, though some may require setting it again
  in such case).

If actual calendar time is not maintained with a system/MicroPython RTC,
functions below which require reference to current absolute time may
behave not as expected.
"""
from typing import Optional, Tuple, Any

def ticks_diff(ticks1, ticks2) -> int:
    """
    Measure ticks difference between values returned from `ticks_ms()`, `ticks_us()`,
    or `ticks_cpu()` functions, as a signed value which may wrap around.

    The argument order is the same as for subtraction
    operator, ``ticks_diff(ticks1, ticks2)`` has the same meaning as ``ticks1 - ticks2``.
    However, values returned by `ticks_ms()`, etc. functions may wrap around, so
    directly using subtraction on them will produce incorrect result. That is why
    `ticks_diff()` is needed, it implements modular (or more specifically, ring)
    arithmetics to produce correct result even for wrap-around values (as long as they not
    too distant inbetween, see below). The function returns **signed** value in the range
    [*-TICKS_PERIOD/2* .. *TICKS_PERIOD/2-1*] (that's a typical range definition for
    two's-complement signed binary integers). If the result is negative, it means that
    *ticks1* occurred earlier in time than *ticks2*. Otherwise, it means that
    *ticks1* occurred after *ticks2*. This holds **only** if *ticks1* and *ticks2*
    are apart from each other for no more than *TICKS_PERIOD/2-1* ticks. If that does
    not hold, incorrect result will be returned. Specifically, if two tick values are
    apart for *TICKS_PERIOD/2-1* ticks, that value will be returned by the function.
    However, if *TICKS_PERIOD/2* of real-time ticks has passed between them, the
    function will return *-TICKS_PERIOD/2* instead, i.e. result value will wrap around
    to the negative range of possible values.

    Informal rationale of the constraints above: Suppose you are locked in a room with no
    means to monitor passing of time except a standard 12-notch clock. Then if you look at
    dial-plate now, and don't look again for another 13 hours (e.g., if you fall for a
    long sleep), then once you finally look again, it may seem to you that only 1 hour
    has passed. To avoid this mistake, just look at the clock regularly. Your application
    should do the same. "Too long sleep" metaphor also maps directly to application
    behaviour: don't let your application run any single task for too long. Run tasks
    in steps, and do time-keeping inbetween.

    `ticks_diff()` is designed to accommodate various usage patterns, among them:

    * Polling with timeout. In this case, the order of events is known, and you will deal
      only with positive results of `ticks_diff()`::

    