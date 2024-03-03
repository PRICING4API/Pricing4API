def heaviside(x):
    if x < 0:
        return 0
    else:
        return 1


def format_time(seconds: int)->str:
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
