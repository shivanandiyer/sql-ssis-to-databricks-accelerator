# Converted from SSIS Expression Task: Calculate ETL Cutoff Time backup
# Original SSIS expression:
#   @[User::TargetETLCutoffTime] = DATEADD("Minute", -5, GETUTCDATE()  )

from datetime import datetime, timedelta, timezone


def compute() -> str:
    """TODO: translate the SSIS expression above into the equivalent Python.

    Example for DATEADD("Minute", -5, GETUTCDATE()) style expressions:
        return (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    """
    raise NotImplementedError('Translate the SSIS expression above.')