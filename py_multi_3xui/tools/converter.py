import datetime

import logging

logger = logging.getLogger(__name__)
class Converter:
    @staticmethod
    def convert_days_to_milliseconds(days: int)-> int:
        logger.debug("converting days to valid time format")
        """
                converts days to time format that used in 3x-ui
                Args:
                   days: int

                Returns:
                    time: int
                """
        try:
            epoch = datetime.datetime.fromtimestamp(0, datetime.UTC)
            now_utc = datetime.datetime.now(datetime.UTC)
        except AttributeError:
            from datetime import timezone
            epoch = datetime.datetime.fromtimestamp(0, timezone.utc)
            now_utc = datetime.datetime.now(timezone.utc)
        x_time = int((now_utc - epoch).total_seconds() * 1000.0)
        MILLISECONDS_PER_DAY = 24 * 60 * 60 * 1000  # 86400000
        MILLISECONDS_OFFSET = 3 * 60 * 60 * 1000  # 10800000
        x_time += MILLISECONDS_PER_DAY * days - MILLISECONDS_OFFSET
        return int(x_time)
    @staticmethod
    def convert_milliseconds_to_days(milliseconds:int)->int:
        MILLISECONDS_PER_DAY = 24 * 60 * 60 * 1000
        days = int(milliseconds / MILLISECONDS_PER_DAY)
        return days


