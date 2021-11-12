import calendar
from datetime import datetime, timedelta


def get_before_time(minutes=0, hours=0, **kwargs):
    return (datetime.now().astimezone() - timedelta(hours=hours, minutes=minutes, **kwargs)).strftime("%d %B %Y %H:%M %z")


def calc_headless_delta(self, interval):
    now = datetime.utcnow()
    time_by_unit = None

    # Check current kindle bar
    if interval[-1] == "m":
        time_by_unit = int(interval[:-1]) * 60
    elif interval[-1] == "h":
        time_by_unit = int(interval[:-1]) * 3600
    elif interval[-1] == "d":
        time_by_unit = int(interval[:-1]) * 3600 * 24
    elif interval[-1] == "M":
        month_days = calendar.monthrange(now.year, now.month)[1]
        time_by_unit = int(interval[:-1]) * 3600 * 24 * month_days
    else:
        AssertionError("You need choose interval")

    if int(now.timestamp()) % time_by_unit == 0:
        if not self.is_delta_updated:
            self.delta_x = self.delta_x + 1
            self.curr_time = now
            self.is_delta_updated = True
    else:
        self.is_delta_updated = False

    return self.delta_x