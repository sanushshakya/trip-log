from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as authtoken_views
from .views import UserViewSet, TripViewSet, DailyLogViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename="users")
router.register(r'trips', TripViewSet, basename="trips")
router.register(r'logs', DailyLogViewSet, basename="logs")

urlpatterns = [
    path('', include(router.urls)),
    path('api-token-auth/', authtoken_views.obtain_auth_token)
]