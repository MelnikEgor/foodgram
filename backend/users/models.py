from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from backend.constants import (
    FIRST_NAME_MAX_LENGTH,
    LAST_NAME_MAX_LENGTH,
    NAME_LENGTH
)


class User(AbstractUser):
    """Кастомная модель пользователя."""

    first_name = models.CharField(
        'Имя',
        max_length=FIRST_NAME_MAX_LENGTH,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=LAST_NAME_MAX_LENGTH,
    )
    email = models.EmailField(
        'Электронная почта',
        unique=True,
        error_messages={
            'unique': (
                'Пользователь с такой электронной почтой уже существует.'
            ),
            'blank': 'Адрес электронной почты обязателен.'
        },
    )
    avatar = models.ImageField(
        upload_to='users/',
        null=True,
        default=None,
        blank=True,
        verbose_name='Аватар'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username', 'email')

    def clean(self):
        super().clean()
        username = self.username
        if username.lower() == 'me':
            raise ValidationError(
                f"Имя пользователя не должно быть '{username}'"
            )

    def __str__(self):
        return self.username[:NAME_LENGTH]


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        blank=True,
        null=True,
        verbose_name='Подписка'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (str(self.user) + ' подписан на ' + str(self.following))
