from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from .models import ContactEnquiry, NewsUpdate, QuoteRequest

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
