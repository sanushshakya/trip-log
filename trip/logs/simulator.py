from datetime import timedelta

MAX_DRIVING_PER_SHIFT = timedelta(hours=11)  # Maximum driving time per shift
MAX_ON_DUTY_PER_SHIFT = timedelta(hours=14)  # Maximum on-duty time per shift
REQUIRED_BREAK_AFTER = timedelta(hours=8)  # Required break after continuous driving
BREAK_DURATION = timedelta(minutes=30)  # Duration of a short break
REQUIRED_RESET_TIME = timedelta(hours=10)  # Required reset time
CYCLE_LIMIT = timedelta(hours=70)  # Maximum cycle time in a week

def simulate_trip(total_driving_duration_hours, initial_cycle_used_hours):
    remaining_trip_drive_time = timedelta(hours=total_driving_duration_hours)
    shift_drive_time = timedelta(0)
    shift_on_duty_time = timedelta(0)
    drive_time_since_break = timedelta(0)
    cycle_time_used = timedelta(hours=initial_cycle_used_hours)

    events = []
    
    # Pickup duration
    pickup_duration = timedelta(hours=1)
    shift_on_duty_time += pickup_duration
    cycle_time_used += pickup_duration
    events.append({'status': 'ON_DUTY', 'duration_hours': 1, 'reason': 'Pickup'})
    
    while remaining_trip_drive_time > timedelta(0):
    
        if shift_drive_time >= MAX_DRIVING_PER_SHIFT or shift_on_duty_time >= MAX_ON_DUTY_PER_SHIFT:
            # Reset and take a sleeper berth break
            events.append({'status': 'OFF_DUTY', 'duration_hours': REQUIRED_RESET_TIME.total_seconds() / 3600, 'reason': '10-hour reset'})
            events.append({'status': 'OFF_DUTY', 'duration_hours': 8, 'reason': 'Sleeper Berth'})  # 8 hours sleeper berth
            shift_drive_time = timedelta(0)
            shift_on_duty_time = timedelta(0)
            drive_time_since_break = timedelta(0)
            continue 
            
        if drive_time_since_break >= REQUIRED_BREAK_AFTER:
            # Take a 30-minute break after the required driving hours
            events.append({'status': 'OFF_DUTY', 'duration_hours': 0.5, 'reason': '30-min break'})
            shift_on_duty_time += BREAK_DURATION 
            drive_time_since_break = timedelta(0)
            continue
            
        if cycle_time_used >= CYCLE_LIMIT:
            raise ValueError("Trip is not possible within the 70-hour cycle limit.")

        # Driving time during the shift
        drivable_time = min(
            remaining_trip_drive_time,
            MAX_DRIVING_PER_SHIFT - shift_drive_time,
            REQUIRED_BREAK_AFTER - drive_time_since_break
        )
        
        events.append({'status': 'DRIVING', 'duration_hours': drivable_time.total_seconds() / 3600})
        
        # Update times
        remaining_trip_drive_time -= drivable_time
        shift_drive_time += drivable_time
        shift_on_duty_time += drivable_time
        drive_time_since_break += drivable_time
        cycle_time_used += drivable_time

        # If shift exceeds the max driving duration, take a sleeper berth break
        if shift_drive_time >= MAX_DRIVING_PER_SHIFT:
            sleeper_berth_duration = timedelta(hours=8)  # Example: 8 hours sleeper berth break
            events.append({'status': 'OFF_DUTY', 'duration_hours': sleeper_berth_duration.total_seconds() / 3600, 'reason': 'Sleeper Berth'})
            shift_on_duty_time += sleeper_berth_duration
            cycle_time_used += sleeper_berth_duration

    # Dropoff duration
    dropoff_duration = timedelta(hours=1)
    shift_on_duty_time += dropoff_duration
    cycle_time_used += dropoff_duration
    events.append({'status': 'ON_DUTY', 'duration_hours': 1, 'reason': 'Dropoff'})

    return events