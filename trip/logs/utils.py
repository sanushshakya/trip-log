from collections import defaultdict
from datetime import datetime, timedelta
from .models import DailyLog

def create_daily_logs_for_trip(trip, events, start_date=None):
    
    if start_date is None:
        start_date = datetime.now().date()

    logs_by_date = defaultdict(lambda: {
        'off_duty_hours': 0,
        'sleeper_berth_hours': 0,
        'driving_hours': 0,
        'on_duty_not_driving_hours': 0,
    })

    current_time = datetime.combine(start_date, datetime.min.time())

    for event in events:
        hours = event['duration_hours']
        end_time = current_time + timedelta(hours=hours)

        while current_time.date() < end_time.date():
            remaining_today = datetime.combine(current_time.date() + timedelta(days=1), datetime.min.time()) - current_time
            chunk_hours = remaining_today.total_seconds() / 3600
            
            add_hours_to_log(logs_by_date[current_time.date()], event, chunk_hours)
            
            current_time += timedelta(hours=chunk_hours)
            hours -= chunk_hours

        if hours > 0:
            add_hours_to_log(logs_by_date[current_time.date()], event, hours)
            current_time += timedelta(hours=hours)

    for log_date, values in logs_by_date.items():
        DailyLog.objects.create(
            trip=trip,
            date=log_date,
            driving_hours=values['driving_hours'],
            off_duty_hours=values['off_duty_hours'],
            sleeper_berth_hours=values['sleeper_berth_hours'],
            on_duty_not_driving_hours=values['on_duty_not_driving_hours']
        )

def add_hours_to_log(log, event, hours):
    """
    Adds a given number of hours to the correct category in a daily log
    based on the event's status and reason.
    """
    status = event['status']
    reason = event.get('reason', '') 

    if status == 'DRIVING':
        log['driving_hours'] += hours
    elif status == 'ON_DUTY':
        log['on_duty_not_driving_hours'] += hours
    elif status == 'OFF_DUTY':
        if 'Sleeper Berth' in reason or 'reset' in reason:
            log['sleeper_berth_hours'] += hours
        else:
            log['off_duty_hours'] += hours
    elif status == 'SLEEPER':
        log['sleeper_berth_hours'] += hours