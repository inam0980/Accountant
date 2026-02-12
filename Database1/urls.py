
from django.contrib import admin
from django.urls import path,include
from django.conf import settings  #1
from django.conf.urls.static import static  #1
from dashboard.language_views import set_language

urlpatterns = [
    path('admin/', admin.site.urls),
    path('set-language/', set_language, name='set_language'),  # Language switcher
    path('', include('dashboard.urls')),  # Dashboard at root URL
    path('schools/', include('schools.urls')),  # Multi-school/organization management
    path('accounting/', include('accounting.urls')),  # Advanced Accounting (General Ledger)
    path('billing/', include('billing.urls')),  # Billing and invoices
    path('reports/', include('reports.urls')),  # Financial reports
    path('accounts/', include('accounts.urls')),  # User authentication

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #1
