import csv
import os

from django.core.wsgi import get_wsgi_application

from recipes.models import Ingredient


os.environ['DJANGO_SETTINGS_MODULE'] = 'foodgram.settings'

application = get_wsgi_application()

with open('ingredients_.csv') as csvfile:
    ingredient_reader = csv.reader(csvfile)
    i = 0
    for line in ingredient_reader:
        ingredient = Ingredient(title=line[0], dimension=line[1])
        try:
            ingredient.save()
        except ValueError:
            print("There was a problem with line", i)
        i = + 1
    print("Success!")