from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Award, ContactEnquiry, Industry, MediaAsset, NewsUpdate, Partner, Product, ProductCategory, Project, ProjectCategory, QuoteRequest, Service, UploadedDocument

@admin.register(ContactEnquiry)
class ContactEnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'requirement', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'company', 'email', 'phone', 'requirement', 'message')
    readonly_fields = ('created_at', 'updated_at', 'ip_hash')
    list_editable = ('status',)

@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'requirement', 'email', 'status', 'created_at')
    list_filter = ('status', 'requirement', 'created_at')
    search_fields = ('name', 'company', 'email', 'phone', 'requirement', 'project_requirement')
    readonly_fields = ('created_at', 'updated_at', 'ip_hash')
    list_editable = ('status',)

@admin.register(UploadedDocument)
class UploadedDocumentAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'mime_type', 'size_bytes', 'created_at')
    search_fields = ('original_name',)
    readonly_fields = ('file', 'original_name', 'mime_type', 'size_bytes', 'created_at', 'updated_at')

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'ownership', 'is_published', 'updated_at')
    list_filter = ('ownership', 'is_published', 'category')
    search_fields = ('title', 'description', 'slug')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'industry', 'is_published', 'updated_at')
    list_filter = ('is_published', 'category')
    search_fields = ('title', 'industry', 'challenge', 'solution', 'application')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'relationship', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('name', 'relationship')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'updated_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ('title', 'period', 'issuer', 'is_published')
    list_filter = ('issuer', 'is_published')
    search_fields = ('title', 'period', 'issuer', 'description')

@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'title', 'category', 'is_published', 'updated_at')
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'alt_text')
    readonly_fields = ('created_at', 'updated_at')

    @admin.display(description='Preview')
    def thumbnail(self, obj):
        if not obj.pk or not obj.file:
            return '—'
        return format_html('<img src="{}" alt="" style="max-width:88px;max-height:54px;object-fit:cover;border:1px solid #ddd;" />', reverse('media-asset-file', args=[obj.pk]))


@admin.register(NewsUpdate)
class NewsUpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'published_at', 'is_published', 'updated_at')
    list_filter = ('is_published', 'category', 'published_at')
    search_fields = ('title', 'summary', 'content', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'published_at'
    fieldsets = (
        ('Update details', {'fields': ('title', 'slug', 'category', 'summary', 'content')}),
        ('Photo and video', {'fields': ('cover_image', 'image_alt_text', 'video_url')}),
        ('Publishing', {'fields': ('published_at', 'is_published')}),
        ('Record timestamps', {'fields': ('created_at', 'updated_at')}),
    )
