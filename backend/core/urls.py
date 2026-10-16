from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import AwardViewSet, AdminDashboardView, AdminEnquiriesView, AdminEnquiriesExportView, AdminEnquiryDetailView, ContactEnquiryCreateView, IndustryViewSet, LoginView, LogoutView, MediaAssetFileView, MediaAssetViewSet, NewsUpdateImageView, NewsUpdateViewSet, PartnerViewSet, PrivateDocumentDownloadView, ProductViewSet, ProjectViewSet, QuoteRequestCreateView, ServiceViewSet, csrf_token

router = DefaultRouter()
router.register('products', ProductViewSet, basename='products')
router.register('projects', ProjectViewSet, basename='projects')
router.register('services', ServiceViewSet, basename='services')
router.register('partners', PartnerViewSet, basename='partners')
router.register('awards', AwardViewSet, basename='awards')
router.register('industries', IndustryViewSet, basename='industries')
router.register('media', MediaAssetViewSet, basename='media')
router.register('news', NewsUpdateViewSet, basename='news-updates')

urlpatterns = [
    path('auth/csrf/', csrf_token, name='csrf-token'),
    path('media/<int:pk>/file/', MediaAssetFileView.as_view(), name='media-asset-file'),
    path('news/<int:pk>/image/', NewsUpdateImageView.as_view(), name='news-update-image'),
    path('auth/login/', LoginView.as_view(), name='api-login'),
    path('auth/logout/', LogoutView.as_view(), name='api-logout'),
    path('enquiries/contact/', ContactEnquiryCreateView.as_view(), name='contact-enquiry'),
    path('enquiries/quote/', QuoteRequestCreateView.as_view(), name='quote-enquiry'),
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('admin/enquiries/export.csv', AdminEnquiriesExportView.as_view(), name='admin-enquiries-export'),
    path('admin/enquiries/', AdminEnquiriesView.as_view(), name='admin-enquiries'),
    path('admin/enquiries/<str:kind>/<int:pk>/', AdminEnquiryDetailView.as_view(), name='admin-enquiry-detail'),
    path('admin/documents/<int:pk>/download/', PrivateDocumentDownloadView.as_view(), name='private-document-download'),
    path('', include(router.urls)),
]
