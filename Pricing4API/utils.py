def heaviside(x):
    if x < 0:
        return 0
    else:
        return 1


def format_time(seconds: int) -> str:
    days = int(seconds // (24 * 60 * 60))
    hours = int((seconds % (24 * 60 * 60)) // (60 * 60))
    minutes = int((seconds % (60 * 60)) // 60)
    seconds = int(seconds % 60)

    time_string = ""
    if days > 0:
        time_string += f"{days}d"
    if hours > 0:
        time_string += f"{hours}h"
    if minutes > 0:
        time_string += f"{minutes}m"
    if seconds > 0:
        time_string += f"{seconds}s"

    return time_string.rstrip(", ")


def time_unit_to_seconds(time_unit: str) -> int:
    if time_unit == "minute" or time_unit == "minutes":
        return 60
    elif time_unit == "hour" or time_unit == "hours":
        return 60 * 60
    elif time_unit == "day" or time_unit == "days":
        return 24 * 60 * 60
    elif time_unit == "week" or time_unit == "weeks":
        return 7 * 24 * 60 * 60
    elif time_unit == "month" or time_unit == "monthly" or time_unit == "months":
        return 30 * 24 * 60 * 60
    elif time_unit == "year" or time_unit == "years":
        return 365 * 24 * 60 * 60
    else:
        return 1
