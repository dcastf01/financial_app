import datetime
import time

def from_datetime_to_format_timestamp_to_binance_api(date_in_datetime):
    return int(time.mktime(date_in_datetime.timetuple())*1000)
def strdate_to_format_timestamp_to_binance_api(date,format_date= "%d/%m/%Y"):
    
    return from_datetime_to_format_timestamp_to_binance_api(datetime.datetime.strptime(date, format_date))

def timestamp_from_api_to_date(ms:int):
    return datetime.datetime.fromtimestamp(ms/1000.0)
