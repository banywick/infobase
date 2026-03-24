# statement/smb_client.py

import os
from smbclient import register_session, listdir, open_file, mkdir

class SmbFolderVk:
    """
    Класс для работы с SMB папкой
    """
    
    def __init__(self, server=None, share=None, username=None, password=None, port=445):
        """
        Инициализация SMB клиента
        
        Args:
            server: сервер SMB (если None, использует значения по умолчанию)
            share: шара SMB (если None, использует значения по умолчанию)
            username: имя пользователя
            password: пароль
            port: порт (обычно 445)
        """
        # Значения по умолчанию
        self.server = server
        self.share = share
        self.username = username or "belousan"
        self.password = password or "9e3e2fPr2"
        self.port = port
        self.debug = True
        
        # Регистрируем сессию
        print(f"🔌 Подключение к SMB: {self.server}")
        register_session(
            self.server, 
            username=self.username, 
            password=self.password, 
            port=self.port
        )
    
    def _log(self, message, level="INFO"):
        if self.debug:
            print(f"[{level}] {message}")
    
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
        
        Args:
            search_root: корневая папка для поиска (если None, использует server/share)
        
        Returns:
            list: список словарей с информацией о каждом элементе
        """
        if search_root is None:
            search_root = f"\\\\{self.server}\\{self.share}"
        
        self._log(f"📂 Сканируем: {search_root}")
        result = []
        
        try:
            items = listdir(search_root)
            self._log(f"   Найдено элементов: {len(items)}")
            
            for item in items:
                item_path = f"{search_root}\\{item}"
                is_dir = self._is_directory(item_path)
                
                item_info = {
                    'name': item,
                    'path': item_path,
                    'is_directory': is_dir,
                    'relative_path': self._get_relative_path(item_path, search_root),
                    'root': search_root
                }
                
                result.append(item_info)
                self._log(f"   {'📁' if is_dir else '📄'} {item}")
                
                if is_dir:
                    children = self.get_all_files_and_folders_recursive(item_path)
                    result.extend(children)
                    
        except Exception as e:
            self._log(f"   ❌ Ошибка: {e}", "ERROR")
        
        return result
    
    def find_files_recursive(self, search_root, extensions=['.xlsx', '.xls', '.xlsm']):
        """
        Найти все файлы с указанными расширениями
        
        Args:
            search_root: корневая папка для поиска
            extensions: список расширений для фильтрации
        
        Returns:
            list: список файлов с информацией
        """
        all_items = self.get_all_files_and_folders_recursive(search_root)
        
        files = []
        for item in all_items:
            if not item['is_directory']:
                if any(item['name'].endswith(ext) for ext in extensions):
                    files.append(item)
        
        return files
    
    def download_file(self, source_path, destination_folder):
        """
        Скачивание файла из SMB
        
        Args:
            source_path: полный путь к файлу в SMB
            destination_folder: локальная папка для сохранения
        
        Returns:
            str: путь к скачанному файлу
        """
        filename = os.path.basename(source_path)
        destination = os.path.join(destination_folder, filename)
        
        os.makedirs(destination_folder, exist_ok=True)
        
        print(f"📥 Скачиваем: {source_path} -> {destination}")
        
        with open_file(source_path, mode='rb') as smb_file:
            with open(destination, 'wb') as local_file:
                local_file.write(smb_file.read())
        
        print(f"✅ Файл скачан: {destination}")
        return destination
    
    def upload_file(self, local_file_path, target_path):
        """
        Загрузка файла в SMB
        
        Args:
            local_file_path: путь к локальному файлу
            target_path: полный путь для сохранения в SMB
        
        Returns:
            str: путь к загруженному файлу в SMB
        """
        print(f"📤 Загружаем в SMB: {target_path}")
        
        # Создаем папку если нужно
        target_dir = os.path.dirname(target_path)
        try:
            mkdir(target_dir)
            print(f"📁 Создана папка: {target_dir}")
        except Exception:
            # Папка уже существует
            pass
        
        with open(local_file_path, 'rb') as local_file:
            with open_file(target_path, mode='wb') as smb_file:
                smb_file.write(local_file.read())
        
        print(f"✅ Загружено: {target_path}")
        return target_path
    
    # Остальные методы для обратной совместимости
    def get_files(self):
        """Получение списка файлов из SMB папки (только корневая папка)"""
        full_path = f"\\\\{self.server}\\{self.share}"
        print(f"📂 Читаем папку: {full_path}")
        
        files = listdir(full_path)
        file_names = [os.path.basename(f) for f in files]
        
        return file_names