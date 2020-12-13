from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentListCreateSet,
                    CommentRetrieveUpdateDestroyAPIView, GenreViewSet,
                    MyTokenObtainPairView, PushEmailViewSet,
                    ReviewListCreateSet, ReviewRetrieveUpdateDestroyAPIView,
                    TitleViewSet, UsersViewSet)

router_v1 = DefaultRouter()
router_v1.register(r'auth/email', PushEmailViewSet, basename='register')
router_v1.register(r'users', UsersViewSet, basename='users')
router_v1.register(r'categories', CategoryViewSet, basename='categories')
router_v1.register(r'genres', GenreViewSet, basename='genres')
router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewListCreateSet,
    basename='comments'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentListCreateSet,
    basename='comments'
)


urlpatterns = [
    path('v1/auth/token/', MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path(
         'v1/titles/<int:title_id>/reviews/<int:review_id>/',
         ReviewRetrieveUpdateDestroyAPIView.as_view(),
         name='review'
         ),
    path('v1/titles/<int:title_id>/reviews/<int:review_id>/'
         'comments/<int:comment_id>/',
         CommentRetrieveUpdateDestroyAPIView.as_view(),
         name='review'
         ),
    path('v1/', include(router_v1.urls)),
]
