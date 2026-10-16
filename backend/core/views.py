import csv
import logging
import mimetypes
import re
import zipfile
from pathlib import Path
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
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

def send_enquiry_notifications(subject, body, customer_email=None, customer_name=None):
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.SALES_ENQUIRY_EMAIL], fail_silently=False)
    except Exception:
        # The enquiry is already committed; mail transport failure must not lose the submission.
        logger.exception('Unable to send new NexAge website enquiry notification.')
    if settings.SEND_CUSTOMER_CONFIRMATION and customer_email:
        try:
            send_mail('We received your enquiry — NexAge India', f'Hello {customer_name or "there"},\n\nThank you for contacting NexAge India. Your enquiry has been received. Our team will contact you shortly.\n\nRegards,\nNexAge India Pvt. Ltd.\nsales@nexageindia.com', settings.DEFAULT_FROM_EMAIL, [customer_email], fail_silently=False)
        except Exception:
            logger.exception('Unable to send enquiry confirmation email.')

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
        send_enquiry_notifications('New NexAge Website Enquiry', notification_body('Contact enquiry', serializer.validated_data, request), enquiry.email, enquiry.name)
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
        quote = serializer.save(ip_hash=get_user_ip_hash(request))
        if upload:
            # Private storage only; no public media URL is configured.
            UploadedDocument.objects.create(quote_request=quote, file=upload, original_name=Path(str(upload.name).replace('\\', '/')).name[:255], mime_type=mimetypes.guess_type(upload.name)[0] or upload.content_type or '', size_bytes=upload.size)
        send_enquiry_notifications('New NexAge Website Enquiry', notification_body('Request for quote', serializer.validated_data, request), quote.email, quote.name)
        return Response({'received': True, 'id': quote.id, 'message': 'Thank you. Your enquiry has been received. Our team will contact you shortly.'}, status=status.HTTP_201_CREATED)

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
