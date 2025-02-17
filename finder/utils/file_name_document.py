from .connect_redis_bd import connect_redis

def get_file_name(request):
    """Получить имя документа"""
    file_name = connect_redis().get("file_name")
    if file_name:
        file_name = file_name.decode("utf8")
        return {"file_name": file_name}
    return {"file_name": file_name}