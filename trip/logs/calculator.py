import requests 
from django.conf import settings
from datetime import date, timedelta

MAX_DRIVING_HOURS_PER_DAY = 11
MAX_ON_DUTY_HOURS_PER_DAY = 14
REQUIRED_OFF_DUTY_HOURS = 10
CYCLE_LIMIT_HOURS = 70
PICKUP_DROPPOFF_TIME_HOURS = 1
FUEL_STOP_MILES = 1000
FUEL_STOP_DURATION_HOURS = 0.5 

def get_route(origin, destination):
    def geocode(address):
        params = {
            'api_key': settings.ORS_API_KEY,
            'text': address,
            'size': 1
        }
        response = requests.get('https://api.openrouteservice.org/geocode/search', params=params)
        response.raise_for_status()
        data = response.json()
        if not data['features']:
            raise ValueError(f"Could not find coordinates for {address}")
   
        return data['features'][0]['geometry']['coordinates']

    origin_coords = geocode(origin)
    destination_coords = geocode(destination)

    headers = {
        'Authorization': settings.ORS_API_KEY,
        'Content-Type': 'application/json',
    }
    body = {
        'coordinates': [origin_coords, destination_coords],
        'instructions': 'false', 
    }

    response = requests.post('https://api.openrouteservice.org/v2/directions/driving-hgv', json=body, headers=headers)
    response.raise_for_status()
    data = response.json()

    route = data['routes'][0]
    summary = route['summary']
    geometry = route['geometry'] 

    return {
        "distance_miles": summary['distance'] * 0.000621371, 
        "duration_hours": summary['duration'] / 3600,
        "geometry": geometry, 
        "start_coords": list(reversed(origin_coords)), 
        "end_coords": list(reversed(destination_coords)), 
    }



