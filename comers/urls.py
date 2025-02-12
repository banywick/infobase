from django.urls import path
from .views import *

urlpatterns = [
    path('', ComersView.as_view(), name='home_commers'),
    path('get_all_positions/', GetAllPositions.as_view(), name='all_positions'),
    path('remove_position/<int:id>/', RemovePosition.as_view(), name ='remove_position'),
    path('add_supplier/', AddSupplier.as_view(), name='add_supplier_name'),
    path('add_invoice_data/', AddInvoiceData.as_view(), name='add_invoice'),
    path('add_filter_invoice_data/', AddFilterInvoiceData.as_view(), name='add_filter_invoice'),
    path('get_filter_invoice_data/', GetFilterInvoiceData.as_view(), name='get_filter_invoice'),
    path('clear_filter_invoice_data/', ClearFilterInvoiceData.as_view(), name='clear_filter_invoice'),
    
]   

