# utils.py
# statement/utils.py

from django.core.cache import cache

from statement.models import SMBPathConfig

def get_active_smb_config():
    """
    Получить активную конфигурацию SMB путей
    """
    try:
        
        cache_key = 'active_smb_config'
        config = cache.get(cache_key)
        
        if config is None:
            config = SMBPathConfig.objects.filter(is_active=True).first()
            if config:
                cache.set(cache_key, config, 3600)
                print(f"✅ Загружена конфигурация: {config.name}")
            else:
                print("⚠️ Активная конфигурация не найдена")
        
        return config
    except Exception as e:
        print(f"❌ Ошибка получения конфигурации: {e}")
        return None

