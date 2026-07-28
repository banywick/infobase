from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Employee, WorkwearCategory, WorkwearItem, WorkwearHistory
from .serializers import (
    EmployeeSerializer, EmployeeCreateUpdateSerializer,
    WorkwearCategorySerializer, 
    WorkwearItemSerializer, WorkwearCreateUpdateSerializer,
    WorkwearHistorySerializer
)

# ==================== Шаблонные представления ====================

class DashboardView(View):
    """Дашборд"""
    def get(self, request):
        return render(request, 'workwear/dashboard.html')

class EmployeeListView(View):
    """Список сотрудников (карточки)"""
    def get(self, request):
        return render(request, 'workwear/employees.html')

class EmployeeDetailView(View):
    """Детальная страница сотрудника"""
    def get(self, request, pk):
        return render(request, 'workwear/employee_detail.html', {'employee_id': pk})

class WorkwearListView(View):
    """Список спецодежды"""
    def get(self, request):
        return render(request, 'workwear/workwear_list.html')

class WorkwearFormView(CreateView):
    """Создание и редактирование спецодежды"""
    model = WorkwearItem
    fields = ['employee', 'category', 'name', 'serial_number', 'size', 'color', 
              'issue_date', 'expiration_date', 'is_active', 'notes']
    template_name = 'workwear/workwear_form.html'
    success_url = reverse_lazy('workwear:workwear_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.filter(is_active=True)
        context['categories'] = WorkwearCategory.objects.filter(is_active=True)
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Создаем запись в истории при создании
        if not self.object.pk:
            WorkwearHistory.objects.create(
                workwear_item=self.object,
                action='issued',
                new_employee=self.object.employee,
                description='Выдача спецодежды',
                created_by=self.request.user if self.request.user.is_authenticated else None
            )
        return response
    
    def get_success_url(self):
        return reverse_lazy('workwear:workwear_list')

class ExpiringItemsView(View):
    """Страница с истекающим сроком"""
    def get(self, request):
        return render(request, 'workwear/expiring_items.html')

# ==================== API Views ====================

class EmployeeListAPIView(APIView):
    """Получить список всех сотрудников"""
    
    def get(self, request):
        queryset = Employee.objects.filter(is_active=True)
        
        # Поиск
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(department__icontains=search)
            )
        
        # Фильтр по отделу
        department = request.query_params.get('department', None)
        if department:
            queryset = queryset.filter(department__icontains=department)
        
        # Фильтр по статусу спецодежды
        status_filter = request.query_params.get('status', None)
        if status_filter:
            today = timezone.now().date()
            if status_filter == 'expired':
                employee_ids = WorkwearItem.objects.filter(
                    expiration_date__lt=today,
                    is_active=True
                ).values_list('employee_id', flat=True).distinct()
                queryset = queryset.filter(id__in=employee_ids)
            elif status_filter == 'expiring':
                threshold = today + timedelta(days=30)
                employee_ids = WorkwearItem.objects.filter(
                    expiration_date__gte=today,
                    expiration_date__lte=threshold,
                    is_active=True
                ).values_list('employee_id', flat=True).distinct()
                queryset = queryset.filter(id__in=employee_ids)
            elif status_filter == 'ok':
                all_employee_ids = Employee.objects.filter(is_active=True).values_list('id', flat=True)
                expired_employee_ids = WorkwearItem.objects.filter(
                    expiration_date__lt=today,
                    is_active=True
                ).values_list('employee_id', flat=True).distinct()
                queryset = queryset.filter(id__in=all_employee_ids).exclude(id__in=expired_employee_ids)
        
        # Пагинация
        paginator = PageNumberPagination()
        paginator.page_size = 20
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = EmployeeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class EmployeeDetailAPIView(APIView):
    """Получить, обновить, удалить сотрудника"""
    
    def get(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)
    
    def put(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = EmployeeCreateUpdateSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        employee.is_active = False
        employee.save()
        return Response({'status': 'success', 'message': 'Сотрудник деактивирован'})

class EmployeeWorkwearAPIView(APIView):
    """Получить всю спецодежду сотрудника"""
    
    def get(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        items = employee.workwear_items.filter(is_active=True)
        
        # Фильтр по статусу
        status_filter = request.query_params.get('status', None)
        if status_filter:
            today = timezone.now().date()
            if status_filter == 'expired':
                items = items.filter(expiration_date__lt=today)
            elif status_filter == 'expiring_soon':
                threshold = today + timedelta(days=30)
                items = items.filter(expiration_date__gte=today, expiration_date__lte=threshold)
        
        serializer = WorkwearItemSerializer(items, many=True)
        return Response(serializer.data)

class EmployeeHistoryAPIView(APIView):
    """Получить историю изменений спецодежды сотрудника"""
    
    def get(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        history = WorkwearHistory.objects.filter(
            Q(previous_employee=employee) | Q(new_employee=employee)
        ).order_by('-created_at')
        serializer = WorkwearHistorySerializer(history, many=True)
        return Response(serializer.data)

# ==================== Workwear Items API Views ====================

class WorkwearItemListAPIView(APIView):
    """Получить список всех предметов спецодежды"""
    
    def get(self, request):
        queryset = WorkwearItem.objects.filter(is_active=True)
        
        # Фильтр по сотруднику
        employee_id = request.query_params.get('employee_id', None)
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Фильтр по категории
        category = request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__id=category)
        
        # Фильтр по статусу
        status_filter = request.query_params.get('status', None)
        if status_filter:
            today = timezone.now().date()
            if status_filter == 'expired':
                queryset = queryset.filter(expiration_date__lt=today)
            elif status_filter == 'expiring':
                threshold = today + timedelta(days=30)
                queryset = queryset.filter(expiration_date__gte=today, expiration_date__lte=threshold)
            elif status_filter == 'active':
                queryset = queryset.filter(expiration_date__gt=today)
        
        # Поиск
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(serial_number__icontains=search) |
                Q(employee__user__first_name__icontains=search) |
                Q(employee__user__last_name__icontains=search)
            )
        
        # Фильтр по диапазону дат истечения
        expiration_from = request.query_params.get('expiration_from', None)
        expiration_to = request.query_params.get('expiration_to', None)
        
        if expiration_from:
            try:
                date_from = datetime.strptime(expiration_from, '%Y-%m-%d').date()
                queryset = queryset.filter(expiration_date__gte=date_from)
            except ValueError:
                pass
        
        if expiration_to:
            try:
                date_to = datetime.strptime(expiration_to, '%Y-%m-%d').date()
                queryset = queryset.filter(expiration_date__lte=date_to)
            except ValueError:
                pass
        
        # Пагинация
        paginator = PageNumberPagination()
        paginator.page_size = 50
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = WorkwearItemSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request):
        """Создать новый предмет спецодежды"""
        serializer = WorkwearCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save()
            
            # Создаем запись в истории
            WorkwearHistory.objects.create(
                workwear_item=item,
                action='issued',
                new_employee=item.employee,
                description='Выдача спецодежды',
                created_by=request.user if request.user.is_authenticated else None
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WorkwearItemDetailAPIView(APIView):
    """Получить, обновить, удалить предмет спецодежды"""
    
    def get(self, request, pk):
        item = get_object_or_404(WorkwearItem, pk=pk)
        serializer = WorkwearItemSerializer(item)
        return Response(serializer.data)
    
    def put(self, request, pk):
        item = get_object_or_404(WorkwearItem, pk=pk)
        old_employee = item.employee
        serializer = WorkwearCreateUpdateSerializer(item, data=request.data)
        if serializer.is_valid():
            updated_item = serializer.save()
            
            # Создаем запись в истории если изменился сотрудник
            if old_employee != updated_item.employee:
                WorkwearHistory.objects.create(
                    workwear_item=updated_item,
                    action='replaced',
                    previous_employee=old_employee,
                    new_employee=updated_item.employee,
                    description='Передача спецодежды другому сотруднику',
                    created_by=request.user if request.user.is_authenticated else None
                )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        item = get_object_or_404(WorkwearItem, pk=pk)
        item.is_active = False
        item.save()
        
        # Создаем запись в истории
        WorkwearHistory.objects.create(
            workwear_item=item,
            action='written_off',
            previous_employee=item.employee,
            description='Списание спецодежды',
            created_by=request.user if request.user.is_authenticated else None
        )
        
        return Response({'status': 'success', 'message': 'Спецодежда списана'})

class WorkwearItemReturnAPIView(APIView):
    """Возврат спецодежды"""
    
    def post(self, request, pk):
        item = get_object_or_404(WorkwearItem, pk=pk)
        item.is_active = False
        item.save()
        
        WorkwearHistory.objects.create(
            workwear_item=item,
            action='returned',
            previous_employee=item.employee,
            description=request.data.get('description', 'Возврат спецодежды'),
            created_by=request.user if request.user.is_authenticated else None
        )
        
        return Response({'status': 'success', 'message': 'Спецодежда возвращена'})

# ==================== Expiring/Expired Items API Views ====================

class ExpiringItemsAPIView(APIView):
    """Получить все предметы с истекающим сроком"""
    
    def get(self, request):
        today = timezone.now().date()
        threshold = today + timedelta(days=30)
        items = WorkwearItem.objects.filter(
            expiration_date__gte=today,
            expiration_date__lte=threshold,
            is_active=True
        ).order_by('expiration_date')
        
        # Дополнительные фильтры
        department = request.query_params.get('department', None)
        if department:
            items = items.filter(employee__department__icontains=department)
        
        serializer = WorkwearItemSerializer(items, many=True)
        return Response(serializer.data)

class ExpiredItemsAPIView(APIView):
    """Получить все просроченные предметы"""
    
    def get(self, request):
        today = timezone.now().date()
        items = WorkwearItem.objects.filter(
            expiration_date__lt=today,
            is_active=True
        ).order_by('expiration_date')
        
        # Дополнительные фильтры
        department = request.query_params.get('department', None)
        if department:
            items = items.filter(employee__department__icontains=department)
        
        serializer = WorkwearItemSerializer(items, many=True)
        return Response(serializer.data)

# ==================== Categories API Views ====================

class CategoryListAPIView(APIView):
    """Получить список всех категорий"""
    
    def get(self, request):
        categories = WorkwearCategory.objects.filter(is_active=True)
        serializer = WorkwearCategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = WorkwearCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryDetailAPIView(APIView):
    """Получить, обновить, удалить категорию"""
    
    def get(self, request, pk):
        category = get_object_or_404(WorkwearCategory, pk=pk)
        serializer = WorkwearCategorySerializer(category)
        return Response(serializer.data)
    
    def put(self, request, pk):
        category = get_object_or_404(WorkwearCategory, pk=pk)
        serializer = WorkwearCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        category = get_object_or_404(WorkwearCategory, pk=pk)
        category.is_active = False
        category.save()
        return Response({'status': 'success', 'message': 'Категория деактивирована'})

# ==================== Dashboard/Statistics API Views ====================

class DashboardStatsAPIView(APIView):
    """Получить статистику для дашборда"""
    
    def get(self, request):
        today = timezone.now().date()
        threshold = today + timedelta(days=30)
        
        # Сотрудники с истекающим сроком
        expiring_employees = Employee.objects.filter(
            id__in=WorkwearItem.objects.filter(
                expiration_date__gte=today,
                expiration_date__lte=threshold,
                is_active=True
            ).values_list('employee_id', flat=True).distinct()
        ).count()
        
        stats = {
            'total_employees': Employee.objects.filter(is_active=True).count(),
            'total_workwear': WorkwearItem.objects.filter(is_active=True).count(),
            'expiring_items': WorkwearItem.objects.filter(
                expiration_date__gte=today,
                expiration_date__lte=threshold,
                is_active=True
            ).count(),
            'expired_items': WorkwearItem.objects.filter(
                expiration_date__lt=today,
                is_active=True
            ).count(),
            'active_categories': WorkwearCategory.objects.filter(is_active=True).count(),
            'expiring_employees': expiring_employees,
        }
        
        return Response(stats)