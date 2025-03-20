import json

from django.core.management.base import BaseCommand, CommandError

from foods.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            with open('data/ingredients.json', 'rb') as file:
                ingredients_data = json.load(file)
                Ingredient.objects.bulk_create(
                    Ingredient(**ingredient) for ingredient in ingredients_data
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Успешно импортировано {Ingredient.objects.count()}.'
                    )
                )
        except Exception as e:
            raise CommandError(f'Ошибка при импорте данных: {e}')
