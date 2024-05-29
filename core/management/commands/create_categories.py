from django.core.management.base import BaseCommand
from core.models import Category
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Create unique categories'

    def handle(self, *args, **kwargs):
        category_names = [
            "Appetizers",
            "Desserts",
            "Main Courses",
            "Seafood",
            "Seafood",
            "Seafood",
            "Main Courses",
            "Desserts",
            "Sandwiches",
            "Desserts"
        ]

        unique_categories = set(category_names)

        for category_name in unique_categories:
            try:
                Category.objects.create(name=category_name)
            except IntegrityError:
                # Handle the IntegrityError (category name already exists)
                pass

        self.stdout.write(self.style.SUCCESS('Successfully created unique categories'))