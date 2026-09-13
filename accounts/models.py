from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(r"^09\d{9}$", "شماره همراه باید با ۰۹ شروع و ۱۱ رقم باشد.")

class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone: raise ValueError("شماره همراه الزامی است.")
        user = self.model(phone=phone, **extra_fields)
        user.set_unusable_password() if password is None else user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True); extra_fields.setdefault("is_superuser", True)
        if not password: raise ValueError("رمز عبور مدیر الزامی است.")
        return self.create_user(phone, password, **extra_fields)

class User(AbstractUser):
    username = None
    phone = models.CharField("شماره همراه", max_length=11, unique=True, validators=[phone_validator])
    first_name = models.CharField("نام", max_length=80)
    last_name = models.CharField("نام خانوادگی", max_length=80)
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = UserManager()
    class Meta: verbose_name = "کاربر"; verbose_name_plural = "کاربران"
    def __str__(self): return f"{self.first_name} {self.last_name}"

class UserProfile(models.Model):
    class Gender(models.TextChoices): MALE = "male", "آقا"; FEMALE = "female", "خانم"
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    national_id = models.CharField("کد ملی", max_length=10, unique=True)
    birth_date = models.DateField("تاریخ تولد")
    gender = models.CharField("جنسیت", max_length=10, choices=Gender.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: verbose_name = "پروفایل کاربر"; verbose_name_plural = "پروفایل کاربران"
