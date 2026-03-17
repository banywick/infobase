import os
from smbclient import register_session, listdir

# smb_client.py (дополненный методом upload)
import os
from smbclient import register_session, listdir, open_file

class SmbFolderVk:
    """
    Класс для работы с SMB папкой
    """
    
    def __init__(self):
        self.server = "10.29.107.16"
        self.share = "белоус а.н"
        self.folder = "тест скрипта"
        self.username = "belousan"
        self.password = "9e3e2fPr2"
        self.port = 445       
        
        # Регистрируем сессию при создании
        print(f"🔌 Подключение к SMB: {self.server}")
        register_session(
            self.server, 
            username=self.username, 
            password=self.password, 
            port=self.port
        )
    
    def get_files(self):
        """Получение списка файлов из SMB папки"""
        full_path = f"\\\\{self.server}\\{self.share}\\{self.folder}"
        print(f"📂 Читаем папку: {full_path}")
        
        files = listdir(full_path)
        file_names = [os.path.basename(f) for f in files]
        
        return file_names
    
    def download_file(self, filename, destination_folder):
        """
        Скачивание файла из SMB
        """
        source = f"\\\\{self.server}\\{self.share}\\{self.folder}\\{filename}"
        destination = os.path.join(destination_folder, filename)
        
        # Создаем папку если нужно
        os.makedirs(destination_folder, exist_ok=True)
        
        # Копируем файл
        with open_file(source, mode='rb') as smb_file:
            with open(destination, 'wb') as local_file:
                local_file.write(smb_file.read())
        
        print(f"✅ Файл скачан: {destination}")
        return destination
    
    def upload_file(self, local_file_path, target_subfolder):
        """
        Загрузка файла в SMB папку
        
        Args:
            local_file_path: путь к локальному файлу
            target_subfolder: подпапка в шаре (например "результат")
        
        Returns:
            str: путь к файлу в SMB
        """
        filename = os.path.basename(local_file_path)
        target_path = f"\\\\{self.server}\\{self.share}\\{target_subfolder}\\{filename}"
        
        print(f"📤 Загружаем в SMB: {target_path}")
        
        with open(local_file_path, 'rb') as local_file:
            with open_file(target_path, mode='wb') as smb_file:
                smb_file.write(local_file.read())
        
        print(f"✅ Загружено: {target_path}")
        return target_path