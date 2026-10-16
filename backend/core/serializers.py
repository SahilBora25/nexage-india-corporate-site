from rest_framework import serializers
from .models import Award, Industry, MediaAsset, NewsUpdate, Partner, Product, ProductCategory, Project, ProjectCategory, Service, ContactEnquiry, QuoteRequest, UploadedDocument

class ContactEnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactEnquiry
        fields = ['id', 'name', 'company', 'email', 'phone', 'requirement', 'message', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']
    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2: raise serializers.ValidationError('Please enter your name.')
        return value
    def validate_message(self, value):
        value = value.strip()
        if len(value) < 5: raise serializers.ValidationError('Please add a little more detail to your message.')
        return value

class QuoteRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteRequest
        fields = ['id', 'name', 'company', 'job_title', 'email', 'phone', 'location', 'requirement', 'project_requirement', 'scope', 'preferred_contact', 'message', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']
    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2: raise serializers.ValidationError('Please enter your full name.')
        return value
    def validate_company(self, value):
        value = value.strip()
        if not value: raise serializers.ValidationError('Please enter your company name.')
        return value
    def validate_project_requirement(self, value):
        value = value.strip()
        if len(value) < 10: raise serializers.ValidationError('Please describe your project requirement in a little more detail.')
        return value

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta: model = ProductCategory; fields = ['id', 'name', 'slug', 'description']
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta: model = Product; fields = ['id', 'title', 'slug', 'category', 'category_name', 'description', 'ownership', 'image_path', 'features', 'is_published', 'created_at', 'updated_at']
class ProjectCategorySerializer(serializers.ModelSerializer):
    class Meta: model = ProjectCategory; fields = ['id', 'name', 'slug']
class ProjectSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta: model = Project; fields = ['id', 'title', 'slug', 'category', 'category_name', 'industry', 'challenge', 'solution', 'application', 'technology', 'result', 'image_path', 'is_published', 'created_at', 'updated_at']
class PartnerSerializer(serializers.ModelSerializer):
    class Meta: model = Partner; fields = ['id', 'name', 'relationship', 'description', 'official_logo_path', 'is_published']
class ServiceSerializer(serializers.ModelSerializer):
    class Meta: model = Service; fields = ['id', 'title', 'slug', 'description', 'image_path', 'is_published']
class AwardSerializer(serializers.ModelSerializer):
    class Meta: model = Award; fields = ['id', 'title', 'period', 'issuer', 'description', 'is_published']
class IndustrySerializer(serializers.ModelSerializer):
    class Meta: model = Industry; fields = ['id', 'name', 'slug', 'description', 'image_path', 'is_published']


class MediaAssetSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True, required=False)
    file_url = serializers.SerializerMethodField()
    class Meta:
        model = MediaAsset
        fields = ['id', 'title', 'category', 'file', 'file_url', 'alt_text', 'is_published', 'created_at', 'updated_at']
        read_only_fields = ['id', 'file_url', 'created_at', 'updated_at']
    def get_file_url(self, obj):
        return f'/api/media/{obj.pk}/file/'
    def validate_file(self, upload):
        from pathlib import Path
        from PIL import Image, UnidentifiedImageError
        if Path(upload.name).suffix.lower() not in MediaAsset.ALLOWED_EXTENSIONS:
            raise serializers.ValidationError('Only JPG, PNG and WebP image files are allowed.')
        if upload.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('Image files must be 10 MB or smaller.')
        try:
            upload.seek(0)
            with Image.open(upload) as image:
                if image.format not in {'JPEG', 'PNG', 'WEBP'}:
                    raise serializers.ValidationError('The file content is not an allowed image format.')
                if image.width * image.height > 32_000_000:
                    raise serializers.ValidationError('Please upload an image with dimensions up to 32 megapixels.')
                image.verify()
        except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError):
            raise serializers.ValidationError('The uploaded image could not be validated.')
        finally:
            upload.seek(0)
        return upload
    def validate(self, attrs):
        if self.instance is None and not attrs.get('file'):
            raise serializers.ValidationError({'file': 'An image file is required.'})
        return attrs


class NewsUpdateSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = NewsUpdate
        fields = ['id', 'title', 'slug', 'category', 'summary', 'content', 'image_url', 'image_alt_text', 'video_url', 'published_at']
        read_only_fields = fields

    def get_image_url(self, obj):
        return f'/api/news/{obj.pk}/image/' if obj.cover_image else ''
