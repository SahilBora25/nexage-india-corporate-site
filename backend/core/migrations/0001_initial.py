# Generated for the initial NexAge catalogue and enquiry workflow.
from django.db import migrations, models
import django.db.models.deletion
import core.models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='ContactEnquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=120)), ('company', models.CharField(blank=True, max_length=160)),
                ('email', models.EmailField(max_length=254)), ('phone', models.CharField(blank=True, max_length=32)),
                ('requirement', models.CharField(blank=True, max_length=180)), ('message', models.TextField(max_length=5000)),
                ('status', models.CharField(choices=[('New', 'New'), ('Contacted', 'Contacted'), ('In Progress', 'In Progress'), ('Quoted', 'Quoted'), ('Won', 'Won'), ('Closed', 'Closed')], db_index=True, default='New', max_length=24)),
                ('internal_note', models.TextField(blank=True, max_length=5000)), ('ip_hash', models.CharField(blank=True, help_text='Optional hashed source address for abuse analysis; never stores raw IP.', max_length=64)),
            ], options={'verbose_name': 'Contact enquiry', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Industry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=160, unique=True)), ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True)), ('image_path', models.CharField(blank=True, max_length=255)), ('is_published', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=160)), ('relationship', models.CharField(max_length=220)), ('description', models.TextField(blank=True)),
                ('official_logo_path', models.CharField(blank=True, help_text='Path to an approved official logo asset.', max_length=255)), ('is_published', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True)), ('slug', models.SlugField(unique=True)), ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True)), ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuoteRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=120)), ('company', models.CharField(max_length=160)), ('job_title', models.CharField(blank=True, max_length=120)),
                ('email', models.EmailField(max_length=254)), ('phone', models.CharField(max_length=32)), ('location', models.CharField(blank=True, max_length=180)),
                ('requirement', models.CharField(max_length=180)), ('project_requirement', models.TextField(max_length=6000)), ('scope', models.CharField(blank=True, max_length=200)),
                ('preferred_contact', models.CharField(blank=True, default='Email', max_length=20)), ('message', models.TextField(blank=True, max_length=4000)),
                ('status', models.CharField(choices=[('New', 'New'), ('Contacted', 'Contacted'), ('In Progress', 'In Progress'), ('Quoted', 'Quoted'), ('Won', 'Won'), ('Closed', 'Closed')], db_index=True, default='New', max_length=24)),
                ('internal_note', models.TextField(blank=True, max_length=5000)), ('ip_hash', models.CharField(blank=True, max_length=64)),
            ], options={'verbose_name': 'Quote request', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=180)), ('slug', models.SlugField(unique=True)), ('description', models.TextField()),
                ('image_path', models.CharField(blank=True, max_length=255)), ('is_published', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=180)), ('period', models.CharField(blank=True, max_length=40)), ('issuer', models.CharField(blank=True, max_length=160)),
                ('description', models.TextField(blank=True)), ('certificate_file', models.FileField(blank=True, max_length=500, upload_to=core.models.private_upload_path)), ('is_published', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=180)), ('slug', models.SlugField(unique=True)), ('description', models.TextField()),
                ('ownership', models.CharField(choices=[('nexage', 'NexAge Solution'), ('partner', 'Partner Product'), ('integrated', 'Integrated Solution')], default='integrated', max_length=20)),
                ('image_path', models.CharField(blank=True, help_text='Frontend public image path; do not store an external executable URL.', max_length=255)),
                ('features', models.JSONField(blank=True, default=list)), ('is_published', models.BooleanField(db_index=True, default=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='core.productcategory')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=180)), ('slug', models.SlugField(unique=True)), ('industry', models.CharField(blank=True, max_length=160)),
                ('challenge', models.TextField(blank=True)), ('solution', models.TextField(blank=True)), ('application', models.TextField(blank=True)),
                ('technology', models.TextField(blank=True)), ('result', models.TextField(blank=True, help_text='Only enter results supported by approved project records.')),
                ('image_path', models.CharField(blank=True, max_length=255)), ('is_published', models.BooleanField(db_index=True, default=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projects', to='core.projectcategory')),
            ],
        ),
        migrations.CreateModel(
            name='UploadedDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
                ('file', models.FileField(max_length=500, upload_to=core.models.private_upload_path)), ('original_name', models.CharField(max_length=255)),
                ('mime_type', models.CharField(blank=True, max_length=100)), ('size_bytes', models.PositiveBigIntegerField(default=0)),
                ('contact_enquiry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='core.contactenquiry')),
                ('quote_request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='core.quoterequest')),
            ], options={'ordering': ['-created_at']},
        ),
    ]
