from django.db import migrations, models
import core.models

class Migration(migrations.Migration):
    dependencies = [('core', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='MediaAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=180)),
                ('category', models.CharField(choices=[('Hero', 'Hero'), ('Solutions', 'Solutions'), ('Products', 'Products'), ('Projects', 'Projects'), ('Industries', 'Industries'), ('Services', 'Services'), ('Other', 'Other')], db_index=True, default='Other', max_length=24)),
                ('file', models.FileField(max_length=500, upload_to=core.models.public_media_upload_path)),
                ('alt_text', models.CharField(help_text='Describe the image for accessibility; do not use keyword stuffing.', max_length=255)),
                ('is_published', models.BooleanField(db_index=True, default=False)),
            ],
            options={'verbose_name': 'Media asset', 'ordering': ['-created_at']},
        ),
    ]
