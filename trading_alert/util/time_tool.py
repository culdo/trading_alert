from datetime import datetime, timedelta


def get_before_time(minutes=0, hours=0):
    return (datetime.now().astimezone() - timedelta(hours=hours, minutes=minutes)).strftime("%d %B %Y %H:%M %z")