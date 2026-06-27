from datetime import datetime

def format_timestamp(ts=None):
    """Formats a timestamp or current time into a readable string."""
    if ts is None:
        return datetime.now().strftime("%I:%M %p")
    return datetime.fromtimestamp(ts).strftime("%I:%M %p")
