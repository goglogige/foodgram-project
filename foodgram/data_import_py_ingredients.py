import csv
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'foodgram.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from recipes.models import Ingredient


with open('foodgram\ingredients_.csv') as csvfile:
    ingredient_reader = csv.reader(csvfile)
    i = 0
    for line in ingredient_reader:
        ingredient = Ingredient(title=line[0], dimension=line[1])
        try:
            ingredient.save()
        except:
            print("There was a problem with line", i)
        i =+ 1
    print("Success!")