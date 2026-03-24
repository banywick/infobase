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

from statement.models import SMBPathConfig
from statement.utils.comparison_search_service import SearchService
from statement.utils.excel_processor import ExcelProcessor
from statement.utils.smb import SmbFolderVk
from statement.utils.smb_config import get_active_smb_config




class StatementHome(TemplateView):
    """Главная страница ВК"""

    template_name = 'statement/statement.html'




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
    


@api_view(['GET', 'POST'])  # Добавляем поддержку GET
def get_vk_files(request):
    """
    Получение всех Excel файлов из SMB рекурсивно
    Поддерживает GET и POST запросы
    """
    try:
        # Получаем search_path из GET или POST
        if request.method == 'GET':
            search_path = request.GET.get('search_path')
        else:  # POST
            data = request.data
            search_path = data.get('search_path')
        
        # Если search_path не передан, берем из активной конфигурации
        if not search_path:
            from .models import SMBPathConfig
            config = SMBPathConfig.objects.filter(is_active=True).first()
            if not config:
                return Response({
                    'success': False,
                    'error': 'Активная конфигурация не найдена. Укажите search_path или создайте конфигурацию в админке.'
                }, status=400)
            search_path = config.search_path
            print(f"🔍 Используем путь из конфигурации: {search_path}")
        
        print(f"🔍 Поиск файлов в: {search_path}")
        
        # Парсим путь
        path_parts = search_path.strip('\\').split('\\')
        if len(path_parts) >= 2:
            server = path_parts[0]
            share = path_parts[1]
            subfolder = '\\'.join(path_parts[2:]) if len(path_parts) > 2 else ''
        else:
            return Response({
                'success': False,
                'error': f'Некорректный путь: {search_path}'
            }, status=400)
        
        # Создаем SMB клиент
        smb = SmbFolderVk(server=server, share=share)
        
        # Формируем полный путь для поиска
        if subfolder:
            full_search_path = f"\\\\{server}\\{share}\\{subfolder}"
        else:
            full_search_path = f"\\\\{server}\\{share}"
        
        # Получаем все файлы рекурсивно
        all_items = smb.get_all_files_and_folders_recursive(full_search_path)
        
        # Фильтруем Excel файлы
        files = []
        for item in all_items:
            if not item['is_directory']:
                filename = item['name']
                if filename.endswith(('.xlsx', '.xls', '.xlsm')):
                    files.append({
                        'name': filename,
                        'path': item['path'],
                        'relative_path': item['relative_path']
                    })
        
        print(f"✅ Найдено Excel файлов: {len(files)}")
        
        return Response({
            'success': True,
            'files': files,
            'count': len(files),
            'search_path': search_path
        })
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
    



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

# views.py - обновленная часть с диапазоном строк

@api_view(['POST'])
def job_vk(request):
    """
    Копирование файла из SMB в папку job и его обработка
    URL: /job_vk_statement/
    """
    print("=" * 50)
    print("🚀 Начало job_vk")
    
    try:
        # Получаем данные из запроса
        data = request.data
        vk_file = data.get('vk_file')
        vk_file_path = data.get('vk_file_path')
        projects = data.get('projects', [])
        start_row = data.get('start_row', 2)
        end_row = data.get('end_row')
        
        print(f"📦 Получены данные:")
        print(f"   Файл: {vk_file}")
        print(f"   Путь к файлу: {vk_file_path}")
        print(f"   Проекты: {json.dumps(projects, indent=2, ensure_ascii=False)}")
        print(f"   Начальная строка: {start_row}")
        print(f"   Конечная строка: {end_row if end_row else 'до конца'}")
        
        if not vk_file:
            return Response({
                'success': False,
                'error': 'Не указан файл ВК'
            }, status=400)
        
        if not start_row or start_row < 1:
            return Response({
                'success': False,
                'error': 'Укажите корректную начальную строку (>= 1)'
            }, status=400)
        
        # ============================================
        # ПОЛУЧАЕМ КОНФИГУРАЦИЮ ИЗ БД
        # ============================================
        from .models import SMBPathConfig
        
        # Получаем активную конфигурацию
        config = SMBPathConfig.objects.filter(is_active=True).first()
        
        if not config:
            return Response({
                'success': False,
                'error': 'Активная конфигурация SMB путей не найдена. Создайте конфигурацию в админке.'
            }, status=404)
        
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
        
        print(f"📁 Параметры SMB:")
        print(f"   Сервер: {smb_server}")
        print(f"   Шара: {smb_share}")
        print(f"   Подпапка поиска: {search_subfolder if search_subfolder else 'корень'}")
        
        # Создаем папку job если её нет
        job_root = os.path.join(settings.BASE_DIR, 'job')
        os.makedirs(job_root, exist_ok=True)
        print(f"📁 Папка job: {job_root}")
        
        # Создаем уникальную подпапку для этой задачи
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = vk_file.replace('.xlsx', '').replace('.xls', '').replace(' ', '_')
        job_subfolder = f"vk_{safe_filename}_{timestamp}"
        job_path = os.path.join(job_root, job_subfolder)
        os.makedirs(job_path, exist_ok=True)
        
        print(f"📁 Создана подпапка: {job_path}")
        
        # ============================================
        # НАХОДИМ ФАЙЛ В SMB (рекурсивно по указанному пути)
        # ============================================
        from smbclient import open_file, mkdir
        
        # Создаем SMB клиент с параметрами из конфигурации
        smb = SmbFolderVk(server=smb_server, share=smb_share)
        
        # Формируем полный путь для поиска
        if search_subfolder:
            full_search_path = f"\\\\{smb_server}\\{smb_share}\\{search_subfolder}"
        else:
            full_search_path = f"\\\\{smb_server}\\{smb_share}"
        
        print(f"🔍 Поиск файлов в: {full_search_path}")
        
        # Получаем все файлы рекурсивно из указанной папки
        all_items = smb.get_all_files_and_folders_recursive(full_search_path)
        
        # Ищем файл по имени или по пути
        source_path = None
        found_file_info = None
        
        for item in all_items:
            if not item['is_directory']:
                if item['name'] == vk_file:
                    source_path = item['path']
                    found_file_info = item
                    print(f"✅ Найден файл по имени: {source_path}")
                    break
                elif vk_file_path and item['path'] == vk_file_path:
                    source_path = item['path']
                    found_file_info = item
                    print(f"✅ Найден файл по пути: {source_path}")
                    break
        
        if not source_path:
            available_files = [item['name'] for item in all_items if not item['is_directory']]
            print(f"❌ Файл '{vk_file}' не найден!")
            print(f"📋 Доступные файлы (первые 20): {available_files[:20]}")
            
            return Response({
                'success': False,
                'error': f'Файл "{vk_file}" не найден в папке {full_search_path}',
                'available_files': available_files[:50],
                'search_path': full_search_path
            }, status=404)
        
        # Формируем путь назначения
        dest_path = os.path.join(job_path, found_file_info['name'])
        
        print(f"📋 Копирование:")
        print(f"   Из: {source_path}")
        print(f"   В: {dest_path}")
        
        # Копируем файл
        try:
            with open_file(source_path, mode='rb') as smb_file:
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
            'vk_file_path': source_path,
            'vk_file_relative_path': found_file_info.get('relative_path', ''),
            'projects': projects,
            'start_row': start_row,
            'end_row': end_row,
            'copied_at': datetime.now().isoformat(),
            'source': source_path,
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
        
        if not upload_success:
            response_data['local_file_path'] = result_file
        
        print(f"\n📤 Ответ пользователю:")
        print(f"   Конфигурация: {config.name}")
        print(f"   SMB путь: {user_smb_path}")
        print(f"   Загрузка успешна: {upload_success}")
        
        return Response(response_data)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)