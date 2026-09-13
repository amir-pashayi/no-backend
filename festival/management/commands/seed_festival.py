from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from festival.models import CompetitionEvent, Festival, Pool

POOLS = ["هفت تیر", "قصر موج", "ولایت (جانبازان)", "مخابرات", "بسیج", "امام علی", "شهرداری", "باکری", "کارگران", "دانشگاه", "موج‌های آبی", "امیرکبیر", "شهید رجایی", "سایر"]
EVENTS = [("۲۵ متر کرال سینه تک‌دست", 12, 13), ("۵۰ متر ترکیبی", 12, 15), ("۲۵ متر شنای آزاد عبور از مانع", 12, 13), ("۵۰ متر کرال سینه تک‌دست", 14, 15), ("۵۰ متر شنای آزاد عبور از مانع", 14, 15), ("۵۰ متر حمل آدمک", 16, 18), ("۵۰ متر ترکیبی رده ۱۶–۱۸", 16, 18), ("۱۰۰ متر شنای آزاد عبور از مانع", 16, 18), ("پرتاب طناب", 16, 18)]

class Command(BaseCommand):
    help = "داده‌های اولیه جشنواره، مواد مسابقه و استخرها را ایجاد می‌کند."

    def handle(self, *args, **kwargs):
        now = timezone.now()
        festival, created = Festival.objects.get_or_create(
            title="جشنواره همگانی نجات غریق ندای امید",
            defaults={
                "registration_starts_at": now - timedelta(days=1),
                "registration_ends_at": now + timedelta(days=30),
                "is_active": True,
            },
        )

        if not festival.is_active or festival.registration_ends_at <= now:
            festival.is_active = True
            festival.registration_starts_at = now - timedelta(days=1)
            festival.registration_ends_at = now + timedelta(days=30)
            festival.save(update_fields=["is_active", "registration_starts_at", "registration_ends_at"])

        for name in POOLS:
            Pool.objects.update_or_create(name=name, defaults={"is_active": True})

        for order, (title, min_age, max_age) in enumerate(EVENTS, start=1):
            CompetitionEvent.objects.update_or_create(
                festival=festival,
                title=title,
                min_age=min_age,
                max_age=max_age,
                defaults={"order": order, "is_active": True},
            )

        status = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f"Festival seed data {status}. Festival ID: {festival.pk}"))
