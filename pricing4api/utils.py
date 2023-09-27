def heaviside(x):
    if x < 0:
        return 0
    else:
        return 1


def format_time(seconds: int)->str:
        days = seconds // (24 * 60 * 60)
        hours = (seconds % (24 * 60 * 60)) // (60 * 60)
        minutes = (seconds % (60 * 60)) // 60
        seconds = seconds % 60

        time_string = ""
        if days > 0:
            time_string += f"{days} day{'s' if days > 1 else ''}, "
        if hours > 0:
                time_string += f"{hours} hour{'s' if hours > 1 else ''}, "
        if minutes > 0:
            time_string += f"{minutes} minute{'s' if minutes > 1 else ''}, "
        if seconds > 0:
            time_string += f"{seconds} second{'s' if seconds > 1 else ''}"

        return time_string.rstrip(", ")
