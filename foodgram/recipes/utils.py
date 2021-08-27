import json
import reportlab

from django.template.defaultfilters import slugify as django_slugify
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db import transaction

from decimal import Decimal
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from foodgram import settings
from .models import (
    User, Ingredient, Recipe,
    RecipeIngredient, Purchase,
)


alphabet = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ы': 'y', 
    'э': 'eh', 'ю': 'yu', 'я': 'ya'
}


def slugify(s):
    """
    Overriding django slugify that allows to use russian words as well.
    """
    return django_slugify(''.join(alphabet.get(w, w) for w in s.lower()))


def pdf_download(request):
    user = get_object_or_404(User, username=request.user)
    pchs_dict = {}
    purchase_list = Purchase.objects.filter(user=user)
    if purchase_list.count() == 0:
        return redirect('purchases')
    for purchase in purchase_list:
        recipe_ingredient_list = RecipeIngredient.objects.filter(
            recipe__id=purchase.recipe.id
        )
        for recipe_ingredient in recipe_ingredient_list:
            title = recipe_ingredient.ingredient.title
            amount = recipe_ingredient.amount
            dimension = recipe_ingredient.ingredient.dimension
            if title not in pchs_dict:
                pchs_dict[title] = [amount, dimension]
            else:
                pchs_dict[title][0] += amount

    reportlab.rl_config.TTFSearchPath.append(
        str(settings.BASE_DIR) + "/Library/Fonts/"
    )
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="recipes.pdf"'
    pdf = canvas.Canvas(response, pagesize='A4', pageCompression=0)
    pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
    pdf.setFont('Arial', 22)
    title = 'My shopping list | Foodgram'
    pdf.setTitle(title)
    pdf.drawCentredString(290, 760, title)
    pdf.setFont('Arial', 18)
    x = 40
    y = 700
    for i, item in enumerate(pchs_dict):
        if y <= 100:
            y = 700
            pdf.showPage()
            pdf.setFont('Arial', 12)
        pdf.drawString(
            x, y, f'{i + 1}:{item} - {pchs_dict[item][0]} {pchs_dict[item][1]}'
        )
        y -= 30
    pdf.showPage()
    pdf.save()
    return response


def get_ingredients(request):
    ingredients = {}
    post = request.POST
    for key, name in post.items():
        if key.startswith('nameIngredient'):
            num = key.partition('_')[-1]
            ingredients[name] = post[f'valueIngredient_{num}']
    return ingredients


def save_recipe(request, form):
    with transaction.atomic():
        recipe = form.save(commit=False)
        recipe.author = request.user
        recipe.slug = slugify(recipe.recipe_name)
        recipe.save()

        obj = []
        ingredients = get_ingredients(request)

        for name, amount in ingredients.items():
            ingredient = get_object_or_404(Ingredient, title=name)
            obj.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=Decimal(amount.replace(',', '.'))
                )
            )

        RecipeIngredient.objects.bulk_create(obj)
        form.save_m2m()
        return recipe


class ObjectsProcessor:

    def __init__(self, object, request):
        self.object = object
        self.request = request

    def add_obj(self):
        user = self.request.user
        json_data = json.loads(self.request.body.decode())
        recipe_id = int(json_data['id'])
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.object.objects.get_or_create(user=user, recipe=recipe)
        data = {'success': 'True'}
        return JsonResponse(data)
    
    def delete_obj(self, id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=id)
        object = self.object.objects.filter(user=user, recipe=recipe)
        data = {'success': 'True'}
        # if not object.exists():
        #     data['success'] = 'False'
        #     return JsonResponse(data)
        # object.delete()
        # return JsonResponse(data)
        if object.delete() == 0:
            data['success'] = 'False'
            return JsonResponse(data)
        return JsonResponse(data)
