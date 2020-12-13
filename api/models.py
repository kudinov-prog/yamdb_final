from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    DJADMIN = "djadmin"
    ROLES = (
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
        (DJADMIN, 'djadmin'),
    )
    bio = models.TextField(max_length=500, blank=True, null=True)
    role = models.CharField(max_length=30, choices=ROLES, default='user')
    confirmation_code = models.CharField(max_length=100, default='FOOBAR')


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    year = models.IntegerField(null=True, blank=True, db_index=True)
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True,
        db_column='category'
    )

    def __str__(self):
        return self.name

    @property
    def rating(self):
        reviews = self.reviews.all()
        score_avg = reviews.aggregate(models.Avg('score')).get('score__avg')
        return None if isinstance(score_avg, type(None)) else int(score_avg)


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        db_column='author'
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField('date published', auto_now_add=True,
                                    db_index=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.title}, {self.score}, {self.author}'


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        db_column='author'
    )
    pub_date = models.DateTimeField('date published', auto_now_add=True,
                                    db_index=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.author}, {self.pub_date:%d.%m.%Y}, {self.text[:50]}'
