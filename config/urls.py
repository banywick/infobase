from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', RedirectView.as_view(url='finder/', permanent=True)),
    path('admin/', admin.site.urls),
    path('auth/', include('auth.urls')),
    path('finder/', include('finder.urls')),
    path('sahr/', include('sahr.urls')),
    path('notes/', include('notes.urls')),
    path('reviews/', include('reviews.urls')),
    path('comers/', include('comers.urls')),
    path('special_cars/', include('cars.urls')),
    path('access_denited/', include('common.urls')),
    path('workwear/', include('workwear.urls', namespace='workwear')),  # <-- namespace указан
    # path('inventory/', include('inventory.urls')),
]

# Подключаем Swagger и ReDoc только в режиме разработки
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        re_path('doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        re_path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]
