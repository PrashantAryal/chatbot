import re
import dateparser 
import datetime
import parsedatetime as pdt

def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def validate_phone(phone):
    return re.match(r"^\+?[1-9]\d{1,14}$", phone) is not None

def extract_date(date_str):
    """
    Extract and parse the date string.
    """
    cal = pdt.Calendar()
    time_struct, parse_status = cal.parse(date_str)

    if parse_status == 1:  # Valid date parsed
        date = datetime.datetime(*time_struct[:6])
        return date.strftime("%Y-%m-%d")
    else:
        return "Sorry, I couldn't understand the date. Please try again."