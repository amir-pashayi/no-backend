from pathlib import Path
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGES = {"jpeg", "png"}

def validate_document(uploaded_file):
    if uploaded_file.size > MAX_FILE_SIZE:
        raise ValidationError("حجم هر فایل نباید بیشتر از ۵ مگابایت باشد.")
    suffix = Path(uploaded_file.name).suffix.lower()
    head = uploaded_file.read(32)
    uploaded_file.seek(0)
    if suffix == ".pdf":
        if not head.startswith(b"%PDF-"): raise ValidationError("فایل PDF معتبر نیست.")
        return
    if suffix not in {".jpg", ".jpeg", ".png"}:
        raise ValidationError("فقط تصویر JPG/PNG یا PDF معتبر قابل بارگذاری است.")
    try:
        image = Image.open(uploaded_file)
        image.verify()
        if image.format.lower() not in ALLOWED_IMAGES:
            raise ValidationError("فرمت واقعی تصویر با فایل انتخاب‌شده مطابقت ندارد.")
    except (UnidentifiedImageError, OSError):
        raise ValidationError("تصویر قابل اعتبارسنجی نیست.")
    finally:
        uploaded_file.seek(0)
