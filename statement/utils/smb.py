# statement/utils/smb.py

import os
from smbclient import register_session, listdir, open_file, mkdir, stat as smb_stat
from smbclient._os import scandir
import logging
import ntpath

logger = logging.getLogger(__name__)


class SmbFolderVk:
    """
    Класс для работы с SMB папкой
    """
    
    def __init__(self, server=None, share=None, username=None, password=None, port=None):
        """
        Инициализация SMB клиента
        """
        # Загружаем настройки из .env
        self.username = username or os.getenv('SMB_USERNAME')
        self.password = password or os.getenv('SMB_PASSWORD')
        self.port = int(port or os.getenv('SMB_PORT', 445))
        
        # Проверяем обязательные параметры
        if not self.username:
            raise ValueError("SMB_USERNAME не задан в .env файле или не передан в конструктор")
        if not self.password:
            raise ValueError("SMB_PASSWORD не задан в .env файле или не передан в конструктор")
        
        # Устанавливаем сервер и шару
        self.server = server or os.getenv('SMB_SERVER')
        self.share = share or os.getenv('SMB_SHARE')
        
        # Настройка дебага
        self.debug = os.getenv('SMB_DEBUG', 'True').lower() == 'true'
        
        # Регистрируем сессию
        try:
            self._log(f"🔌 Подключение к SMB серверу: {self.server or 'по умолчанию'}")
            
            if self.server:
                register_session(
                    self.server,
                    username=self.username,
                    password=self.password,
                    port=self.port
                )
                self._log(f"✅ SMB сессия зарегистрирована для {self.username}@{self.server}")
            else:
                register_session(
                    username=self.username,
                    password=self.password,
                    port=self.port
                )
                self._log(f"✅ SMB сессия зарегистрирована для {self.username}")
                
        except Exception as e:
            self._log(f"❌ Ошибка регистрации SMB сессии: {e}", "ERROR")
            raise
    
    def _log(self, message, level="INFO"):
        """Логирование с учетом debug режима"""
        if self.debug:
            if level == "ERROR":
                logger.error(message)
            elif level == "WARNING":
                logger.warning(message)
            else:
                logger.info(message)
            print(f"[{level}] {message}")
    
    def _build_full_path(self, path=""):
        """Формирует полный путь UNC"""
        if path.startswith('\\\\'):
            return path
        
        if self.server and self.share:
            if path:
                return f"\\\\{self.server}\\{self.share}\\{path}"
            return f"\\\\{self.server}\\{self.share}"
        
        return path
    
    def stat_file(self, file_path):
        """
        Получает информацию о файле (stat)
        
        Args:
            file_path: путь к файлу в SMB
        
        Returns:
            stat_result: объект с информацией о файле или None
        """
        try:
            # Если путь не полный, строим полный путь
            if not file_path.startswith('\\\\'):
                file_path = self._build_full_path(file_path)
            
            # Используем функцию stat из smbclient
            stat_result = smb_stat(file_path)
            return stat_result
        except Exception as e:
            self._log(f"⚠️ Не удалось получить stat для {file_path}: {e}", "WARNING")
            return None
    
    def get_file_size(self, file_path):
        """
        Получает размер файла в байтах
        
        Args:
            file_path: путь к файлу в SMB
        
        Returns:
            int: размер файла или 0
        """
        stat_result = self.stat_file(file_path)
        if stat_result:
            return stat_result.st_size
        return 0
    
    def get_file_mtime(self, file_path):
        """
        Получает время последнего изменения файла
        
        Args:
            file_path: путь к файлу в SMB
        
        Returns:
            float: timestamp или None
        """
        stat_result = self.stat_file(file_path)
        if stat_result and hasattr(stat_result, 'st_mtime'):
            return stat_result.st_mtime
        return None
    
    def _is_directory(self, path):
        """Проверяет, является ли путь директорией"""
        try:
            items = listdir(path)
            return True
        except Exception:
            return False
    
    def _get_relative_path(self, full_path, root_path):
        """Получает относительный путь от корневой папки"""
        if full_path.startswith(root_path):
            relative = full_path[len(root_path):].lstrip('\\')
            return relative if relative else '.'
        return full_path
    
    def get_all_files_and_folders_recursive(self, search_root=None):
        """
        Рекурсивное получение всех файлов и папок
        """
        if search_root is None:
            search_root = self._build_full_path()
        
        self._log(f"📂 Сканируем: {search_root}")
        result = []
        
        try:
            items = listdir(search_root)
            self._log(f"   Найдено элементов: {len(items)}")
            
            for item in items:
                item_path = f"{search_root}\\{item}"
                is_dir = self._is_directory(item_path)
                
                # Получаем информацию о файле через stat
                file_size = None
                modified_time = None
                if not is_dir:
                    stat_result = self.stat_file(item_path)
                    if stat_result:
                        file_size = stat_result.st_size
                        if hasattr(stat_result, 'st_mtime'):
                            modified_time = stat_result.st_mtime
                
                item_info = {
                    'name': item,
                    'path': item_path,
                    'is_directory': is_dir,
                    'relative_path': self._get_relative_path(item_path, search_root),
                    'root': search_root,
                    'size': file_size,
                    'modified_time': modified_time
                }
                
                result.append(item_info)
                self._log(f"   {'📁' if is_dir else '📄'} {item}")
                
                if is_dir:
                    children = self.get_all_files_and_folders_recursive(item_path)
                    result.extend(children)
                    
        except Exception as e:
            self._log(f"   ❌ Ошибка при сканировании {search_root}: {e}", "ERROR")
        
        return result
    
    def find_files_recursive(self, search_root=None, extensions=None):
        """
        Найти все файлы с указанными расширениями
        """
        if extensions is None:
            extensions = ['.xlsx', '.xls', '.xlsm']
        
        if search_root is None:
            search_root = self._build_full_path()
        
        all_items = self.get_all_files_and_folders_recursive(search_root)
        
        files = []
        for item in all_items:
            if not item['is_directory']:
                if any(item['name'].lower().endswith(ext.lower()) for ext in extensions):
                    files.append(item)
        
        self._log(f"✅ Найдено {len(files)} файлов с расширениями {extensions}")
        return files
    
# statement/utils/smb.py

    def download_file(self, source_path, destination_folder):
        """
        Скачивание файла из SMB
        """
        import ntpath
        from smbclient import open_file as smb_open
        
        # Нормализуем путь
        source_path = source_path.replace('/', '\\')
        
        if not source_path.startswith('\\\\'):
            source_path = self._build_full_path(source_path)
        
        filename = ntpath.basename(source_path)
        destination = os.path.join(destination_folder, filename)
        
        os.makedirs(destination_folder, exist_ok=True)
        
        self._log(f"📥 Скачиваем: {source_path} -> {destination}")
        
        try:
            # Используем контекстный менеджер
            with smb_open(source_path, mode='rb') as smb_file:
                data = smb_file.read()
                
            with open(destination, 'wb') as local_file:
                local_file.write(data)
            
            self._log(f"✅ Скачано {len(data)} байт")
            return destination
            
        except Exception as e:
            self._log(f"❌ Ошибка: {e}", "ERROR")
            raise
    def upload_file(self, local_file_path, target_path):
        """
        Загрузка файла в SMB
        """
        if not target_path.startswith('\\\\'):
            target_path = self._build_full_path(target_path)
        
        self._log(f"📤 Загружаем в SMB: {target_path}")
        
        target_dir = os.path.dirname(target_path)
        try:
            mkdir(target_dir)
            self._log(f"📁 Создана папка: {target_dir}")
        except Exception:
            pass
        
        try:
            with open(local_file_path, 'rb') as local_file:
                with open_file(target_path, mode='wb') as smb_file:
                    smb_file.write(local_file.read())
            
            self._log(f"✅ Загружено: {target_path}")
            return target_path
        except Exception as e:
            self._log(f"❌ Ошибка при загрузке: {e}", "ERROR")
            raise
    
    def file_exists(self, file_path):
        """
        Проверяет существование файла
        """
        if not file_path.startswith('\\\\'):
            file_path = self._build_full_path(file_path)
        
        try:
            smb_stat(file_path)
            return True
        except Exception:
            return False
    
    def get_files(self, path=""):
        """
        Получение списка файлов из SMB папки (только корневая папка)
        """
        full_path = self._build_full_path(path)
        self._log(f"📂 Читаем папку: {full_path}")
        
        try:
            files = listdir(full_path)
            file_names = [os.path.basename(f) for f in files]
            self._log(f"✅ Найдено файлов: {len(file_names)}")
            return file_names
        except Exception as e:
            self._log(f"❌ Ошибка при чтении папки: {e}", "ERROR")
            return []