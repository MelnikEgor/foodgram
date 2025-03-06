from django.apps import AppConfig


class FoodsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foods'
    verbose_name = 'Еда'
    verbose_name_plural = 'еда'
