from datetime import datetime, time
import pytz

IST = pytz.timezone('Asia/Kolkata')

def get_ist_now() -> datetime:
    return datetime.now(IST)

def is_market_open(market_start: str = "09:15", market_end: str = "15:30") -> bool:
    now = get_ist_now()
    
    # Check if weekend
    if now.weekday() >= 5:
        return False
    
    start_time = datetime.strptime(market_start, "%H:%M").time()
    end_time = datetime.strptime(market_end, "%H:%M").time()
    current_time = now.time()
    
    return start_time <= current_time <= end_time

def get_market_hours(market_start: str = "09:15", market_end: str = "15:30"):
    return {
        'start': datetime.strptime(market_start, "%H:%M").time(),
        'end': datetime.strptime(market_end, "%H:%M").time()
    }
