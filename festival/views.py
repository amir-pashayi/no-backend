import mimetypes

from django.core import signing
from django.http import FileResponse, Http404
from django.urls import reverse
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
        registration = Registration.objects.filter(user__phone=data.validated_data["phone"], user__profile__national_id=data.validated_data["national_id"]).select_related("user","user__profile","festival","pool").prefetch_related("events").order_by("-created_at").first()
        if not registration: return Response({"detail":"اطلاعات واردشده صحیح نیست یا کارت ثبت‌نامی یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
        token = signing.dumps({"registration":str(registration.public_id)}, salt="festival.card-portrait")
        portrait_url = request.build_absolute_uri(f"{reverse('card-portrait', args=[registration.public_id])}?token={token}")
        age_group = "۱۲–۱۳ سال" if registration.age_at_registration <= 13 else "۱۴–۱۵ سال" if registration.age_at_registration <= 15 else "۱۶–۱۸ سال"
        return Response({"tracking_code":registration.tracking_code,"participant":{"first_name":registration.user.first_name,"last_name":registration.user.last_name},"national_id":registration.user.profile.national_id,"age_group":age_group,"portrait_url":portrait_url,"festival":registration.festival.title,"pool":registration.pool.name,"events":[event.title for event in registration.events.all()],"status":registration.status,"created_at":registration.created_at})


class CardPortraitView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, public_id):
        try:
            signed_data = signing.loads(
                request.query_params.get("token", ""),
                salt="festival.card-portrait",
                max_age=15 * 60,
            )
        except signing.BadSignature as error:
            raise Http404 from error
        if signed_data.get("registration") != str(public_id):
            raise Http404
        registration = Registration.objects.filter(public_id=public_id).first()
        if not registration or not registration.portrait:
            raise Http404
        content_type = mimetypes.guess_type(registration.portrait.name)[0] or "application/octet-stream"
        return FileResponse(registration.portrait.open("rb"), content_type=content_type)
