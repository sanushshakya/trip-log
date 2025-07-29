from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from requests.exceptions import RequestException

from .models import CustomUser, Trip, DailyLog
from .serializers import UserSerializer, TripSerializer, DailyLogSerializer
from .calculator import get_route
from .simulator import simulate_trip


class UserViewSet(ViewSet):
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def get_users(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=200)
    
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required."}, status=400)

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response({"error": "Invalid credentials"}, status=401)

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user": UserSerializer(user).data
        }, status=200)

class TripViewSet(ViewSet):
    
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def get_trip(self, request):
        id = request.query_params.get("id")
        log = Trip.objects.get(id=id)
        serializer = TripSerializer(log)
        return Response(serializer.data, status=200)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def get_trips(self, request):
        trips = Trip.objects.filter(user=request.user)
        serializer = TripSerializer(trips, many=True)
        return Response(serializer.data, status=200)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def create_trip(self, request):
        serializer = TripSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            trip = serializer.save()
            return Response(TripSerializer(trip).data, status=201)
        return Response(serializer.errors, status=400)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def generate_plan(self, request, pk=None):
        try:
            trip = Trip.objects.get(pk=pk, user=request.user)
        except Trip.DoesNotExist:
            return Response({'error': 'Trip not found.'}, status=404)

        try:
            route_info = get_route(trip.pickup_location, trip.dropoff_location)
            events = simulate_trip(route_info['duration_hours'], trip.current_cycle_hours_used)

            return Response({'events': events, 'routes': route_info}, status=200)

        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        except RequestException as e:
            return Response({'error': f'Failed to connect to mapping service: {e}'}, status=503)
        except Exception:
            return Response({'error': 'An unexpected server error occurred.'}, status=500)


class DailyLogViewSet(ViewSet):
    
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def get_log(self, request):
        id = request.query_params.get("id")
        log = DailyLog.objects.get(id=id)
        serializer = DailyLogSerializer(log)
        return Response(serializer.data, status=200)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def get_logs(self, request):
        logs = DailyLog.objects.all()
        serializer = DailyLogSerializer(logs, many=True)
        return Response(serializer.data, status=200)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def create_log(self, request):
        serializer = DailyLogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
        