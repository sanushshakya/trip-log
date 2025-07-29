from rest_framework import serializers
from .models import CustomUser, Trip, DailyLog
from .calculator import get_route
from .simulator import simulate_trip
from .utils import create_daily_logs_for_trip 

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name']
        


class TripSerializer(serializers.ModelSerializer):
    available_cycle_hours = serializers.FloatField(read_only=True)

    class Meta:
        model = Trip
        fields = [
            'id', 'user', 'current_location', 'pickup_location',
            'dropoff_location', 'current_cycle_hours_used',
            'available_cycle_hours', 'created_on', 'updated_on',
        ]
        
    
class DailyLogSerializer(serializers.ModelSerializer):
    trip = TripSerializer(read_only=True)
    class Meta:
        model = DailyLog
        fields = [
            'id', 'trip', 'date',
            'off_duty_hours', 'sleeper_berth_hours',
            'driving_hours', 'on_duty_not_driving_hours',
            'created_on', 'updated_on'
        ]

    def validate(self, data):
        total = (
            data.get('off_duty_hours', 0) +
            data.get('sleeper_berth_hours', 0) +
            data.get('driving_hours', 0) +
            data.get('on_duty_not_driving_hours', 0)
        )
        if total > 24:
            raise serializers.ValidationError("Total logged hours in a day cannot exceed 24.")
        return data