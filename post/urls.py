from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import CommentViewSet, LikePostAPIView

app_name = "posts"

router = DefaultRouter()
router.register(r"^(?P<post_id>\d+)/comment", CommentViewSet)

urlpatterns = [
    path('', views.PostList.as_view()),
    path('<int:id>', views.PostDetails.as_view()),
    path("", include(router.urls)),
    path("like/<int:pk>/", LikePostAPIView.as_view(), name="like-post"),
]
