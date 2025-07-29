from django.contrib import admin
from .models import CustomUser, DailyLog, Trip

@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_staff', 'is_active')
    
@admin.register(DailyLog)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id','date', 'off_duty_hours', 'sleeper_berth_hours', 'driving_hours', 'on_duty_not_driving_hours')
              
@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ( 'user', 'pickup_location', 'dropoff_location', 'created_on')