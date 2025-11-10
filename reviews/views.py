from django.views.generic import TemplateView
from rest_framework.generics import CreateAPIView
from finder.models import Review
from .serializers import ReviewSerializer

class ReviewsView(TemplateView):
    """
    Класс представления для отображения главной страницы с отзывами.

    Этот класс использует шаблон 'reviews/index.html' для рендеринга
    главной страницы, где могут быть отображены отзывы пользователей.

    Attributes:
        template_name (str): Путь к шаблону, используемому для рендеринга страницы.
    """
    template_name = 'reviews/index.html'

class AddReview(CreateAPIView):
    """
    Класс представления для создания нового отзыва.

    Этот класс предоставляет API-эндпоинт для создания новых отзывов.
    Он использует сериализатор `ReviewSerializer` для валидации данных
    и сохранения нового отзыва в базе данных.

    Attributes:
        queryset (QuerySet): Набор запросов, содержащий все объекты модели `Review`.
        serializer_class (class): Класс сериализатора, используемый для валидации и сохранения данных.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
