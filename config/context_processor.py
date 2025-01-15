# from finder.utils import connect_redis

# def get_file_name(request):
#     file_name = connect_redis().get("file_name")
#     if file_name:
#         file_name = file_name.decode("utf8")
#         return {"file_name": file_name}
#     return {"file_name": file_name}


# def user_permission_is_in_group(request):
#     """Распределение пользователей по группам для отображения ссылок"""
#     groups = request.user.groups.values_list('name', flat=True)
#     return {
#         'user_is_in_group_update': 'update_base' in groups,
#         'user_is_in_group_commers': 'commers' in groups,
#         'user_is_in_group_inventory': 'inventory' in groups,
#         'user_is_in_group_inventory_guest': 'inventory_guest' in groups,
#     }