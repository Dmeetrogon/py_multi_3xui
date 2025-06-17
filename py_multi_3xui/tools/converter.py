import datetime

import logging

logger = logging.getLogger(__name__)
class Converter:

    @staticmethod
    def convert_days_to_valid_3xui_time(days: int)-> int:
        """
        Converts days to a valid time that can be used in 3xui
        :param days: days
        :return: a valid time format for 3xui
        """
        logger.debug("converting days to valid time format")

        try:
            epoch = datetime.datetime.fromtimestamp(0, datetime.UTC)
            now_utc = datetime.datetime.now(datetime.UTC)
        except AttributeError:
            from datetime import timezone
            epoch = datetime.datetime.fromtimestamp(0, timezone.utc)
            now_utc = datetime.datetime.now(timezone.utc)
        x_time = int((now_utc - epoch).total_seconds() * 1000.0)
        MILLISECONDS_PER_DAY = 24 * 60 * 60 * 1000  # 86400000
        x_time += MILLISECONDS_PER_DAY * days
        return int(x_time)
    @staticmethod
    def convert_milliseconds_to_days(milliseconds:int)->int:
        """
        Converting milliseconds to days
        :param milliseconds: amount of milliseconds
        :return: days
        """
        logger.debug("converting millisecond to days")
        MILLISECONDS_PER_DAY = 24 * 60 * 60 * 1000
        days = int(milliseconds / MILLISECONDS_PER_DAY)
        return days
    @staticmethod
    def convert_days_to_milliseconds(days:int)->int:
        """
        Converting days to milliseconds
        :param days: amount of days
        :return: milliseconds
        """
        logger.debug("converting days to millisecond")
        MILLISECONDS_PER_DAY = 24 * 60 * 60 * 1000
        milliseconds = days * MILLISECONDS_PER_DAY
        return milliseconds


