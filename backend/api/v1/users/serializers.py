from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.v1.fields import Base64ImageField
from api.v1.foods.recipe_short_serializer import RecipeShortReadSerializer
from api.v1.mixins import UserameNotMeMixin
from api.v1.utils import check_field


User = get_user_model()


class UserWriteSerializer(serializers.ModelSerializer, UserameNotMeMixin):
    """Сериализатор регистрации пользователя."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения пользователей."""

    is_subscribed = serializers.SerializerMethodField(
        'get_is_subscribed',
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name'
        )

    def get_is_subscribed(self, obj):
        obj = obj.subscriber.all()
        return check_field(self, obj)


class FollowSerializer(UserReadSerializer):
    """Сериализатор подписок пользователя."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
                recipes = recipes[:recipes_limit]
            except ValueError:
                pass
        serializer = RecipeShortReadSerializer(
            recipes,
            read_only=True,
            many=True
        )
        return serializer.data


class PasswordSerializer(serializers.ModelSerializer):
    """Сериализатор смены пароля."""

    new_password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            'blank': 'Новый пароль не может быть пустым.',
        },
    )
    current_password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            'blank': 'Текущий пароль не может быть пустым.',
        },
    )

    class Meta:
        model = User
        fields = ('new_password', 'current_password')

    def validate(self, attrs):
        current_password = attrs['current_password']
        if not self.instance.check_password(current_password):
            raise serializers.ValidationError(
                {
                    'current_password': 'Текущий пароль не такой.'
                }
            )
        if attrs['new_password'] == current_password:
            raise serializers.ValidationError(
                {
                    'new_password': 'Новый пароль похож на старый.'
                }
            )
        return attrs


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватара пользователя."""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = (
            'avatar',
        )
