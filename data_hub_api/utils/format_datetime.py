from datetime import datetime, timezone
from dateutil.parser import parse


def format_datetime_with_utc_offset(
    date_string: str,
    date_format: str = "%Y-%m-%dT%H:%M:%S%z"
):

    if isinstance(date_string, datetime):
        date_string = date_string.strftime("%Y-%m-%dT%H:%M:%S%z")

    dt_object = parse(date_string)

    # Set the UTC timezone explicitly
    dt_object_utc = dt_object.replace(tzinfo=timezone.utc)

    # Convert to the desired timezone (UTC) with the colon in the UTC offset
    dt_object_with_tz = dt_object_utc.astimezone(timezone.utc)

    # Format the datetime object with the correct UTC offset format
    formatted_date_string = dt_object_with_tz.strftime(date_format)

    # Manually add the colon in the UTC offset
    formatted_date_string = formatted_date_string[:-2] + ":" + formatted_date_string[-2:]

    return formatted_date_string
