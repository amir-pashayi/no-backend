# بک‌اند جشنواره ندای امید

## اجرا

1. فایل `.env.example` را با نام `.env` کپی کنید و `DJANGO_SECRET_KEY` را با یک کلید تصادفی طولانی جایگزین کنید.
2. وابستگی‌ها را نصب کنید: `python -m pip install -r requirements.txt`
3. مایگریشن‌ها را اجرا کنید: `python manage.py migrate`
4. داده اولیه را بسازید: `python manage.py seed_festival`
5. برای ورود به پنل، مدیر بسازید: `python manage.py createsuperuser`
6. سرور توسعه: `python manage.py runserver`

پنل مدیریت Unfold در `http://127.0.0.1:8000/admin/` قرار دارد.

## API

- `GET /api/pools/` — فهرست استخرها
- `GET /api/festivals/{id}/events/` — مواد مسابقه جشنواره
- `POST /api/registrations/` — ثبت‌نام با `multipart/form-data`
- `POST /api/cards/recover/` — بازیابی کارت با `national_id` و `phone`
- `POST /api/auth/token/` و `POST /api/auth/token/refresh/` — توکن مدیران

## نکات امنیتی

- کد ملی و موبایل هم در API و هم در دیتابیس یکتا هستند؛ اعتبار کد ملی ایرانی در سمت سرور بررسی می‌شود.
- فایل‌ها محدود به JPG، PNG و PDF واقعی تا ۵ مگابایت هستند. محتوای تصویر/PDF نیز بررسی می‌شود، نه فقط پسوند فایل.
- مسیر ثبت‌نام و بازیابی کارت محدودیت تعداد درخواست دارند؛ مسیر بازیابی برای جلوگیری از حدس‌زدن اطلاعات فقط پیام عمومی برمی‌گرداند.
- شناسه عمومی و کد رهگیری غیرقابل‌حدس هستند و شناسه‌های داخلی دیتابیس هرگز در پاسخ کارت منتشر نمی‌شوند.
- در محیط production حتماً `DJANGO_DEBUG=False`، PostgreSQL، HTTPS، فضای ذخیره‌سازی خصوصی برای مدارک و اسکن آنتی‌ویروس فایل‌ها را فعال کنید. فایل‌های کاربر نباید از طریق وب‌سرور عمومی قابل‌دسترسی باشند.
