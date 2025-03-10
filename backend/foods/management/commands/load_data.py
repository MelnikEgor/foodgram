import json

from django.core.management.base import BaseCommand, CommandError
from foods.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):

        try:
            with open('data/ingredients.json', 'rb') as file:
                ingredients_data = json.load(file)
                for ingredient_data in ingredients_data:
                    ingredient = Ingredient(**ingredient_data)
                    ingredient.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Успешно импортировано {len(ingredients_data)}.'
                    )
                )
        except Exception as e:
            raise CommandError(f'Ошибка при импорте данных: {e}')
