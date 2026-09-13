from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from .models import CompetitionEvent, Pool, Registration
from .serializers import CardRecoverySerializer, EventSerializer, PoolSerializer, RegistrationSerializer

class PoolListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]; queryset = Pool.objects.filter(is_active=True); serializer_class = PoolSerializer
class EventListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]; serializer_class = EventSerializer
    def get_queryset(self): return CompetitionEvent.objects.filter(is_active=True, festival_id=self.kwargs["festival_id"])
class RegistrationCreateView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]; serializer_class = RegistrationSerializer; throttle_classes = [ScopedRateThrottle]; throttle_scope = "registration"
class CardRecoveryView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]; serializer_class = CardRecoverySerializer; throttle_classes = [ScopedRateThrottle]; throttle_scope = "card_recovery"
    def post(self, request):
        data = self.get_serializer(data=request.data); data.is_valid(raise_exception=True)
        registration = Registration.objects.filter(user__phone=data.validated_data["phone"], user__profile__national_id=data.validated_data["national_id"]).select_related("user","festival","pool").prefetch_related("events").order_by("-created_at").first()
        if not registration: return Response({"detail":"اطلاعات واردشده صحیح نیست یا کارت ثبت‌نامی یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"tracking_code":registration.tracking_code,"participant":{"first_name":registration.user.first_name,"last_name":registration.user.last_name},"festival":registration.festival.title,"pool":registration.pool.name,"events":[event.title for event in registration.events.all()],"status":registration.status,"created_at":registration.created_at})
