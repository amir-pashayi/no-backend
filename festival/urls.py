from django.urls import path
from .views import CardPortraitView, CardRecoveryView, EventListView, PoolListView, RegistrationCreateView
urlpatterns = [path("pools/", PoolListView.as_view()), path("festivals/<int:festival_id>/events/", EventListView.as_view()), path("registrations/", RegistrationCreateView.as_view()), path("cards/recover/", CardRecoveryView.as_view()), path("cards/<uuid:public_id>/portrait/", CardPortraitView.as_view(), name="card-portrait")]
