from pathlib import Path
from uuid import uuid4
from django.db import models
from django.utils import timezone

STATUS_CHOICES = [
    ('New', 'New'), ('Contacted', 'Contacted'), ('In Progress', 'In Progress'),
    ('Quoted', 'Quoted'), ('Won', 'Won'), ('Closed', 'Closed'),
]

def private_upload_path(instance, filename):
    suffix = Path(filename).suffix.lower()
    month = timezone.now().strftime('%Y/%m')
    return f'private_uploads/{month}/{uuid4().hex}{suffix}'


def public_media_upload_path(instance, filename):
    suffix = Path(filename).suffix.lower()
    month = timezone.now().strftime('%Y/%m')
    return f'public_media/{month}/{uuid4().hex}{suffix}'


def news_update_upload_path(instance, filename):
    suffix = Path(filename).suffix.lower()
    month = timezone.now().strftime('%Y/%m')
    return f'news_updates/{month}/{uuid4().hex}{suffix}'

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class ContactEnquiry(TimestampedModel):
    name = models.CharField(max_length=120)
    company = models.CharField(max_length=160, blank=True)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=32, blank=True)
    requirement = models.CharField(max_length=180, blank=True)
    message = models.TextField(max_length=5000)
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default='New', db_index=True)
    internal_note = models.TextField(blank=True, max_length=5000)
    ip_hash = models.CharField(max_length=64, blank=True, help_text='Optional hashed source address for abuse analysis; never stores raw IP.')
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact enquiry'
    def __str__(self):
        return f'{self.name} — {self.requirement or "Contact enquiry"}'

class QuoteRequest(TimestampedModel):
    name = models.CharField(max_length=120)
    company = models.CharField(max_length=160)
    job_title = models.CharField(max_length=120, blank=True)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=32)
    location = models.CharField(max_length=180, blank=True)
    requirement = models.CharField(max_length=180)
    project_requirement = models.TextField(max_length=6000)
    scope = models.CharField(max_length=200, blank=True)
    preferred_contact = models.CharField(max_length=20, blank=True, default='Email')
    message = models.TextField(max_length=4000, blank=True)
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default='New', db_index=True)
    internal_note = models.TextField(blank=True, max_length=5000)
    ip_hash = models.CharField(max_length=64, blank=True)
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Quote request'
    def __str__(self):
        return f'{self.name} — {self.requirement}'

class UploadedDocument(TimestampedModel):
    quote_request = models.ForeignKey(QuoteRequest, null=True, blank=True, on_delete=models.CASCADE, related_name='documents')
    contact_enquiry = models.ForeignKey(ContactEnquiry, null=True, blank=True, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to=private_upload_path, max_length=500)
    original_name = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100, blank=True)
    size_bytes = models.PositiveBigIntegerField(default=0)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return self.original_name

class MediaAsset(TimestampedModel):
    CATEGORY_CHOICES = [
        ('Hero', 'Hero'), ('Solutions', 'Solutions'), ('Products', 'Products'),
        ('Projects', 'Projects'), ('Industries', 'Industries'), ('Services', 'Services'), ('Other', 'Other'),
    ]
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
    title = models.CharField(max_length=180)
    category = models.CharField(max_length=24, choices=CATEGORY_CHOICES, default='Other', db_index=True)
    file = models.FileField(upload_to=public_media_upload_path, max_length=500)
    alt_text = models.CharField(max_length=255, help_text='Describe the image for accessibility; do not use keyword stuffing.')
    is_published = models.BooleanField(default=False, db_index=True)
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Media asset'
    def clean(self):
        from django.core.exceptions import ValidationError
        from PIL import Image, UnidentifiedImageError
        if not self.file:
            return
        suffix = Path(self.file.name).suffix.lower()
        if suffix not in self.ALLOWED_EXTENSIONS:
            raise ValidationError({'file': 'Only JPG, PNG and WebP image files are allowed.'})
        if getattr(self.file, 'size', 0) > 10 * 1024 * 1024:
            raise ValidationError({'file': 'Image files must be 10 MB or smaller.'})
        try:
            self.file.seek(0)
            with Image.open(self.file) as image:
                if image.format not in {'JPEG', 'PNG', 'WEBP'}:
                    raise ValidationError({'file': 'The file content is not an allowed image format.'})
                if image.width * image.height > 32_000_000:
                    raise ValidationError({'file': 'Please upload an image with dimensions up to 32 megapixels.'})
                image.verify()
        except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError):
            raise ValidationError({'file': 'The uploaded image could not be validated.'})
        finally:
            try: self.file.seek(0)
            except Exception: pass
    def __str__(self): return self.title

class ProductCategory(TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    def __str__(self): return self.name

class Product(TimestampedModel):
    OWNERSHIP = [('nexage', 'NexAge Solution'), ('partner', 'Partner Product'), ('integrated', 'Integrated Solution')]
    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name='products')
    description = models.TextField()
    ownership = models.CharField(max_length=20, choices=OWNERSHIP, default='integrated')
    image_path = models.CharField(max_length=255, blank=True, help_text='Frontend public image path; do not store an external executable URL.')
    features = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=True, db_index=True)
    def __str__(self): return self.title

class ProjectCategory(TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    def __str__(self): return self.name

class Project(TimestampedModel):
    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(ProjectCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name='projects')
    industry = models.CharField(max_length=160, blank=True)
    challenge = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    application = models.TextField(blank=True)
    technology = models.TextField(blank=True)
    result = models.TextField(blank=True, help_text='Only enter results supported by approved project records.')
    image_path = models.CharField(max_length=255, blank=True)
    is_published = models.BooleanField(default=True, db_index=True)
    def __str__(self): return self.title

class Partner(TimestampedModel):
    name = models.CharField(max_length=160)
    relationship = models.CharField(max_length=220)
    description = models.TextField(blank=True)
    official_logo_path = models.CharField(max_length=255, blank=True, help_text='Path to an approved official logo asset.')
    is_published = models.BooleanField(default=True)
    def __str__(self): return self.name

class Service(TimestampedModel):
    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image_path = models.CharField(max_length=255, blank=True)
    is_published = models.BooleanField(default=True)
    def __str__(self): return self.title

class Award(TimestampedModel):
    title = models.CharField(max_length=180)
    period = models.CharField(max_length=40, blank=True)
    issuer = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    certificate_file = models.FileField(upload_to=private_upload_path, blank=True, max_length=500)
    is_published = models.BooleanField(default=True)
    def __str__(self): return f'{self.title} {self.period}'.strip()

class Industry(TimestampedModel):
    name = models.CharField(max_length=160, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image_path = models.CharField(max_length=255, blank=True)
    is_published = models.BooleanField(default=True)
    def __str__(self): return self.name


class NewsUpdate(TimestampedModel):
    CATEGORY_CHOICES = [
        ('Company News', 'Company News'),
        ('Project Update', 'Project Update'),
        ('Achievement', 'Achievement'),
        ('Event', 'Event / Exhibition'),
        ('Technology', 'Technology'),
    ]
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.CharField(max_length=24, choices=CATEGORY_CHOICES, default='Company News', db_index=True)
    summary = models.CharField(max_length=320)
    content = models.TextField()
    cover_image = models.FileField(upload_to=news_update_upload_path, blank=True, max_length=500)
    image_alt_text = models.CharField(max_length=255, blank=True)
    video_url = models.URLField(blank=True, max_length=500, help_text='Optional public HTTPS YouTube or Vimeo link. Videos are embedded from the link; upload photos directly.')
    published_at = models.DateTimeField(default=timezone.now, db_index=True)
    is_published = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'News & company update'
        verbose_name_plural = 'News & company updates'

    def clean(self):
        from urllib.parse import urlparse
        from django.core.exceptions import ValidationError
        from PIL import Image, UnidentifiedImageError

        super().clean()
        if self.video_url:
            parsed = urlparse(self.video_url.strip())
            host = (parsed.hostname or '').lower().removeprefix('www.')
            allowed_hosts = {
                'youtube.com', 'm.youtube.com', 'youtu.be', 'youtube-nocookie.com',
                'vimeo.com', 'player.vimeo.com',
            }
            if parsed.scheme != 'https' or host not in allowed_hosts:
                raise ValidationError({'video_url': 'Use a valid HTTPS YouTube or Vimeo URL.'})

        if not self.cover_image:
            return
        suffix = Path(self.cover_image.name).suffix.lower()
        if suffix not in self.ALLOWED_IMAGE_EXTENSIONS:
            raise ValidationError({'cover_image': 'Only JPG, PNG and WebP image files are allowed.'})
        if getattr(self.cover_image, 'size', 0) > 10 * 1024 * 1024:
            raise ValidationError({'cover_image': 'Image files must be 10 MB or smaller.'})
        try:
            self.cover_image.seek(0)
            with Image.open(self.cover_image) as image:
                if image.format not in {'JPEG', 'PNG', 'WEBP'}:
                    raise ValidationError({'cover_image': 'The file content is not an allowed image format.'})
                if image.width * image.height > 32_000_000:
                    raise ValidationError({'cover_image': 'Please upload an image with dimensions up to 32 megapixels.'})
                image.verify()
        except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError):
            raise ValidationError({'cover_image': 'The uploaded image could not be validated.'})
        finally:
            try:
                self.cover_image.seek(0)
            except Exception:
                pass

    def __str__(self):
        return self.title
