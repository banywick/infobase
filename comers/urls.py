from django.urls import path
from .views import *

urlpatterns = [
    path('', ComersView.as_view(), name='home_commers'),
    path('get_all_positions/', GetAllPositions.as_view(), name='all_positions'),
    path('remove_position/<int:id>/', RemovePosition.as_view(), name ='remove_position'),
    path('add_supplier/', AddSupplier.as_view(), name='add_supplier_name'),
    path('add_invoice_data/', AddInvoiceData.as_view(), name='add_invoice'),
    path('edit_invoices/<int:pk>/', RetrieveUpdateInvoiceData.as_view(), name='invoice_detail_edit'),
    
]   

