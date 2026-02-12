from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.invoice_list, name='list'),
    path('invoice/create/', views.invoice_create, name='create'),
    path('invoice/create/simplified/', views.simplified_invoice_create, name='simplified_create'),
    path('invoice/create/vat/', views.vat_invoice_create, name='vat_create'),
    path('invoice/<str:invoice_number>/', views.invoice_detail, name='detail'),
    path('invoice/<str:invoice_number>/payment/', views.payment_create, name='payment'),
    path('invoice/<str:invoice_number>/pdf/', views.invoice_pdf, name='pdf'),
    path('invoice/<str:invoice_number>/print/', views.invoice_print, name='print'),
    path('payments/', views.payment_list, name='payments'),
]
