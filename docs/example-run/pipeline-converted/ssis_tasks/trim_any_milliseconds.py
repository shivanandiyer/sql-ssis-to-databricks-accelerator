# Converted from SSIS Expression Task: Trim Any Milliseconds
# Original SSIS expression:
#   @[User::TargetETLCutoffTime] = DATEADD("Millisecond", 0 - DATEPART("Millisecond", @[User::TargetETLCutoffTime]), @[User::TargetETLCutoffTime])

from datetime import datetime, timedelta, timezone


def compute() -> str:
    """TODO: translate the SSIS expression above into the equivalent Python.

    Example for DATEADD("Minute", -5, GETUTCDATE()) style expressions:
        return (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    """
    raise NotImplementedError('Translate the SSIS expression above.')