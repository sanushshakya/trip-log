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
        fields = '__all__' 
        
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user  
        trip = Trip.objects.create(**validated_data)

        try:
            route_info = get_route(trip.pickup_location, trip.dropoff_location)
            events = simulate_trip(route_info['duration_hours'], trip.current_cycle_hours_used)
            create_daily_logs_for_trip(trip, events)
        except Exception as e:
            print(f"Trip plan generation failed: {e}")

        return trip
    
    def validate(self, data):
        if data['pickup_location'].lower() == data['dropoff_location'].lower():
            raise serializers.ValidationError("Pickup and dropoff locations cannot be the same.")
        return data

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


        
   