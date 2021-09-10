import calendar
from datetime import datetime, timedelta


def get_before_time(minutes=0, hours=0):
    return (datetime.now().astimezone() - timedelta(hours=hours, minutes=minutes)).strftime("%d %B %Y %H:%M %z")


def calc_headless_delta(start_time, interval):
    now = datetime.now()
    time_by_unit = None

    # Check current kindle bar
    if interval[-1] == "m":
        time_by_unit = (now - start_time).seconds // 60
    elif interval[-1] == "h":
        time_by_unit = (now - start_time).seconds // 60 // 60
    elif interval[-1] == "d":
        time_by_unit = (now - start_time).days
    elif interval[-1] == "M":
        month_days = calendar.monthrange(now.year, now.month)[1]
        time_by_unit = (now - start_time).days // month_days
    else:
        AssertionError("You need choose interval")
    delta_x = time_by_unit // int(interval[:-1])
    return delta_x