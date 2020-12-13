import random
import string

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import (RetrieveUpdateDestroyAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .filters import TitlesFilter
from .models import Category, Genre, Review, Title, User
from .permissions import (IsAdmin, IsAdminOrReadOnly, IsAnon, IsModerator,
                          RetrieveUpdateDestroyPermission, IsOwner)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, PushEmailSerializer,
                          ReviewSerializer, TitleSerializer,
                          UsesrsSerializer,
                          YamdbTokenObtainPairSerializer)


def generate_code():
    letters = string.ascii_uppercase
    code = ''.join(random.choice(letters) for i in range(6))
    return code


class BaseCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass


class BaseListUpdateViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin,
                            viewsets.GenericViewSet):
    pass


class PushEmailViewSet(BaseCreateViewSet):
    queryset = User.objects.all()
    serializer_class = PushEmailSerializer

    def perform_create(self, serializer):
        generated_data = generate_code()

        user = User.objects.create_user(
            email=self.request.data.get('email'),
            username=self.request.data.get('email').partition("@")[0],
            password=generated_data
        )

        user_email = user.email
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Yours confirmation code',
            message=f'confirmation_code: {confirmation_code}',
            from_email='registration@yamdb.fake',
            recipient_list=(user_email,),
            fail_silently=False
        )


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = YamdbTokenObtainPairSerializer


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsesrsSerializer
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated, IsOwner)
    filter_backends = [filters.SearchFilter]
    search_fields = ('username',)
    lookup_field = 'username'

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        user = self.request.user
        allow_all = user.is_superuser or user.is_staff
        if self.action == 'list' and not allow_all:
            raise PermissionDenied('ERROR: Access denied')
        return User.objects.all()

    @action(detail=False, methods=['GET', 'PATCH'], url_path='me',
            permission_classes=(IsOwner, IsAuthenticated,))
    def get_or_update_user(self, request):
        himself = User.objects.get(username=self.request.user)
        if request.method == 'GET':
            serializer = self.get_serializer(himself)
            return Response(serializer.data)
        if request.method == 'PATCH':
            serializer = self.get_serializer(himself, data=request.data,
                                             partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewListCreateSet(mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    permission_classes = [IsAnon | IsAdmin | IsModerator | IsAuthenticated]
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        author = self.request.user
        text = self.request.data.get('text')

        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)

        reviews = Review.objects.filter(author=author, title=title)
        if reviews.count() > 0:
            return True

        serializer.save(title=title, author=author, text=text)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        queryset = title.reviews.all()
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        not_create_success = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        if not_create_success:
            return Response(
                serializer.data,
                status=status.HTTP_400_BAD_REQUEST,
                headers=headers
            )
        else:
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )


class ReviewRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [RetrieveUpdateDestroyPermission, ]

    def get_object(self):
        obj = get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["review_id"]
        )
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        queryset = title.reviews.all()
        return queryset


class CommentListCreateSet(mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           viewsets.GenericViewSet):
    permission_classes = [IsAnon | IsAdmin | IsModerator | IsAuthenticated]
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        author = self.request.user
        text = self.request.data.get('text')

        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        title = get_object_or_404(Title, id=title_id)
        review = get_object_or_404(title.reviews, id=review_id)
        serializer.save(review=review, author=author, text=text)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        title = get_object_or_404(Title, id=title_id)
        review = get_object_or_404(title.reviews.all(), id=review_id)
        queryset = review.comments.all()
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        not_create_success = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        if not_create_success:
            return Response(
                serializer.data,
                status=status.HTTP_400_BAD_REQUEST,
                headers=headers
            )
        else:
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )


class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [RetrieveUpdateDestroyPermission, ]

    def get_object(self):
        obj = get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["comment_id"]
        )
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        title = get_object_or_404(Title, id=title_id)
        review = get_object_or_404(title.reviews.all(), id=review_id)
        queryset = review.comments
        return queryset


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['name']
    lookup_field = 'slug'


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['name']
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(ratings=Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitlesFilter
