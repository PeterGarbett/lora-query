import datetime
import math

RESOLUTION = 2


def small_timestamp_mins():
    """I want a small number of digits that will change per minute
    So i work in fractions of a day, as you would with Julian days,
    so I subtract a large base and round to 4 decimal places"""

    today = datetime.datetime.now()
    unix_timestamp = datetime.datetime.timestamp(today)
    now = unix_timestamp % 31536000  # Seconds into the year
    stamp = round(now / (60 * 60), RESOLUTION)  # Hours
    return stamp


def time_difference_in_minutes(first, second):
    """
    Difference, to get a decimal
    """

    diff = second - first
    return round(diff, RESOLUTION)


def main():
    """Test program"""
    import time

    nw = small_timestamp_mins()
    print(nw)
    time.sleep(60)
    nw2 = small_timestamp_mins()

    change = time_difference_in_minutes(nw, nw2)
    print(change)


if __name__ == "__main__":
    main()
