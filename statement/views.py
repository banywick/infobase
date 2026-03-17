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

from statement.utils.excel_processor import ExcelProcessor
from statement.utils.smb import SmbFolderVk




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
        # Приоритет: тело запроса > URL параметр
        if request.data and 'search_string' in request.data:
            search_term = request.data['search_string']
        elif search_string:
            # Декодируем URL-закодированную строку
            search_term = unquote(search_string)
        else:
            return Response(
                {'error': 'Не передана строка для поиска'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Поиск в базе
        results = AccountingData.objects.filter(
            nomenclature_kd__icontains=search_term
        )
        
        serializer = AccountingDataSerializer(results, many=True)
        
        return Response({
            'search_string': search_term,
            'matches_found': results.count(),
            'data': serializer.data
        })
    

@api_view(['GET'])
def get_vk_files(request):
    """
    Простой API эндпоинт для получения списка файлов из SMB
    """
    try:
        smb = SmbFolderVk()
        files = smb.get_files()
        print(files)
        
        
        return Response({
            'success': True,
            'files': files,
            'count': len(files)
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
    



# views.py - обновленный ответ
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
        projects = data.get('projects', [])
        
        print(f"📦 Получены данные:")
        print(f"   Файл: {vk_file}")
        print(f"   Проекты: {json.dumps(projects, indent=2, ensure_ascii=False)}")
        
        if not vk_file:
            return Response({
                'success': False,
                'error': 'Не указан файл ВК'
            }, status=400)
        
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
        
        # Копируем файл из SMB
        smb = SmbFolderVk()
        
        # Формируем путь к файлу в SMB
        source_path = f"\\\\{smb.server}\\{smb.share}\\{smb.folder}\\{vk_file}"
        dest_path = os.path.join(job_path, vk_file)
        
        print(f"📋 Копирование:")
        print(f"   Из: {source_path}")
        print(f"   В: {dest_path}")
        
        # Копируем файл
        from smbclient import open_file
        with open_file(source_path, mode='rb') as smb_file:
            with open(dest_path, 'wb') as local_file:
                local_file.write(smb_file.read())
        
        print(f"✅ Файл скопирован: {dest_path}")
        
        # Сохраняем информацию о проектах
        info = {
            'vk_file': vk_file,
            'projects': projects,
            'copied_at': datetime.now().isoformat(),
            'source': source_path,
            'destination': dest_path,
            'status': 'copied'
        }
        
        info_path = os.path.join(job_path, 'job_info.json')
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        
        print(f"📝 Информация сохранена: {info_path}")
        
        # ============================================
        # ТУТ ЖЕ ЗАПУСКАЕМ ОБРАБОТКУ EXCEL
        # ============================================
        print("🔄 Начинаем обработку Excel файла...")
        
        # Создаем папку для результатов внутри job
        result_folder = os.path.join(job_path, 'results')
        os.makedirs(result_folder, exist_ok=True)
        
        # Создаем экземпляр процессора
        processor = ExcelProcessor()
        
        # Обрабатываем файл - читаем столбец B (индекс 2)
        result_file = processor.process_column_b(
            input_file=dest_path,
            column_index=2,  # Столбец B
            output_folder=result_folder
        )
        
        print(f"✅ Excel обработан: {result_file}")
        
        # ============================================
        # КОПИРУЕМ РЕЗУЛЬТАТ В SMB ПАПКУ "результат"
        # ============================================
        print("🔄 Копируем результат в SMB папку 'результат'...")
        
        # Загружаем результат в SMB
        result_filename = os.path.basename(result_file)
        
        # Убеждаемся что папка "результат" существует
        try:
            target_path = f"\\\\{smb.server}\\{smb.share}\\результат\\{result_filename}"
            
            with open(result_file, 'rb') as local_file:
                with open_file(target_path, mode='wb') as smb_file:
                    smb_file.write(local_file.read())
            
            print(f"✅ Результат скопирован в SMB: {target_path}")
            
            # Формируем понятный пользователю путь
            user_smb_path = f"\\\\{smb.server}\\{smb.share}\\результат\\{result_filename}"
            
            # ============================================
            # УДАЛЯЕМ ВРЕМЕННУЮ ПАПКУ ПОСЛЕ УСПЕШНОЙ ЗАГРУЗКИ
            # ============================================
            print("🧹 Удаляем временную папку...")
            
            # Проверяем что файл действительно существует в SMB перед удалением
            try:
                # Пробуем открыть файл в SMB чтобы убедиться что он там есть
                with open_file(target_path, mode='rb') as verify_file:
                    # Просто проверяем что файл существует
                    pass
                
                # Удаляем временную папку
                shutil.rmtree(job_path)
                print(f"✅ Временная папка удалена: {job_path}")
                
                deletion_status = "deleted"
                
            except Exception as e:
                print(f"⚠️ Не удалось проверить файл в SMB перед удалением: {e}")
                print(f"⚠️ Временная папка НЕ УДАЛЕНА: {job_path}")
                deletion_status = "not_deleted_verification_failed"
            
        except Exception as e:
            print(f"⚠️ Ошибка при копировании в SMB: {e}")
            user_smb_path = f"Локальный файл: {result_file} (не удалось скопировать в SMB)"
            deletion_status = "not_deleted_upload_failed"
        
        # ============================================
        # ФОРМИРУЕМ ОТВЕТ ДЛЯ ПОЛЬЗОВАТЕЛЯ
        # ============================================
        
        response_data = {
            'success': True,
            'message': f'✅ Файл {vk_file} обработан',
            'smb_result_path': user_smb_path,
            'job_folder': f"job/{job_subfolder}",
            'projects': [p.get('project') for p in projects],
            'rows_processed': processor.last_row_count if hasattr(processor, 'last_row_count') else 0,
            'result_filename': result_filename,
            'temp_folder_deleted': deletion_status == 'deleted'
        }
        
        print(f"📤 Ответ пользователю:")
        print(f"   SMB путь: {user_smb_path}")
        print(f"   Строк обработано: {response_data['rows_processed']}")
        print(f"   Временная папка удалена: {response_data['temp_folder_deleted']}")
        
        return Response(response_data)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        
        # В случае ошибки НЕ удаляем папку, чтобы можно было посмотреть логи
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)