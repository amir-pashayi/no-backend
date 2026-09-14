import secrets
import uuid
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from .validators import validate_document

class Pool(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ["name"]; verbose_name = "Pool"; verbose_name_plural = "Pools"
    def __str__(self): return self.name

class Festival(models.Model):
    title = models.CharField(max_length=160, default="جشنواره همگانی نجات غریق (ندای امید)")
    registration_starts_at = models.DateTimeField()
    registration_ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    class Meta: verbose_name = "Festival"; verbose_name_plural = "Festivals"
    def __str__(self): return self.title

class CompetitionEvent(models.Model):
    festival = models.ForeignKey(Festival, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=150)
    min_age = models.PositiveSmallIntegerField(validators=[MinValueValidator(12)])
    max_age = models.PositiveSmallIntegerField()
    gender = models.CharField(max_length=10, choices=[("all","All"),("male","Male"),("female","Female")], default="all")
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ["order", "title"]; verbose_name = "Competition event"; verbose_name_plural = "Competition events"
    def __str__(self): return self.title

def document_path(instance, filename):
    return f"registrations/{instance.public_id}/{filename}"

class Registration(models.Model):
    class Status(models.TextChoices): PENDING = "pending", "Pending review"; APPROVED = "approved", "Approved"; REJECTED = "rejected", "Rejected"
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tracking_code = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="registrations")
    festival = models.ForeignKey(Festival, on_delete=models.PROTECT, related_name="registrations")
    pool = models.ForeignKey(Pool, on_delete=models.PROTECT)
    events = models.ManyToManyField(CompetitionEvent, related_name="registrations")
    age_at_registration = models.PositiveSmallIntegerField()
    insurance_document = models.FileField(upload_to=document_path, validators=[validate_document])
    portrait = models.FileField(upload_to=document_path, validators=[validate_document])
    birth_certificate = models.FileField(upload_to=document_path, validators=[validate_document])
    payment_receipt = models.FileField(upload_to=document_path, validators=[validate_document])
    terms_accepted_at = models.DateTimeField()
    insurance_confirmed_at = models.DateTimeField()
    payment_confirmed_at = models.DateTimeField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Registration"; verbose_name_plural = "Registrations"
        constraints = [models.UniqueConstraint(fields=["user", "festival"], name="one_registration_per_user_per_festival")]
    def save(self, *args, **kwargs):
        if not self.tracking_code:
            while True:
                tracking_code = f"NO-{secrets.randbelow(9_000_000) + 1_000_000}"
                if not Registration.objects.filter(tracking_code=tracking_code).exists():
                    self.tracking_code = tracking_code
                    break
        super().save(*args, **kwargs)
    def __str__(self): return self.tracking_code
