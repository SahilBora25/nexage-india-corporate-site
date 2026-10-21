from io import StringIO
from pathlib import Path
import tempfile
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.throttling import AnonRateThrottle
from .models import ContactEnquiry, NewsUpdate, Product, Project, QuoteRequest, Service, UploadedDocument

class EnquiryWorkflowTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_contact_submission_persists(self):
        # Use the locmem email backend in the test process to avoid real SMTP.
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            response = self.client.post('/api/enquiries/contact/', {
                'name': 'A Test Customer', 'company': 'Example Manufacturing', 'email': 'customer@example.com',
                'phone': '+91 90000 00000', 'requirement': 'Conveyor integration',
                'message': 'We need support for a production conveyor.',
            }, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContactEnquiry.objects.count(), 1)
        self.assertEqual(ContactEnquiry.objects.first().status, 'New')

    def test_quote_requires_project_description(self):
        response = self.client.post('/api/enquiries/quote/', {
            'name': 'A Test Customer', 'company': 'Example Manufacturing', 'email': 'customer@example.com',
            'phone': '+91 90000 00000', 'requirement': 'Industrial Automation', 'project_requirement': 'short',
        }, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(QuoteRequest.objects.count(), 0)


class ReadinessCheckTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_healthcheck_reports_ready_when_database_and_cache_respond(self):
        response = self.client.get('/healthz/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})

    @patch('config.urls.connections')
    def test_healthcheck_reports_unavailable_when_database_is_unreachable(self, connections):
        connections.__getitem__.return_value.ensure_connection.side_effect = OSError('database unavailable')
        response = self.client.get('/healthz/')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {'status': 'unavailable'})

    @patch('config.urls.cache.get', side_effect=OSError('cache unavailable'))
    def test_healthcheck_reports_unavailable_when_cache_is_unreachable(self, _cache_get):
        response = self.client.get('/healthz/')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {'status': 'unavailable'})


@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'quote-reliability-tests'}})
class QuoteStorageReliabilityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.raise_request_exception = False
        self.payload = {
            'name': 'Test Customer', 'company': 'Example Manufacturing', 'email': 'customer@example.com',
            'phone': '+91 90000 00000', 'requirement': 'Conveyor integration',
            'project_requirement': 'We need an assembly conveyor integration.',
        }
        cache.clear()

    def make_upload(self):
        return SimpleUploadedFile('drawing.pdf', b'%PDF-1.4\nTest drawing', content_type='application/pdf')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', DEFAULT_FROM_EMAIL='web@example.com', SALES_ENQUIRY_EMAIL='sales@example.com')
    def test_storage_failure_leaves_no_record_and_same_key_retry_succeeds_once(self):
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                storage = default_storage
                original_save = storage.save
                attempts = 0

                def fail_once(name, content):
                    nonlocal attempts
                    attempts += 1
                    if attempts == 1:
                        original_save(name, content)
                        raise OSError('storage interrupted after writing')
                    return original_save(name, content)

                with patch('core.views.default_storage.save', side_effect=fail_once):
                    failed = self.client.post(
                        '/api/enquiries/quote/',
                        {**self.payload, 'attachment': self.make_upload()},
                        format='multipart', HTTP_IDEMPOTENCY_KEY='quote-retry-key-0001',
                    )
                    self.assertEqual(failed.status_code, 503)
                    self.assertEqual(QuoteRequest.objects.count(), 0)
                    self.assertEqual(UploadedDocument.objects.count(), 0)

                    retried = self.client.post(
                        '/api/enquiries/quote/',
                        {**self.payload, 'attachment': self.make_upload()},
                        format='multipart', HTTP_IDEMPOTENCY_KEY='quote-retry-key-0001',
                    )

                self.assertEqual(retried.status_code, 201)
                self.assertEqual(QuoteRequest.objects.count(), 1)
                self.assertEqual(UploadedDocument.objects.count(), 1)
                document = UploadedDocument.objects.get()
                self.assertTrue((Path(media_root) / document.file.name).is_file())
                self.assertEqual(len(list(Path(media_root).rglob('*.pdf'))), 1)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', DEFAULT_FROM_EMAIL='web@example.com', SALES_ENQUIRY_EMAIL='sales@example.com')
    def test_retry_after_success_returns_same_quote_without_duplicate(self):
        for _ in range(2):
            response = self.client.post(
                '/api/enquiries/quote/', self.payload, format='multipart',
                HTTP_IDEMPOTENCY_KEY='quote-retry-key-0002',
            )
            self.assertEqual(response.status_code, 201)
            if _ == 0:
                first_response = response.data
            else:
                self.assertEqual(response.data, first_response)
        self.assertEqual(QuoteRequest.objects.count(), 1)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', DEFAULT_FROM_EMAIL='web@example.com', SALES_ENQUIRY_EMAIL='sales@example.com')
    def test_database_document_failure_rolls_back_quote_and_removes_saved_file(self):
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                with patch('core.views.UploadedDocument.objects.create', side_effect=OSError('database insert failed')):
                    response = self.client.post(
                        '/api/enquiries/quote/',
                        {**self.payload, 'attachment': self.make_upload()},
                        format='multipart', HTTP_IDEMPOTENCY_KEY='quote-retry-key-0003',
                    )
                self.assertEqual(response.status_code, 503)
                self.assertEqual(QuoteRequest.objects.count(), 0)
                self.assertEqual(UploadedDocument.objects.count(), 0)
                self.assertEqual(list(Path(media_root).rglob('*.*')), [])

    def test_invalid_file_extension_is_rejected(self):
        invalid = SimpleUploadedFile('program.exe', b'MZ-executable-content', content_type='application/octet-stream')
        response = self.client.post('/api/enquiries/quote/', {
            'name': 'A Test Customer', 'company': 'Example Manufacturing', 'email': 'customer@example.com',
            'phone': '+91 90000 00000', 'requirement': 'Industrial Automation', 'project_requirement': 'We need an assembly workstation integration.',
            'attachment': invalid,
        }, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(QuoteRequest.objects.count(), 0)


class NewsUpdatePublicApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_only_published_and_due_updates_are_public(self):
        published = NewsUpdate.objects.create(
            title='Completed conveyor integration',
            slug='completed-conveyor-integration',
            category='Project Update',
            summary='A completed integration update.',
            content='The project update details.',
            is_published=True,
        )
        draft = NewsUpdate.objects.create(
            title='Draft company milestone',
            slug='draft-company-milestone',
            summary='This draft must stay private.',
            content='Draft details.',
            is_published=False,
        )
        future = NewsUpdate.objects.create(
            title='Future exhibition',
            slug='future-exhibition',
            summary='This update is scheduled for later.',
            content='Future details.',
            published_at=timezone.now() + timezone.timedelta(days=1),
            is_published=True,
        )

        response = self.client.get('/api/news/')
        self.assertEqual(response.status_code, 200)
        visible_ids = {item['id'] for item in response.data}
        self.assertIn(published.id, visible_ids)
        self.assertNotIn(draft.id, visible_ids)
        self.assertNotIn(future.id, visible_ids)

    def test_image_route_does_not_disclose_draft_updates(self):
        draft = NewsUpdate.objects.create(
            title='Unpublished update',
            slug='unpublished-update',
            summary='Not public.',
            content='Not public.',
            is_published=False,
        )
        response = self.client.get(f'/api/news/{draft.id}/image/')
        self.assertEqual(response.status_code, 404)


class ProxyThrottleIdentityTests(TestCase):
    def test_anonymous_throttle_rate_has_the_existing_default(self):
        self.assertEqual(AnonRateThrottle().get_rate(), '100/day')

    def test_anonymous_throttle_uses_single_proxy_client_address(self):
        request = APIRequestFactory().get(
            '/',
            HTTP_X_FORWARDED_FOR='198.51.100.42',
            REMOTE_ADDR='172.20.0.3',
        )
        self.assertEqual(AnonRateThrottle().get_ident(request), '198.51.100.42')

    def test_nginx_replaces_incoming_forwarded_for_chain(self):
        project_root = Path(__file__).resolve().parents[2]
        nginx_config = (project_root / 'nginx.conf').read_text(encoding='utf-8')
        self.assertEqual(
            nginx_config.count('proxy_set_header X-Forwarded-For $remote_addr;'),
            2,
        )
        self.assertNotIn('$proxy_add_x_forwarded_for', nginx_config)


class EnquiryNotificationFailureTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.payload = {
            'name': 'Test Customer',
            'company': 'Example Manufacturing',
            'email': 'customer@example.com',
            'phone': '+91 90000 00000',
            'requirement': 'Conveyor integration',
            'message': 'A test-only enquiry.',
        }

    @patch('core.views.send_mail', side_effect=OSError('private SMTP detail'))
    def test_staff_mail_failure_keeps_saved_enquiry_and_api_contract(self, _send_mail):
        with self.settings(
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
            SEND_CUSTOMER_CONFIRMATION=False,
        ):
            with self.assertLogs('core.views', level='ERROR') as captured:
                response = self.client.post(
                    '/api/enquiries/contact/',
                    self.payload,
                    format='multipart',
                )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(set(response.data), {'received', 'id', 'message'})
        self.assertEqual(ContactEnquiry.objects.count(), 1)
        log_output = '\n'.join(captured.output)
        self.assertIn('staff_enquiry_notification_failed', log_output)
        self.assertIn('record_kind=contact', log_output)
        self.assertNotIn('customer@example.com', log_output)
        self.assertNotIn('private SMTP detail', log_output)

    @patch('core.views.send_mail', side_effect=[1, OSError('private SMTP detail')])
    def test_customer_confirmation_failure_is_separately_observable(self, _send_mail):
        with self.settings(
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
            SEND_CUSTOMER_CONFIRMATION=True,
        ):
            with self.assertLogs('core.views', level='ERROR') as captured:
                response = self.client.post(
                    '/api/enquiries/contact/',
                    self.payload,
                    format='multipart',
                )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContactEnquiry.objects.count(), 1)
        log_output = '\n'.join(captured.output)
        self.assertIn('customer_confirmation_email_failed', log_output)
        self.assertNotIn('customer@example.com', log_output)
        self.assertNotIn('private SMTP detail', log_output)

    @patch('core.views.send_mail', return_value=0)
    def test_zero_message_count_is_logged_as_a_delivery_failure(self, _send_mail):
        with self.settings(
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
            SEND_CUSTOMER_CONFIRMATION=False,
        ):
            with self.assertLogs('core.views', level='ERROR') as captured:
                response = self.client.post(
                    '/api/enquiries/contact/',
                    self.payload,
                    format='multipart',
                )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContactEnquiry.objects.count(), 1)
        self.assertIn('staff_enquiry_notification_failed', '\n'.join(captured.output))


class CatalogueSeedCommandTests(TestCase):
    def test_seed_catalog_is_repeatable_and_preserves_existing_edits(self):
        call_command('seed_catalog', stdout=StringIO())
        product_count = Product.objects.count()
        service_count = Service.objects.count()
        product = Product.objects.get(slug='jidoka')
        product.title = 'Admin-approved Jidoka title'
        product.save(update_fields=['title', 'updated_at'])

        call_command('seed_catalog', stdout=StringIO())

        self.assertEqual(Product.objects.count(), product_count)
        self.assertEqual(Service.objects.count(), service_count)
        product.refresh_from_db()
        self.assertEqual(product.title, 'Admin-approved Jidoka title')

    def test_catalogue_image_manifest_seeds_expected_slugs_and_sync_preserves_existing_paths(self):
        from core.catalogue_images import CATALOGUE_IMAGE_MAPS

        call_command('seed_catalog', stdout=StringIO())
        product = Product.objects.get(slug='jidoka')
        project = Project.objects.get(slug='jigs-fixtures-project')
        self.assertEqual(product.image_path, CATALOGUE_IMAGE_MAPS['products']['jidoka'])
        self.assertEqual(project.image_path, CATALOGUE_IMAGE_MAPS['projects']['jigs-fixtures-project'])
        public_products = APIClient().get('/api/products/')
        public_projects = APIClient().get('/api/projects/')
        self.assertEqual(public_products.status_code, 200)
        self.assertEqual(public_projects.status_code, 200)
        self.assertEqual(next(row for row in public_products.data if row['slug'] == 'jidoka')['image_path'], CATALOGUE_IMAGE_MAPS['products']['jidoka'])
        self.assertEqual(next(row for row in public_projects.data if row['slug'] == 'jigs-fixtures-project')['image_path'], CATALOGUE_IMAGE_MAPS['projects']['jigs-fixtures-project'])

        product.image_path = 'admin-selected-product-image.webp'
        product.save(update_fields=['image_path', 'updated_at'])
        project.image_path = ''
        project.save(update_fields=['image_path', 'updated_at'])
        call_command('sync_catalog_images', '--apply', stdout=StringIO())

        product.refresh_from_db()
        project.refresh_from_db()
        self.assertEqual(product.image_path, 'admin-selected-product-image.webp')
        self.assertEqual(project.image_path, CATALOGUE_IMAGE_MAPS['projects']['jigs-fixtures-project'])
