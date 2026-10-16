# Generated for the NewsUpdate content feature.
from django.db import migrations, models
import django.utils.timezone
import core.models


class Migration(migrations.Migration):
    dependencies = [('core', '0002_mediaasset')]

    operations = [
        migrations.CreateModel(
            name='NewsUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=180)),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('category', models.CharField(choices=[('Company News', 'Company News'), ('Project Update', 'Project Update'), ('Achievement', 'Achievement'), ('Event', 'Event / Exhibition'), ('Technology', 'Technology')], db_index=True, default='Company News', max_length=24)),
                ('summary', models.CharField(max_length=320)),
                ('content', models.TextField()),
                ('cover_image', models.FileField(blank=True, max_length=500, upload_to=core.models.news_update_upload_path)),
                ('image_alt_text', models.CharField(blank=True, max_length=255)),
                ('video_url', models.URLField(blank=True, help_text='Optional public HTTPS YouTube or Vimeo link. Videos are embedded from the link; upload photos directly.', max_length=500)),
                ('published_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('is_published', models.BooleanField(db_index=True, default=False)),
            ],
            options={
                'verbose_name': 'News & company update',
                'verbose_name_plural': 'News & company updates',
                'ordering': ['-published_at', '-created_at'],
            },
        ),
    ]
