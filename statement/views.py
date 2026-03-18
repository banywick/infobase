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

from statement.utils.comparison_search_service import SearchService
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
        results, error, status_code = SearchService.process_search_request(
            request, 
            search_string
        )
        
        if error:
            return Response({'error': error}, status=status_code)
        
        return Response(results, status=status_code)
    

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
        projects = data.get('projects', [])
        start_row = data.get('start_row', 2)  # По умолчанию со 2 строки
        end_row = data.get('end_row')  # Может быть None (до конца)
        
        print(f"📦 Получены данные:")
        print(f"   Файл: {vk_file}")
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
        
        # Сохраняем информацию о проектах и диапазоне
        info = {
            'vk_file': vk_file,
            'projects': projects,
            'start_row': start_row,
            'end_row': end_row,
            'copied_at': datetime.now().isoformat(),
            'source': source_path,
            'destination': dest_path,
            'status': 'copied'
        }
        
        info_path = os.path.join(job_path, 'job_info.json')
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        
        print(f"📝 Информация сохранена: {info_path}")
        print(f"   Диапазон строк: {start_row} - {end_row if end_row else 'до конца'}")
        
        # ============================================
        # ЗАПУСКАЕМ ОБРАБОТКУ EXCEL С ДИАПАЗОНОМ
        # ============================================
        print("🔄 Начинаем обработку Excel файла...")
        
        # Создаем папку для результатов внутри job
        result_folder = os.path.join(job_path, 'results')
        os.makedirs(result_folder, exist_ok=True)
        
        # Создаем экземпляр процессора
        processor = ExcelProcessor()
        
        # Обрабатываем файл с указанным диапазоном строк и проектами
        result_file = processor.process_with_projects(
            input_file=dest_path,
            projects=projects,  # Передаем проекты
            start_row=start_row,
            end_row=end_row if end_row else None,
            output_folder=result_folder
        )
        
        print(f"✅ Excel обработан: {result_file}")
        print(f"📊 Обработано строк с данными: {processor.last_row_count}")
        print(f"📊 Диапазон обработки: {processor.processed_range}")
        
        # ============================================
        # КОПИРУЕМ РЕЗУЛЬТАТ В SMB ПАПКУ "результат"
        # ============================================
        print("🔄 Копируем результат в SMB папку 'результат'...")
        
        # Загружаем результат в SMB
        result_filename = os.path.basename(result_file)
        
        try:
            target_path = f"\\\\{smb.server}\\{smb.share}\\результат\\{result_filename}"
            
            with open(result_file, 'rb') as local_file:
                with open_file(target_path, mode='wb') as smb_file:
                    smb_file.write(local_file.read())
            
            print(f"✅ Результат скопирован в SMB: {target_path}")
            
            # Формируем понятный пользователю путь
            user_smb_path = f"\\\\{smb.server}\\{smb.share}\\результат\\{result_filename}"
            
            # Проверяем что файл существует в SMB
            try:
                with open_file(target_path, mode='rb') as verify_file:
                    pass
                
                # Удаляем временную папку
                # print("🧹 Удаляем временную папку...")
                # shutil.rmtree(job_path)
                # print(f"✅ Временная папка удалена: {job_path}")
                deletion_status = "deleted"
                
            except Exception as e:
                print(f"⚠️ Не удалось проверить файл в SMB: {e}")
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
            'rows_processed': processor.last_row_count,
            'row_range': processor.processed_range,
            'result_filename': result_filename,
            'temp_folder_deleted': deletion_status == 'deleted'
        }
        
        print(f"📤 Ответ пользователю:")
        print(f"   SMB путь: {user_smb_path}")
        print(f"   Диапазон: {processor.processed_range}")
        print(f"   Строк обработано: {processor.last_row_count}")
        
        return Response(response_data)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)