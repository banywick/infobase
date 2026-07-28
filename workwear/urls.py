from django.urls import path
from .views import *

# ЭТО ОЧЕНЬ ВАЖНО - добавляем app_name
app_name = 'workwear'

urlpatterns = [
    # ========== Шаблонные страницы ==========
    path('', DashboardView.as_view(), name='dashboard'),
    path('employees/', EmployeeListView.as_view(), name='employees'),
    path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee_detail'),
    path('workwear/', WorkwearListView.as_view(), name='workwear_list'),
    path('workwear/add/', WorkwearFormView.as_view(), name='workwear_add'),
    path('workwear/<int:pk>/edit/', WorkwearFormView.as_view(), name='workwear_edit'),
    path('expiring/', ExpiringItemsView.as_view(), name='expiring_items'),
    
    # ========== API endpoints ==========
    path('api/employees/', EmployeeListAPIView.as_view(), name='api_employee_list'),
    path('api/employees/<int:pk>/', EmployeeDetailAPIView.as_view(), name='api_employee_detail'),
    path('api/employees/<int:pk>/workwear/', EmployeeWorkwearAPIView.as_view(), name='api_employee_workwear'),
    path('api/employees/<int:pk>/history/', EmployeeHistoryAPIView.as_view(), name='api_employee_history'),
    
    path('api/workwear-items/', WorkwearItemListAPIView.as_view(), name='api_workwear_list'),
    path('api/workwear-items/<int:pk>/', WorkwearItemDetailAPIView.as_view(), name='api_workwear_detail'),
    path('api/workwear-items/<int:pk>/return/', WorkwearItemReturnAPIView.as_view(), name='api_workwear_return'),
    
    path('api/expiring-items/', ExpiringItemsAPIView.as_view(), name='api_expiring_items'),
    path('api/expired-items/', ExpiredItemsAPIView.as_view(), name='api_expired_items'),
    
    path('api/categories/', CategoryListAPIView.as_view(), name='api_category_list'),
    path('api/categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='api_category_detail'),
    
    path('api/dashboard/stats/', DashboardStatsAPIView.as_view(), name='api_dashboard_stats'),
]