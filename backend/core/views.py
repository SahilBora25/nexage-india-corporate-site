import csv
import hashlib
import json
import logging
import mimetypes
import re
import zipfile
from pathlib import Path
from uuid import uuid4
from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.http import FileResponse, Http404, HttpResponse
from django.middleware.csrf import get_token, CsrfViewMiddleware
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser, SAFE_METHODS, BasePermission
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from .models import Award, Industry, MediaAsset, NewsUpdate, Partner, Product, Project, Service, ContactEnquiry, QuoteRequest, UploadedDocument
from .serializers import AwardSerializer, ContactEnquirySerializer, IndustrySerializer, MediaAssetSerializer, NewsUpdateSerializer, PartnerSerializer, ProductSerializer, ProjectSerializer, QuoteRequestSerializer, ServiceSerializer

logger = logging.getLogger(__name__)
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.docx', '.xlsx'}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
STATUS_VALUES = {'New', 'Contacted', 'In Progress', 'Quoted', 'Won', 'Closed'}

class ContactThrottle(AnonRateThrottle): scope = 'contact'
class QuoteThrottle(AnonRateThrottle): scope = 'quote'
class AuthThrottle(AnonRateThrottle): scope = 'auth'

class ReadOnlyOrStaff(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or bool(request.user and request.user.is_staff)

def get_user_ip_hash(request):
    # Raw IP addresses are not persisted; leave this blank unless an organization-approved
    # one-way hashing/salting policy is configured in deployment.
    return ''

def send_enquiry_notifications(subject, body, record_kind, record_id, customer_email=None, customer_name=None):
    delivery = {'staff_sent': False, 'customer_confirmation_sent': None}
    try:
        sent_count = send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.SALES_ENQUIRY_EMAIL], fail_silently=False)
        if sent_count != 1:
            raise RuntimeError('Email backend reported that the staff notification was not sent.')
    except Exception as exc:
        # Keep the established API success response because the enquiry is already
        # saved. Emit a searchable, PII-free event so operations can follow up.
        logger.error(
            'staff_enquiry_notification_failed record_kind=%s record_id=%s error_type=%s',
            record_kind,
            record_id,
            type(exc).__name__,
        )
    else:
        delivery['staff_sent'] = True
    if settings.SEND_CUSTOMER_CONFIRMATION and customer_email:
        try:
            sent_count = send_mail(
                'We received your enquiry - NexAge India',
                f'Hello {customer_name or "there"},\n\nThank you for contacting NexAge India. Your enquiry has been received. Our team will contact you shortly.\n\nRegards,\nNexAge India Pvt. Ltd.\n{settings.SALES_ENQUIRY_EMAIL}',
                settings.DEFAULT_FROM_EMAIL,
                [customer_email],
                fail_silently=False,
            )
            if sent_count != 1:
                raise RuntimeError('Email backend reported that the customer confirmation was not sent.')
        except Exception as exc:
            logger.error(
                'customer_confirmation_email_failed record_kind=%s record_id=%s error_type=%s',
                record_kind,
                record_id,
                type(exc).__name__,
            )
            delivery['customer_confirmation_sent'] = False
        else:
            delivery['customer_confirmation_sent'] = True
    return delivery

def notification_body(kind, data, request):
    stamp = timezone.localtime(timezone.now()).strftime('%d %b %Y, %I:%M %p %Z')
    lines = [
        f'Type: {kind}', f'Customer: {data.get("name", "")}', f'Company: {data.get("company", "")}',
        f'Email: {data.get("email", "")}', f'Phone: {data.get("phone", "")}',
        f'Requirement: {data.get("requirement", "")}', f'Location: {data.get("location", "")}',
        f'Scope: {data.get("scope", "")}', f'Preferred contact: {data.get("preferred_contact", "")}',
        f'Message / project requirement: {data.get("project_requirement", data.get("message", ""))}',
        f'Additional message: {data.get("message", "")}', f'Date/time: {stamp}',
    ]
    return '\n'.join(lines)

def check_upload(upload):
    if not upload: return None
    suffix = Path(upload.name).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        return 'File type not supported. Upload PDF, JPG, PNG, DOCX or XLSX.'
    if upload.size > MAX_UPLOAD_BYTES:
        return 'File is larger than the 10 MB limit.'
    upload.seek(0)
    head = upload.read(16)
    upload.seek(0)
    if suffix == '.pdf' and not head.startswith(b'%PDF-'):
        return 'The uploaded PDF does not appear to be a valid PDF file.'
    if suffix in {'.jpg', '.jpeg'} and not head.startswith(b'\xff\xd8\xff'):
        return 'The uploaded JPEG does not appear to be a valid image.'
    if suffix == '.png' and not head.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'The uploaded PNG does not appear to be a valid image.'
    if suffix in {'.docx', '.xlsx'}:
        try:
            with zipfile.ZipFile(upload) as zf:
                names = set(zf.namelist())
                if '[Content_Types].xml' not in names or (suffix == '.docx' and 'word/document.xml' not in names) or (suffix == '.xlsx' and 'xl/workbook.xml' not in names):
                    return 'The uploaded Office document is not valid.'
        except (zipfile.BadZipFile, OSError):
            return 'The uploaded Office document is not valid.'
        finally:
            upload.seek(0)
    return None

@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_token(request):
    return Response({'csrfToken': get_token(request._request)})

class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]
    parser_classes = [JSONParser]
    def post(self, request):
        csrf_failure = CsrfViewMiddleware(lambda r: None).process_view(request._request, lambda r: None, (), {})
        if csrf_failure is not None:
            return Response({'detail': 'CSRF verification failed. Refresh the page and try again.'}, status=status.HTTP_403_FORBIDDEN)
        username = str(request.data.get('username', '')).strip()
        password = request.data.get('password', '')
        if not username or not isinstance(password, str):
            return Response({'detail': 'Enter a username and password.'}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(request, username=username, password=password)
        if user is None or not user.is_active or not user.is_staff:
            return Response({'detail': 'Invalid credentials or insufficient permission.'}, status=status.HTTP_400_BAD_REQUEST)
        login(request, user)
        request.session.cycle_key()
        return Response({
            'authenticated': True,
            'username': user.get_username(),
            # Django rotates the CSRF secret on login. Return a token for the new
            # cookie so subsequent admin PATCH and logout requests keep working.
            'csrfToken': get_token(request._request),
        })

class LogoutView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [SessionAuthentication]
    def post(self, request):
        logout(request)
        # Logout rotates the CSRF secret too. Keep the admin login form's token
        # in sync so a user can sign back in without refreshing the page.
        return Response({'authenticated': False, 'csrfToken': get_token(request._request)})

class ContactEnquiryCreateView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ContactThrottle]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    def post(self, request):
        if str(request.data.get('website', '')).strip():
            # Honeypot submissions are discarded with a generic acknowledgement.
            return Response({'received': True}, status=status.HTTP_201_CREATED)
        serializer = ContactEnquirySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enquiry = serializer.save(ip_hash=get_user_ip_hash(request))
        send_enquiry_notifications(
            'New NexAge Website Enquiry',
            notification_body('Contact enquiry', serializer.validated_data, request),
            'contact',
            enquiry.pk,
            enquiry.email,
            enquiry.name,
        )
        return Response({'received': True, 'id': enquiry.id, 'message': 'Thank you. Your enquiry has been received. Our team will contact you shortly.'}, status=status.HTTP_201_CREATED)

class QuoteRequestCreateView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [QuoteThrottle]
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request):
        if str(request.data.get('website', '')).strip():
            return Response({'received': True}, status=status.HTTP_201_CREATED)
        upload = request.FILES.get('attachment')
        upload_error = check_upload(upload)
        if upload_error:
            return Response({'detail': upload_error}, status=status.HTTP_400_BAD_REQUEST)
        serializer = QuoteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        idempotency_key = request.headers.get('Idempotency-Key', '').strip()
        reservation = None
        cache_key = None
        if idempotency_key:
            if not re.fullmatch(r'[A-Za-z0-9._:-]{16,128}', idempotency_key):
                return Response({'detail': 'The submission key is invalid. Please refresh the form and try again.'}, status=status.HTTP_400_BAD_REQUEST)
            fingerprint_hash = hashlib.sha256()
            payload = json.dumps(serializer.validated_data, sort_keys=True, separators=(',', ':'), default=str)
            fingerprint_hash.update(payload.encode('utf-8'))
            if upload:
                for chunk in upload.chunks():
                    fingerprint_hash.update(chunk)
                upload.seek(0)
            fingerprint = fingerprint_hash.hexdigest()
            cache_key = f'nexage:quote-idempotency:{hashlib.sha256(idempotency_key.encode("ascii")).hexdigest()}'
            reservation = {'state': 'pending', 'fingerprint': fingerprint, 'owner': uuid4().hex}
            try:
                reserved = cache.add(cache_key, reservation, timeout=86400)
                if not reserved:
                    prior = cache.get(cache_key)
                    if isinstance(prior, dict) and prior.get('fingerprint') != fingerprint:
                        return Response({'detail': 'This submission key was already used for different form data.'}, status=status.HTTP_409_CONFLICT)
                    if isinstance(prior, dict) and prior.get('state') == 'complete':
                        return Response(prior['response'], status=prior['status'])
                    return Response({'detail': 'A request with this key is already being processed. Retry with the same form data.'}, status=status.HTTP_409_CONFLICT)
            except Exception as exc:
                logger.error('quote_idempotency_cache_unavailable error_type=%s', type(exc).__name__)
                return Response({'detail': 'The request could not be safely checked for duplicates. Please retry shortly.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        stored_name = None
        storage = default_storage
        if upload:
            # Store first so a failed storage write cannot leave an enquiry row.
            # The returned storage name is tracked for cleanup if the DB transaction fails.
            document = UploadedDocument()
            storage = document.file.storage
            original_name = Path(str(upload.name).replace('\\', '/')).name[:255]
            storage_path = None
            target_was_absent = False
            try:
                storage_path = document.file.field.generate_filename(document, original_name)
                target_was_absent = not storage.exists(storage_path)
                if not target_was_absent:
                    raise FileExistsError('The generated private upload path is already in use.')
                stored_name = storage.save(storage_path, upload)
            except Exception as exc:
                # A storage backend can write a blob and then raise before returning
                # its final name. The generated UUID path was confirmed absent first.
                if target_was_absent and storage_path:
                    try:
                        if storage.exists(storage_path):
                            storage.delete(storage_path)
                    except Exception as cleanup_exc:
                        logger.error('quote_attachment_cleanup_failed error_type=%s', type(cleanup_exc).__name__)
                logger.error('quote_attachment_storage_failed error_type=%s', type(exc).__name__)
                self._release_reservation(cache_key, reservation)
                return Response({'detail': 'The attachment could not be saved. Please retry the request.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            with transaction.atomic():
                quote = serializer.save(ip_hash=get_user_ip_hash(request))
                if stored_name:
                    # The file has already been written to private storage. Saving its
                    # name creates only the database row and avoids a second storage write.
                    UploadedDocument.objects.create(
                        quote_request=quote,
                        file=stored_name,
                        original_name=original_name,
                        mime_type=mimetypes.guess_type(upload.name)[0] or upload.content_type or '',
                        size_bytes=upload.size,
                    )
        except Exception as exc:
            if stored_name:
                try:
                    storage.delete(stored_name)
                except Exception as cleanup_exc:
                    logger.error('quote_attachment_cleanup_failed error_type=%s', type(cleanup_exc).__name__)
            self._release_reservation(cache_key, reservation)
            logger.error('quote_persistence_failed error_type=%s', type(exc).__name__)
            return Response({'detail': 'The request could not be saved. Please retry using the same submission.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        response_data = {'received': True, 'id': quote.id, 'message': 'Thank you. Your enquiry has been received. Our team will contact you shortly.'}
        if cache_key and reservation:
            try:
                current = cache.get(cache_key)
                if isinstance(current, dict) and current.get('owner') == reservation['owner']:
                    cache.set(cache_key, {'state': 'complete', 'fingerprint': reservation['fingerprint'], 'response': response_data, 'status': status.HTTP_201_CREATED}, timeout=86400)
            except Exception as exc:
                logger.error('quote_idempotency_cache_completion_failed error_type=%s', type(exc).__name__)
        send_enquiry_notifications(
            'New NexAge Website Enquiry',
            notification_body('Request for quote', serializer.validated_data, request),
            'quote',
            quote.pk,
            quote.email,
            quote.name,
        )
        return Response(response_data, status=status.HTTP_201_CREATED)

    @staticmethod
    def _release_reservation(cache_key, reservation):
        if not cache_key or not reservation:
            return
        try:
            current = cache.get(cache_key)
            if isinstance(current, dict) and current.get('owner') == reservation['owner']:
                cache.delete(cache_key)
        except Exception as exc:
            logger.error('quote_idempotency_cache_release_failed error_type=%s', type(exc).__name__)

class PublishedModelViewSet(viewsets.ModelViewSet):
    permission_classes = [ReadOnlyOrStaff]
    authentication_classes = [SessionAuthentication]
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)

class MediaAssetViewSet(viewsets.ModelViewSet):
    serializer_class = MediaAssetSerializer
    permission_classes = [ReadOnlyOrStaff]
    authentication_classes = [SessionAuthentication]
    queryset = MediaAsset.objects.all()
    def get_queryset(self):
        if self.request.user and self.request.user.is_staff:
            return MediaAsset.objects.all()
        return MediaAsset.objects.filter(is_published=True)

class MediaAssetFileView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]
    def get(self, request, pk):
        try:
            asset = MediaAsset.objects.get(pk=pk)
        except MediaAsset.DoesNotExist:
            raise Http404
        if not asset.is_published and not (request.user and request.user.is_staff):
            raise Http404
        try:
            handle = asset.file.open('rb')
        except (FileNotFoundError, OSError, ValueError):
            raise Http404
        suffix = Path(asset.file.name).suffix.lower()
        mime = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp'}.get(suffix, 'application/octet-stream')
        response = FileResponse(handle, content_type=mime, filename=Path(asset.file.name).name, as_attachment=False)
        response['X-Content-Type-Options'] = 'nosniff'
        response['Content-Security-Policy'] = "default-src 'none'; sandbox"
        response['Cache-Control'] = 'public, max-age=3600' if asset.is_published else 'private, no-store'
        return response

class NewsUpdateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NewsUpdateSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_queryset(self):
        return NewsUpdate.objects.filter(
            is_published=True,
            published_at__lte=timezone.now(),
        ).order_by('-published_at', '-created_at')


class NewsUpdateImageView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, pk):
        try:
            update = NewsUpdate.objects.get(
                pk=pk,
                is_published=True,
                published_at__lte=timezone.now(),
            )
        except NewsUpdate.DoesNotExist:
            raise Http404
        if not update.cover_image:
            raise Http404
        try:
            handle = update.cover_image.open('rb')
        except (FileNotFoundError, OSError, ValueError):
            raise Http404
        suffix = Path(update.cover_image.name).suffix.lower()
        mime = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp'}.get(suffix, 'application/octet-stream')
        response = FileResponse(handle, content_type=mime, filename=Path(update.cover_image.name).name, as_attachment=False)
        response['X-Content-Type-Options'] = 'nosniff'
        response['Content-Security-Policy'] = "default-src 'none'; sandbox"
        response['Cache-Control'] = 'public, max-age=3600'
        return response


class ProductViewSet(PublishedModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
class ProjectViewSet(PublishedModelViewSet):
    queryset = Project.objects.select_related('category').all()
    serializer_class = ProjectSerializer
class ServiceViewSet(PublishedModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
class PartnerViewSet(PublishedModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
class AwardViewSet(PublishedModelViewSet):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer
class IndustryViewSet(PublishedModelViewSet):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer

class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [SessionAuthentication]
    def get(self, request):
        contacts = ContactEnquiry.objects.all()
        quotes = QuoteRequest.objects.all()
        total = contacts.count() + quotes.count()
        new_count = contacts.filter(status='New').count() + quotes.filter(status='New').count()
        closed = contacts.filter(status__in=['Won', 'Closed']).count() + quotes.filter(status__in=['Won', 'Closed']).count()
        return Response({
            'total_enquiries': total,
            'new_enquiries': new_count,
            'quote_requests': quotes.count(),
            'open_requests': total - closed,
            'closed_requests': closed,
        })

class AdminEnquiriesView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [SessionAuthentication]
    def get(self, request):
        combined = []
        for e in ContactEnquiry.objects.prefetch_related('documents'):
            docs = list(e.documents.all())
            combined.append({'id': e.id, 'kind': 'contact', 'name': e.name, 'company': e.company, 'email': e.email, 'phone': e.phone, 'requirement': e.requirement, 'message': e.message, 'status': e.status, 'internal_note': e.internal_note, 'created_at': e.created_at, 'attachment_id': docs[0].id if docs else None, 'location': ''})
        for e in QuoteRequest.objects.prefetch_related('documents'):
            docs = list(e.documents.all())
            combined.append({'id': e.id, 'kind': 'quote', 'name': e.name, 'company': e.company, 'email': e.email, 'phone': e.phone, 'requirement': e.requirement, 'message': e.project_requirement + (('\n\nAdditional message: ' + e.message) if e.message else ''), 'status': e.status, 'internal_note': e.internal_note, 'created_at': e.created_at, 'attachment_id': docs[0].id if docs else None, 'location': e.location})
        combined.sort(key=lambda row: row['created_at'], reverse=True)
        for row in combined:
            row['created_at'] = row['created_at'].isoformat()
        return Response(combined)

class AdminEnquiriesExportView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [SessionAuthentication]
    def get(self, request):
        kind = request.query_params.get('type', 'All')
        status_filter = request.query_params.get('status', 'All')
        query = request.query_params.get('q', '').strip()[:180]
        from_date_raw = request.query_params.get('from_date', '')
        to_date_raw = request.query_params.get('to_date', '')
        from_date = parse_date(from_date_raw) if from_date_raw else None
        to_date = parse_date(to_date_raw) if to_date_raw else None
        if from_date_raw and not from_date: return Response({'detail': 'Invalid start date.'}, status=status.HTTP_400_BAD_REQUEST)
        if to_date_raw and not to_date: return Response({'detail': 'Invalid end date.'}, status=status.HTTP_400_BAD_REQUEST)
        if from_date and to_date and from_date > to_date: return Response({'detail': 'Start date must not be after end date.'}, status=status.HTTP_400_BAD_REQUEST)
        if kind not in {'All', 'contact', 'quote'}: return Response({'detail': 'Invalid enquiry type.'}, status=status.HTTP_400_BAD_REQUEST)
        if status_filter != 'All' and status_filter not in STATUS_VALUES: return Response({'detail': 'Invalid enquiry status.'}, status=status.HTTP_400_BAD_REQUEST)

        combined = []
        if kind in {'All', 'contact'}:
            qs = ContactEnquiry.objects.all()
            if status_filter != 'All': qs = qs.filter(status=status_filter)
            if from_date: qs = qs.filter(created_at__date__gte=from_date)
            if to_date: qs = qs.filter(created_at__date__lte=to_date)
            if query: qs = qs.filter(Q(name__icontains=query) | Q(company__icontains=query) | Q(email__icontains=query) | Q(phone__icontains=query) | Q(requirement__icontains=query) | Q(message__icontains=query))
            for e in qs.iterator():
                combined.append((e.created_at, [e.id, 'Contact', e.name, e.company, e.email, e.phone, e.requirement, e.message, e.status, e.internal_note, e.created_at, '']))
        if kind in {'All', 'quote'}:
            qs = QuoteRequest.objects.all()
            if status_filter != 'All': qs = qs.filter(status=status_filter)
            if from_date: qs = qs.filter(created_at__date__gte=from_date)
            if to_date: qs = qs.filter(created_at__date__lte=to_date)
            if query: qs = qs.filter(Q(name__icontains=query) | Q(company__icontains=query) | Q(email__icontains=query) | Q(phone__icontains=query) | Q(requirement__icontains=query) | Q(project_requirement__icontains=query) | Q(message__icontains=query))
            for e in qs.iterator():
                scope = e.project_requirement + (('\n\nAdditional message: ' + e.message) if e.message else '')
                combined.append((e.created_at, [e.id, 'Quote', e.name, e.company, e.email, e.phone, e.requirement, scope, e.status, e.internal_note, e.created_at, e.location]))
        combined.sort(key=lambda row: row[0], reverse=True)
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="nexage-enquiries-{timezone.localdate().isoformat()}.csv"'
        response['X-Content-Type-Options'] = 'nosniff'
        writer = csv.writer(response, lineterminator='\r\n')
        response.write('\ufeff')
        writer.writerow(['ID', 'Type', 'Name', 'Company', 'Email', 'Phone', 'Requirement', 'Message / Scope', 'Status', 'Internal Note', 'Created At', 'Location'])
        for _created, row in combined:
            safe_row = []
            for value in row:
                if isinstance(value, str) and value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')):
                    value = "'" + value
                safe_row.append(timezone.localtime(value).isoformat() if hasattr(value, 'tzinfo') and getattr(value, 'tzinfo', None) else value)
            writer.writerow(safe_row)
        return response

class AdminEnquiryDetailView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [SessionAuthentication]
    parser_classes = [JSONParser]
    def patch(self, request, kind, pk):
        if kind not in {'contact', 'quote'}:
            return Response({'detail': 'Unknown enquiry type.'}, status=status.HTTP_404_NOT_FOUND)
        model = ContactEnquiry if kind == 'contact' else QuoteRequest
        try: enquiry = model.objects.get(pk=pk)
        except model.DoesNotExist: return Response({'detail': 'Enquiry not found.'}, status=status.HTTP_404_NOT_FOUND)
        new_status = request.data.get('status', enquiry.status)
        note = request.data.get('internal_note', enquiry.internal_note)
        if new_status not in STATUS_VALUES: return Response({'detail': 'Invalid enquiry status.'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(note, str) or len(note) > 5000: return Response({'detail': 'Internal note is too long.'}, status=status.HTTP_400_BAD_REQUEST)
        enquiry.status = new_status
        enquiry.internal_note = note
        enquiry.save(update_fields=['status', 'internal_note', 'updated_at'])
        docs = enquiry.documents.all()
        return Response({'id': enquiry.id, 'kind': kind, 'name': enquiry.name, 'company': enquiry.company, 'email': enquiry.email, 'phone': enquiry.phone, 'requirement': enquiry.requirement, 'message': enquiry.message if kind == 'contact' else enquiry.project_requirement + (('\n\nAdditional message: ' + enquiry.message) if enquiry.message else ''), 'status': enquiry.status, 'internal_note': enquiry.internal_note, 'created_at': enquiry.created_at.isoformat(), 'attachment_id': docs.first().id if docs.exists() else None, 'location': getattr(enquiry, 'location', '')})

class PrivateDocumentDownloadView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [SessionAuthentication]
    def get(self, request, pk):
        try: document = UploadedDocument.objects.get(pk=pk)
        except UploadedDocument.DoesNotExist: raise Http404
        try:
            handle = document.file.open('rb')
        except (FileNotFoundError, OSError, ValueError): raise Http404
        response = FileResponse(handle, as_attachment=True, filename=Path(document.original_name).name)
        response['X-Content-Type-Options'] = 'nosniff'
        response['Content-Security-Policy'] = "sandbox; default-src 'none'"
        return response
