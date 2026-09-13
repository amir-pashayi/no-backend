from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from festival.models import CompetitionEvent, Festival, Pool

POOLS = ["هفت تیر", "قصر موج", "ولایت (جانبازان)", "مخابرات", "بسیج", "امام علی", "شهرداری", "باکری", "کارگران", "دانشگاه", "موج‌های آبی", "امیرکبیر", "شهید رجایی", "سایر"]
EVENTS = [("۲۵ متر کرال سینه تک‌دست", 12, 13), ("۵۰ متر ترکیبی", 12, 15), ("۲۵ متر شنای آزاد عبور از مانع", 12, 13), ("۵۰ متر کرال سینه تک‌دست", 14, 15), ("۵۰ متر شنای آزاد عبور از مانع", 14, 15), ("۵۰ متر حمل آدمک", 16, 18), ("۵۰ متر ترکیبی رده ۱۶–۱۸", 16, 18), ("۱۰۰ متر شنای آزاد عبور از مانع", 16, 18), ("پرتاب طناب", 16, 18)]

class Command(BaseCommand):
    help = "داده‌های اولیه جشنواره، مواد مسابقه و استخرها را ایجاد می‌کند."
    def handle(self, *args, **kwargs):
        festival, created = Festival.objects.get_or_create(title="جشنواره همگانی نجات غریق ندای امید", defaults={"registration_starts_at": timezone.now() - timedelta(days=1), "registration_ends_at": timezone.now() + timedelta(days=30), "is_active": True})
        for name in POOLS: Pool.objects.get_or_create(name=name)
        for order, (title, min_age, max_age) in enumerate(EVENTS, start=1): CompetitionEvent.objects.get_or_create(festival=festival, title=title, min_age=min_age, max_age=max_age, defaults={"order": order})
        self.stdout.write(self.style.SUCCESS("Festival seed data is ready."))
