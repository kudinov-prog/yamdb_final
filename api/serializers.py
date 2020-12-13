from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Category, Comment, Genre, Review, Title, User


class PushEmailSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=None, min_length=None,
                                  allow_blank=False)

    class Meta:
        model = User
        fields = ('email',)


class YamdbTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.CharField(max_length=None, min_length=None,
                                  allow_blank=False, write_only=True)
    confirmation_code = serializers.CharField(allow_blank=False,
                                              write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ('confirmation_code', 'email', 'token')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].required = False
        self.fields[self.username_field].required = False

    def validate(self, attrs):
        user = User.objects.get(email=attrs['email'])
        attrs.update({'password': user.confirmation_code})
        attrs.update({'username': user.username})

        return super(YamdbTokenObtainPairSerializer, self).validate(attrs)


class UserInfoSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(source='description', allow_blank=True,
                                allow_null=True)

    class Meta:
        model = User
        fields = (
            'bio', 'first_name', 'last_name',
            'username', 'email', 'role'
        )
        read_only_fields = ('role',)
        extra_kwargs = {
            'bio': {'allow_blank': True, 'allow_null': True},
            'first_name': {'allow_blank': True, 'allow_null': True},
            'last_name': {'allow_blank': True, 'allow_null': True},
        }


class UsesrsSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(required=False)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name',
            'username', 'bio', 'email', 'role'
        )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    review = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )
    title = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    def validate_score(self, score):
        if score < 1 or score > 10:
            raise serializers.ValidationError("Оценка должна между 1 и 10.")
        return score

    class Meta:
        model = Review
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'name', 'slug'
        )


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = (
            'name', 'slug'
        )


class CategoryField(serializers.SlugRelatedField):

    def to_representation(self, value):
        serializer = CategorySerializer(value)
        return serializer.data


class GenreField(serializers.SlugRelatedField):

    def to_representation(self, value):
        serializer = GenreSerializer(value)
        return serializer.data


class TitleSerializer(serializers.ModelSerializer):
    category = CategoryField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=False
    )
    genre = GenreField(slug_field='slug', queryset=Genre.objects.all(),
                       many=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
