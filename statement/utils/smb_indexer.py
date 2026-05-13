# utils/smb_indexer.py
import os
from datetime import datetime
from typing import List, Dict, Any
from smbclient import stat
from statement.models import SMBPathConfig, SMBFileIndex
from statement.utils.smb import SmbFolderVk


class SMBFileIndexer:
    """
    Сервис для индексации файлов в SMB
    """
    
    EXCEL_EXTENSIONS = {'.xlsx', '.xls', '.xlsm'}
    
    def __init__(self, config: SMBPathConfig):
        self.config = config
        self.smb = None
        self._init_smb_client()
    
    def _init_smb_client(self):
        """Инициализация SMB клиента"""
        path_parts = self.config.search_path.strip('\\').split('\\')
        if len(path_parts) >= 2:
            server = path_parts[0]
            share = path_parts[1]
            self.smb = SmbFolderVk(server=server, share=share)
        else:
            raise ValueError(f"Некорректный путь: {self.config.search_path}")
    
    def get_full_search_path(self) -> str:
        """Получить полный путь для поиска"""
        path_parts = self.config.search_path.strip('\\').split('\\')
        if len(path_parts) >= 2:
            server = path_parts[0]
            share = path_parts[1]
            subfolder = '\\'.join(path_parts[2:]) if len(path_parts) > 2 else ''
            
            if subfolder:
                return f"\\\\{server}\\{share}\\{subfolder}"
            else:
                return f"\\\\{server}\\{share}"
        return self.config.search_path
    
    def scan_and_index(self, force_rescan: bool = False) -> Dict[str, Any]:
        """
        Сканирует SMB и обновляет индекс файлов
        
        Args:
            force_rescan: Принудительное полное сканирование (иначе обновляет только новые/измененные)
        
        Returns:
            Dict с результатами сканирования
        """
        print(f"🔄 Начинаем индексацию для конфигурации: {self.config.name}")
        
        # Если не принудительное сканирование, сначала проверяем существующие файлы
        if not force_rescan:
            self._mark_missing_files()
        
        search_path = self.get_full_search_path()
        all_items = self.smb.get_all_files_and_folders_recursive(search_path)
        
        stats = {
            'total_found': 0,
            'new_files': 0,
            'updated_files': 0,
            'errors': 0,
            'files_by_type': {'xlsx': 0, 'xls': 0, 'xlsm': 0}
        }
        
        for item in all_items:
            if not item['is_directory']:
                filename = item['name']
                ext = os.path.splitext(filename)[1].lower()
                
                if ext in self.EXCEL_EXTENSIONS:
                    stats['total_found'] += 1
                    ext_clean = ext[1:]  # убираем точку
                    stats['files_by_type'][ext_clean] = stats['files_by_type'].get(ext_clean, 0) + 1
                    
                    try:
                        self._update_or_create_file_index(item, ext_clean, search_path)
                        stats['new_files' if not item.get('existed') else 'updated_files'] += 1
                    except Exception as e:
                        stats['errors'] += 1
                        print(f"❌ Ошибка при индексации {filename}: {e}")
        
        # Удаляем из индекса файлы, которые больше не доступны
        deleted_count = self._cleanup_missing_files()
        stats['deleted_files'] = deleted_count
        
        print(f"✅ Индексация завершена:")
        print(f"   Найдено файлов: {stats['total_found']}")
        print(f"   Новых: {stats['new_files']}")
        print(f"   Обновлено: {stats['updated_files']}")
        print(f"   Удалено из индекса: {deleted_count}")
        print(f"   По типам: {stats['files_by_type']}")
        
        return stats
    
    def _mark_missing_files(self):
        """Помечает существующие файлы как потенциально отсутствующие"""
        SMBFileIndex.objects.filter(
            config=self.config,
            is_available=True
        ).update(is_available=False)
    
    def _update_or_create_file_index(self, item: Dict, ext: str, search_path: str):
        """Обновляет или создает запись о файле в БД"""
        
        # Получаем размер и время изменения через stat метод нашего класса
        file_size = None
        modified_time = None
        
        try:
            # Используем stat_file метод SmbFolderVk
            stat_result = self.smb.stat_file(item['path'])
            if stat_result:
                file_size = stat_result.st_size
                if hasattr(stat_result, 'st_mtime'):
                    from datetime import datetime
                    modified_time = datetime.fromtimestamp(stat_result.st_mtime)
        except Exception as e:
            print(f"⚠️ Не удалось получить stat для {item['name']}: {e}")
        
        # Создаем или обновляем запись
        file_index, created = SMBFileIndex.objects.update_or_create(
            config=self.config,
            file_path=item['path'],
            defaults={
                'filename': item['name'],
                'file_extension': ext,
                'relative_path': item.get('relative_path', ''),
                'file_size': file_size,
                'modified_time': modified_time,
                'is_available': True,
                'last_checked': datetime.now()
            }
        )
        
        # Для отладки
        if created:
            print(f"   📄 Новый файл: {item['name']}")
        else:
            print(f"   🔄 Обновлен: {item['name']}")
        
        item['existed'] = not created
    
    def _cleanup_missing_files(self) -> int:
        """Удаляет из базы записи о файлах, которые не были найдены"""
        deleted_count, _ = SMBFileIndex.objects.filter(
            config=self.config,
            is_available=False
        ).delete()
        return deleted_count
    
    def get_available_files(self, file_type: str = None) -> List[Dict]:
        """
        Получить список доступных файлов из индекса
        
        Args:
            file_type: 'xlsx', 'xls', 'xlsm' или None для всех
        """
        queryset = SMBFileIndex.objects.filter(
            config=self.config,
            is_available=True
        ).order_by('filename')
        
        if file_type:
            queryset = queryset.filter(file_extension=file_type)
        
        return [
            {
                'id': f.id,
                'filename': f.filename,
                'path': f.file_path,
                'relative_path': f.relative_path,
                'size': f.file_size,
                'modified': f.modified_time,
                'type': f.file_extension,
                'config_name': self.config.name
            }
            for f in queryset
        ]


def index_all_active_configs(force_rescan: bool = False) -> Dict[str, Any]:
    """
    Запускает индексацию для всех активных конфигураций
    
    Returns:
        Сводка по индексации
    """
    active_configs = SMBPathConfig.objects.filter(is_active=True)
    
    if not active_configs.exists():
        return {
            'success': False,
            'error': 'Нет активных конфигураций для индексации'
        }
    
    results = {}
    total_stats = {
        'total_files': 0,
        'total_new': 0,
        'total_updated': 0,
        'total_deleted': 0
    }
    
    for config in active_configs:
        try:
            indexer = SMBFileIndexer(config)
            stats = indexer.scan_and_index(force_rescan)
            results[config.name] = stats
            
            total_stats['total_files'] += stats['total_found']
            total_stats['total_new'] += stats.get('new_files', 0)
            total_stats['total_updated'] += stats.get('updated_files', 0)
            total_stats['total_deleted'] += stats.get('deleted_files', 0)
            
        except Exception as e:
            results[config.name] = {'error': str(e)}
            print(f"❌ Ошибка при индексации {config.name}: {e}")
    
    return {
        'success': True,
        'results': results,
        'total_stats': total_stats
    }