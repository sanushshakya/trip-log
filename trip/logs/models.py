from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta, date
from django.core.exceptions import ValidationError

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"

class Trip(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    current_location = models.CharField(max_length=255, blank=False, null=False)
    pickup_location = models.CharField(max_length=255, blank=False, null=False)
    dropoff_location = models.CharField(max_length=255, blank=False, null=False)
    current_cycle_hours_used = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(70)])
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    def calculate_cycle_hours(self):
        eight_days_ago = date.today() - timedelta(days=7)
        logs = self.daily_logs.filter(date__gte=eight_days_ago)

        total_hours = 0
        for log in logs:
            total_hours += (
                log.off_duty_hours +
                log.sleeper_berth_hours +
                log.driving_hours +
                log.on_duty_not_driving_hours
            )
        return total_hours

    def update_cycle_hours(self):
        self.current_cycle_hours_used = self.calculate_cycle_hours()
        self.save()
        
    @property
    def available_cycle_hours(self):
        return max(0, 70 - self.current_cycle_hours_used)
        
    def __str__(self):
        return f"Trip #{self.id} for {self.user.email}"

class DailyLog(models.Model):
    trip = models.ForeignKey(Trip, related_name='daily_logs', on_delete=models.CASCADE)
    date = models.DateField()
    off_duty_hours = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(24)])
    sleeper_berth_hours =  models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(24)])
    driving_hours =  models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(24)])
    on_duty_not_driving_hours =  models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(24)])
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('trip', 'date')

    def __str__(self):
        return f"Daily Log for {self.trip} on {self.date}"
    
    def clean(self):
        total = (
            self.off_duty_hours +
            self.sleeper_berth_hours +
            self.driving_hours +
            self.on_duty_not_driving_hours
        )
        if total > 24:
            raise ValidationError("Total hours in a day cannot exceed 24.")