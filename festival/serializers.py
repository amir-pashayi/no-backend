from datetime import date
import re
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers
from accounts.models import User, UserProfile
from .models import CompetitionEvent, Festival, Pool, Registration

def validate_national_id(value):
    if not value.isdigit() or len(value) != 10 or len(set(value)) == 1: raise serializers.ValidationError("کد ملی معتبر نیست.")
    check = int(value[-1]); total = sum(int(value[i]) * (10-i) for i in range(9)) % 11
    if check != (total if total < 2 else 11-total): raise serializers.ValidationError("کد ملی معتبر نیست.")
    return value
def calculate_age(birth_date):
    today = date.today(); return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def jalali_to_gregorian(value):
    """Converts a valid Persian YYYY/MM/DD date to a Gregorian date without client trust."""
    if not re.fullmatch(r"1[34]\d{2}/(0?[1-9]|1[0-2])/(0?[1-9]|[12]\d|3[01])", value):
        raise serializers.ValidationError("تاریخ تولد شمسی معتبر نیست.")
    jy, jm, jd = map(int, value.split("/")); jy += 1595
    days = -355668 + 365 * jy + (jy // 33) * 8 + ((jy % 33 + 3) // 4) + jd
    days += (jm - 1) * 31 if jm < 7 else (jm - 7) * 30 + 186
    gy = 400 * (days // 146097); days %= 146097
    if days > 36524:
        gy += 100 * ((days - 1) // 36524); days = (days - 1) % 36524
        if days >= 365: days += 1
    gy += 4 * (days // 1461); days %= 1461
    if days > 365: gy += (days - 1) // 365; days = (days - 1) % 365
    gd = days + 1; leap = gy % 4 == 0 and (gy % 100 != 0 or gy % 400 == 0)
    month_days = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 1
    for length in month_days:
        if gd <= length: break
        gd -= length; gm += 1
    return date(gy, gm, gd)

class PoolSerializer(serializers.ModelSerializer):
    class Meta: model = Pool; fields = ["id", "name"]
class EventSerializer(serializers.ModelSerializer):
    class Meta: model = CompetitionEvent; fields = ["id", "title", "min_age", "max_age", "gender"]
class RegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=80, write_only=True)
    last_name = serializers.CharField(max_length=80, write_only=True)
    phone = serializers.RegexField(r"^09\d{9}$", write_only=True)
    national_id = serializers.CharField(min_length=10, max_length=10, validators=[validate_national_id], write_only=True)
    birth_date = serializers.CharField(write_only=True)
    gender = serializers.ChoiceField(choices=UserProfile.Gender.choices, write_only=True)
    event_ids = serializers.PrimaryKeyRelatedField(queryset=CompetitionEvent.objects.filter(is_active=True), many=True, write_only=True)
    terms_accepted = serializers.BooleanField(write_only=True)
    insurance_confirmed = serializers.BooleanField(write_only=True)
    payment_confirmed = serializers.BooleanField(write_only=True)
    class Meta:
        model = Registration
        fields = ["public_id","tracking_code","first_name","last_name","phone","national_id","birth_date","gender","festival","pool","event_ids","insurance_document","portrait","birth_certificate","payment_receipt","terms_accepted","insurance_confirmed","payment_confirmed","status","created_at"]
        read_only_fields = ["public_id","tracking_code","status","created_at"]
    def validate(self, attrs):
        if not all(attrs[key] for key in ("terms_accepted","insurance_confirmed","payment_confirmed")): raise serializers.ValidationError("تأیید همه شرایط الزامی است.")
        attrs["birth_date"] = jalali_to_gregorian(attrs["birth_date"])
        age = calculate_age(attrs["birth_date"])
        if not 12 <= age <= 18: raise serializers.ValidationError({"birth_date":"سن شرکت‌کننده باید بین ۱۲ تا ۱۸ سال باشد."})
        festival = attrs["festival"]
        if not festival.is_active or not festival.registration_starts_at <= timezone.now() <= festival.registration_ends_at: raise serializers.ValidationError("ثبت‌نام این جشنواره فعال نیست.")
        for event in attrs["event_ids"]:
            if event.festival_id != festival.id or not event.min_age <= age <= event.max_age or event.gender not in ("all", attrs["gender"]): raise serializers.ValidationError({"event_ids":"یک یا چند ماده انتخابی معتبر نیست."})
        return attrs
    @transaction.atomic
    def create(self, validated):
        now = timezone.now(); event_ids = validated.pop("event_ids"); first_name = validated.pop("first_name"); last_name = validated.pop("last_name"); phone = validated.pop("phone"); national_id = validated.pop("national_id"); birth_date = validated.pop("birth_date"); gender = validated.pop("gender")
        validated.pop("terms_accepted"); validated.pop("insurance_confirmed"); validated.pop("payment_confirmed")
        profile = UserProfile.objects.select_for_update().filter(national_id=national_id).select_related("user").first()
        if profile and profile.user.phone != phone: raise serializers.ValidationError("این کد ملی با شماره همراه دیگری ثبت شده است.")
        user, _ = User.objects.select_for_update().get_or_create(phone=phone, defaults={"first_name":first_name,"last_name":last_name})
        if hasattr(user, "profile") and user.profile.national_id != national_id: raise serializers.ValidationError("این شماره همراه با کد ملی دیگری ثبت شده است.")
        if Registration.objects.filter(user=user, festival=validated["festival"]).exists(): raise serializers.ValidationError("برای این کد ملی و شماره همراه قبلاً در این جشنواره ثبت‌نام انجام شده است.")
        user.first_name, user.last_name = first_name, last_name; user.save(update_fields=["first_name","last_name"])
        UserProfile.objects.update_or_create(user=user, defaults={"national_id":national_id,"birth_date":birth_date,"gender":gender})
        try:
            with transaction.atomic():
                registration = Registration.objects.create(user=user, age_at_registration=calculate_age(birth_date), terms_accepted_at=now, insurance_confirmed_at=now, payment_confirmed_at=now, **validated)
        except IntegrityError as error:
            raise serializers.ValidationError("برای این کاربر قبلاً در این جشنواره ثبت‌نام انجام شده است.") from error
        registration.events.set(event_ids)
        return registration
class CardRecoverySerializer(serializers.Serializer):
    national_id = serializers.CharField(min_length=10, max_length=10, validators=[validate_national_id])
    phone = serializers.RegexField(r"^09\d{9}$")
