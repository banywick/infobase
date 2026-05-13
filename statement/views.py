from datetime import datetime
import json
import os
import shutil
from urllib.parse import unquote
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from config import settings
from finder.models import AccountingData
from finder.serializers import AccountingDataSerializer
from rest_framework.decorators import api_view

from statement.models import SMBPathConfig, SMBFileIndex
from statement.utils.comparison_search_service import SearchService
from statement.utils.excel_processor import ExcelProcessor
from statement.utils.smb import SmbFolderVk
from smbclient import open_file, mkdir



class StatementHome(TemplateView):
    """Главная страница ВК"""
    template_name = 'statement/statement.html'


# statement/views.py (добавить)

@api_view(['POST'])
def start_processing(request):
    """
    Запуск обработки непрочитанных файлов
    """
    config_id = request.data.get('config_id')
    limit = request.data.get('limit', 50)
    
    from .tasks import process_smb_files
    task = process_smb_files.delay(config_id=config_id, limit=limit)
    
    return Response({
        'success': True,
        'task_id': task.id,
        'message': f'Запущена обработка файлов'
    }, status=202)


@api_view(['GET'])
def get_processing_stats(request):
    """
    Получить статистику обработки файлов
    """
    stats = {
        'pending': SMBFileIndex.objects.filter(processing_status='pending', is_available=True).count(),
        'processing': SMBFileIndex.objects.filter(processing_status='processing').count(),
        'processed': SMBFileIndex.objects.filter(processing_status='processed').count(),
        'error': SMBFileIndex.objects.filter(processing_status='error').count(),
        'total_accounting_data': AccountingData.objects.count(),
    }
    
    return Response({
        'success': True,
        'stats': stats
    })

class Statement(APIView):
    """
    Эндпоинт поддерживает:
    1. POST с JSON телом: {"search_string": "текст"}
    2. POST с строкой в URL: /api/draw_statement/текст/
    """
    
    def post(self, request, search_string=None):
        results, error, status_code = SearchService.process_search_request(
            request, 
            search_string
        )
        
        if error:
            return Response({'error': error}, status=status_code)
        
        return Response(results, status=status_code)


@api_view(['GET'])
def get_smb_config(request):
    """
    Получить активную конфигурацию SMB путей
    """
    try:
        config = SMBPathConfig.objects.filter(is_active=True).first()
        
        if not config:
            return Response({
                'success': False,
                'error': 'Активная конфигурация не найдена. Создайте в админке.'
            }, status=404)
        
        return Response({
            'success': True,
            'search_path': config.search_path,
            'result_path': config.result_path,
            'config_name': config.name
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
def job_vk(request):
    """
    Копирование файла из SMB в папку job и его обработка
    Поддерживает file_id из индекса
    """
    print("=" * 50)
    print("🚀 Начало job_vk")
    
    try:
        # Получаем данные из запроса
        data = request.data
        vk_file = data.get('vk_file')
        file_id = data.get('file_id')
        projects = data.get('projects', [])
        start_row = data.get('start_row', 2)
        end_row = data.get('end_row')
        
        print(f"📦 Получены данные:")
        print(f"   Файл: {vk_file}")
        print(f"   File ID: {file_id}")
        print(f"   Проекты: {json.dumps(projects, indent=2, ensure_ascii=False)}")
        print(f"   Начальная строка: {start_row}")
        print(f"   Конечная строка: {end_row if end_row else 'до конца'}")
        
        if not vk_file and not file_id:
            return Response({
                'success': False,
                'error': 'Не указан файл ВК или ID файла'
            }, status=400)
        
        if not start_row or start_row < 1:
            return Response({
                'success': False,
                'error': 'Укажите корректную начальную строку (>= 1)'
            }, status=400)
        
        # ============================================
        # ПОЛУЧАЕМ КОНФИГУРАЦИЮ ИЗ ИНДЕКСА ИЛИ БД
        # ============================================
        
        # Если передан file_id, получаем путь из индекса
        if file_id:
            file_index = SMBFileIndex.objects.filter(id=file_id, is_available=True).first()
            if not file_index:
                return Response({
                    'success': False,
                    'error': f'Файл с ID {file_id} не найден в индексе или недоступен'
                }, status=404)
            
            config = file_index.config
            vk_file = file_index.filename
            vk_file_path = file_index.file_path
            
            print(f"✅ Найден файл в индексе:")
            print(f"   Конфигурация: {config.name}")
            print(f"   Путь: {vk_file_path}")
        else:
            # Старая логика - поиск по имени файла (на случай если индекс не используется)
            config = SMBPathConfig.objects.filter(is_active=True).first()
            if not config:
                return Response({
                    'success': False,
                    'error': 'Активная конфигурация SMB путей не найдена. Создайте конфигурацию в админке.'
                }, status=404)
            
            vk_file_path = None
        
        print(f"✅ Используем конфигурацию: {config.name}")
        print(f"   Поиск в: {config.search_path}")
        print(f"   Результат в: {config.result_path}")
        
        # ============================================
        # ПАРСИМ ПУТИ ИЗ КОНФИГУРАЦИИ
        # ============================================
        search_root = config.search_path
        result_root = config.result_path
        
        # Извлекаем server и share из пути поиска
        path_parts = search_root.strip('\\').split('\\')
        if len(path_parts) >= 2:
            smb_server = path_parts[0]
            smb_share = path_parts[1]
            search_subfolder = '\\'.join(path_parts[2:]) if len(path_parts) > 2 else ''
        else:
            return Response({
                'success': False,
                'error': f'Некорректный путь поиска: {search_root}'
            }, status=400)
        
        # Создаем папку job
        job_root = os.path.join(settings.BASE_DIR, 'job')
        os.makedirs(job_root, exist_ok=True)
        
        # Создаем уникальную подпапку
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = vk_file.replace('.xlsx', '').replace('.xls', '').replace(' ', '_')
        job_subfolder = f"vk_{safe_filename}_{timestamp}"
        job_path = os.path.join(job_root, job_subfolder)
        os.makedirs(job_path, exist_ok=True)
        
        print(f"📁 Создана подпапка: {job_path}")
        
        # ============================================
        # НАХОДИМ ФАЙЛ В SMB
        # ============================================
        smb = SmbFolderVk(server=smb_server, share=smb_share)
        
        # Если у нас нет точного пути, ищем по имени
        if not vk_file_path:
            full_search_path = f"\\\\{smb_server}\\{smb_share}"
            if search_subfolder:
                full_search_path = f"{full_search_path}\\{search_subfolder}"
            
            print(f"🔍 Поиск файла '{vk_file}' в: {full_search_path}")
            
            all_items = smb.get_all_files_and_folders_recursive(full_search_path)
            source_path = None
            
            for item in all_items:
                if not item['is_directory'] and item['name'] == vk_file:
                    source_path = item['path']
                    print(f"✅ Найден файл по имени: {source_path}")
                    break
            
            if not source_path:
                return Response({
                    'success': False,
                    'error': f'Файл "{vk_file}" не найден'
                }, status=404)
            
            vk_file_path = source_path
        
        # Формируем путь назначения
        dest_path = os.path.join(job_path, vk_file)
        
        print(f"📋 Копирование:")
        print(f"   Из: {vk_file_path}")
        print(f"   В: {dest_path}")
        
        # Копируем файл
        try:
            with open_file(vk_file_path, mode='rb') as smb_file:
                with open(dest_path, 'wb') as local_file:
                    local_file.write(smb_file.read())
            
            print(f"✅ Файл скопирован: {dest_path}")
            
        except Exception as e:
            print(f"❌ Ошибка при копировании файла: {e}")
            return Response({
                'success': False,
                'error': f'Не удалось скопировать файл: {str(e)}'
            }, status=500)
        
        # Сохраняем информацию
        info = {
            'config_name': config.name,
            'vk_file': vk_file,
            'vk_file_path': vk_file_path,
            'file_id': file_id if file_id else None,
            'projects': projects,
            'start_row': start_row,
            'end_row': end_row,
            'copied_at': datetime.now().isoformat(),
            'destination': dest_path,
            'search_root': search_root,
            'result_root': result_root,
            'status': 'copied'
        }
        
        info_path = os.path.join(job_path, 'job_info.json')
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        
        # ============================================
        # ОБРАБОТКА EXCEL
        # ============================================
        print("🔄 Начинаем обработку Excel файла...")
        
        result_folder = os.path.join(job_path, 'results')
        os.makedirs(result_folder, exist_ok=True)
        
        processor = ExcelProcessor()
        
        result_file = processor.process_with_projects(
            input_file=dest_path,
            projects=projects,
            start_row=start_row,
            end_row=end_row if end_row else None,
            output_folder=result_folder
        )
        
        print(f"✅ Excel обработан: {result_file}")
        
        # ============================================
        # КОПИРУЕМ РЕЗУЛЬТАТ В SMB ПО ПУТИ ИЗ КОНФИГУРАЦИИ
        # ============================================
        print(f"🔄 Копируем результат в SMB: {result_root}")
        
        result_filename = os.path.basename(result_file)
        
        # Парсим путь для сохранения результата
        result_path_parts = result_root.strip('\\').split('\\')
        if len(result_path_parts) >= 2:
            result_server = result_path_parts[0]
            result_share = result_path_parts[1]
            result_subfolder = '\\'.join(result_path_parts[2:]) if len(result_path_parts) > 2 else ''
        else:
            # Если путь некорректный, используем значения из поиска
            result_server = smb_server
            result_share = smb_share
            result_subfolder = "результат"
        
        print(f"📁 Параметры сохранения:")
        print(f"   Сервер: {result_server}")
        print(f"   Шара: {result_share}")
        print(f"   Подпапка: {result_subfolder if result_subfolder else 'корень'}")
        
        # Создаем отдельный SMB клиент для сохранения (если сервер другой)
        if result_server != smb_server or result_share != smb_share:
            result_smb = SmbFolderVk(server=result_server, share=result_share)
        else:
            result_smb = smb
        
        # Формируем полный путь для сохранения
        if result_subfolder:
            result_smb_folder = f"\\\\{result_server}\\{result_share}\\{result_subfolder}"
        else:
            result_smb_folder = f"\\\\{result_server}\\{result_share}"
        
        # Создаем папку для результатов (рекурсивно)
        try:
            current_path = f"\\\\{result_server}\\{result_share}"
            for folder in result_subfolder.split('\\'):
                if folder:
                    current_path = f"{current_path}\\{folder}"
                    try:
                        mkdir(current_path)
                        print(f"📁 Создана папка: {current_path}")
                    except Exception:
                        # Папка уже существует
                        pass
            print(f"✅ Папка готова: {result_smb_folder}")
        except Exception as e:
            print(f"⚠️ Ошибка при создании папки: {e}")
        
        # Создаем подпапку с именем исходного файла (без расширения)
        file_name_without_ext = os.path.splitext(vk_file)[0]
        target_folder = f"{result_smb_folder}\\{file_name_without_ext}"
        
        # Создаем подпапку для файла
        try:
            mkdir(target_folder)
            print(f"📁 Создана папка для файла: {target_folder}")
        except Exception:
            # Папка уже существует
            pass
        
        # Формируем полный путь к файлу
        target_path = f"{target_folder}\\{result_filename}"
        
        print(f"📤 Загружаем результат в SMB: {target_path}")
        
        upload_success = False
        upload_error = None
        
        try:
            # Загружаем файл
            uploaded_path = result_smb.upload_file(result_file, target_path)
            print(f"✅ Результат загружен: {uploaded_path}")
            upload_success = True
            
        except Exception as e:
            upload_error = str(e)
            print(f"❌ Ошибка при загрузке: {e}")
            
            # Пробуем сохранить в корень папки результатов
            try:
                fallback_path = f"{result_smb_folder}\\{result_filename}"
                print(f"🔄 Пробуем сохранить в корень: {fallback_path}")
                uploaded_path = result_smb.upload_file(result_file, fallback_path)
                target_path = fallback_path
                upload_success = True
                print(f"✅ Результат загружен в корень: {target_path}")
            except Exception as e2:
                upload_error = f"{upload_error}; Альтернатива: {e2}"
                print(f"❌ Альтернатива не сработала: {e2}")
        
        # ============================================
        # УДАЛЯЕМ ВРЕМЕННУЮ ПАПКУ
        # ============================================
        
        deletion_status = "not_deleted"
        
        if upload_success:
            try:
                print("🧹 Удаляем временную папку...")
                shutil.rmtree(job_path)
                print(f"✅ Временная папка удалена: {job_path}")
                deletion_status = "deleted"
            except Exception as e:
                print(f"⚠️ Не удалось удалить временную папку: {e}")
                deletion_status = f"delete_error: {e}"
        else:
            print(f"⚠️ Временная папка не удалена (ошибка загрузки): {job_path}")
        
        # ============================================
        # ФОРМИРУЕМ ОТВЕТ
        # ============================================
        
        user_smb_path = target_path if upload_success else f"Локальный файл: {result_file} (не удалось скопировать в SMB: {upload_error})"
        
        response_data = {
            'success': upload_success,
            'message': f'✅ Файл {vk_file} обработан' if upload_success else f'⚠️ Файл обработан, но не скопирован в SMB',
            'smb_result_path': user_smb_path,
            'job_folder': f"job/{job_subfolder}",
            'projects': [p.get('project') for p in projects],
            'rows_processed': processor.last_row_count if hasattr(processor, 'last_row_count') else 0,
            'row_range': processor.processed_range if hasattr(processor, 'processed_range') else f"{start_row}-{end_row if end_row else 'конец'}",
            'result_filename': result_filename,
            'temp_folder_deleted': deletion_status == 'deleted',
            'upload_success': upload_success,
            'upload_error': upload_error if not upload_success else None,
            'config_used': {
                'name': config.name,
                'search_path': search_root,
                'result_path': result_root
            }
        }
        
        # Обновляем информацию об успешной обработке в индексе
        if file_id:
            SMBFileIndex.objects.filter(id=file_id).update(
                last_checked=datetime.now()
            )
        
        return Response(response_data)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================
# НОВЫЕ ЭНДПОЙНТЫ ДЛЯ РАБОТЫ С ИНДЕКСОМ
# ============================================

@api_view(['GET'])
def get_index_status(request):
    """
    Получить статус индексации
    """
    configs = SMBPathConfig.objects.filter(is_active=True)
    stats = {}
    
    for config in configs:
        file_count = SMBFileIndex.objects.filter(
            config=config,
            is_available=True
        ).count()
        
        last_indexed = SMBFileIndex.objects.filter(
            config=config
        ).order_by('-last_checked').first()
        
        stats[config.name] = {
            'total_files': file_count,
            'last_indexed': last_indexed.last_checked if last_indexed else None,
            'is_indexed': file_count > 0
        }
    
    return Response({
        'success': True,
        'stats': stats
    })


@api_view(['GET'])
def get_index_stats(request):
    """
    Получить статистику индексации по всем конфигурациям
    """
    configs = SMBPathConfig.objects.filter(is_active=True)
    
    stats = []
    for config in configs:
        file_count = SMBFileIndex.objects.filter(
            config=config,
            is_available=True
        ).count()
        
        # Получаем список типов файлов
        file_types = SMBFileIndex.objects.filter(
            config=config,
            is_available=True
        ).values_list('file_extension', flat=True).distinct()
        
        stats.append({
            'id': config.id,
            'name': config.name,
            'search_path': config.search_path,
            'file_count': file_count,
            'file_types': list(file_types),
            'last_indexed': SMBFileIndex.objects.filter(
                config=config
            ).order_by('-last_checked').first().last_checked if file_count > 0 else None
        })
    
    return Response({
        'success': True,
        'configs': stats,
        'total_files': sum(s['file_count'] for s in stats),
        'active_configs_count': configs.count()
    })


@api_view(['POST'])
def start_indexing(request):
    """
    Запустить индексацию через Celery
    """
    config_id = request.data.get('config_id')
    force = request.data.get('force', False)
    
    # Запускаем задачу
    task = index_smb_files.delay(config_id=config_id, force=force)
    
    return Response({
        'success': True,
        'task_id': task.id,
        'message': 'Индексация запущена в фоновом режиме'
    }, status=202)


@api_view(['GET'])
def get_indexed_files(request):
    """
    Получить список индексированных файлов из ВСЕХ активных конфигураций
    Параметры:
    - search: поиск по имени файла
    - page: номер страницы
    - page_size: размер страницы
    - config_name: опционально - фильтр по конфигурации
    """
    # Получаем все активные конфигурации
    configs = SMBPathConfig.objects.filter(is_active=True)
    
    if not configs.exists():
        return Response({
            'success': False,
            'error': 'Нет активных конфигураций'
        }, status=404)
    
    # Фильтр по конкретной конфигурации (опционально)
    config_name = request.GET.get('config_name')
    if config_name:
        configs = configs.filter(name=config_name)
    
    # Базовый запрос - собираем файлы из всех конфигураций
    queryset = SMBFileIndex.objects.filter(
        config__in=configs,
        is_available=True
    ).select_related('config').order_by('filename')
    
    # Поиск по имени файла
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(filename__icontains=search_query)
    
    # Пагинация
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 50))
    
    total = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    
    files = queryset[start:end]
    
    # Формируем ответ с информацией о конфигурации для каждого файла
    files_data = []
    for f in files:
        files_data.append({
            'id': f.id,
            'filename': f.filename,
            'path': f.file_path,
            'relative_path': f.relative_path,
            'size': f.file_size,
            'modified': f.modified_time,
            'type': f.file_extension,
            'config': {
                'id': f.config.id,
                'name': f.config.name,
                'search_path': f.config.search_path
            }
        })
    
    # Собираем информацию о всех конфигурациях для фильтрации на фронте
    configs_info = [{
        'id': c.id,
        'name': c.name,
        'file_count': SMBFileIndex.objects.filter(config=c, is_available=True).count()
    } for c in configs]
    
    return Response({
        'success': True,
        'files': files_data,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size,
        'configs': configs_info,
        'active_configs_count': configs.count()
    })


@api_view(['POST'])
def get_file_info(request):
    """
    Получить информацию о файле по ID
    """
    file_id = request.data.get('file_id')
    
    if not file_id:
        return Response({
            'success': False,
            'error': 'Укажите file_id'
        }, status=400)
    
    try:
        file_index = SMBFileIndex.objects.select_related('config').get(id=file_id, is_available=True)
        
        return Response({
            'success': True,
            'file': {
                'id': file_index.id,
                'filename': file_index.filename,
                'path': file_index.file_path,
                'relative_path': file_index.relative_path,
                'size': file_index.file_size,
                'modified': file_index.modified_time,
                'type': file_index.file_extension,
                'config_name': file_index.config.name,
                'config': {
                    'id': file_index.config.id,
                    'name': file_index.config.name,
                    'search_path': file_index.config.search_path,
                    'result_path': file_index.config.result_path
                }
            }
        })
    except SMBFileIndex.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Файл не найден в индексе'
        }, status=404)