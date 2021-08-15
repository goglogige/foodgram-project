import io
import json
import reportlab

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from django.urls import resolve
from django.db.models.query import Prefetch
from decimal import Decimal
#from django.views.decorators.cache import cache_page
from django.http import FileResponse

from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from foodgram.settings import PAGINATION_SIZE
from foodgram import settings
from .models import (
    User, Ingredient, Recipe, RecipeIngredient, 
    Tag, Purchase, Favorite, Follow
    )
from .forms import RecipeForm
from .utils import slugify


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


def ingredients(request):
    ingredients_queryset = Ingredient.objects.values()
    list_ingredients = [ingredient for ingredient in ingredients_queryset] 

    return JsonResponse(
        list_ingredients,
        safe=False,
    ) 


@login_required()
def add_purchases(request):
    user = request.user
    json_data = json.loads(request.body.decode())
    recipe_id = int(json_data['id'])
    recipe = get_object_or_404(Recipe, id=recipe_id)
    purchase = Purchase.objects.filter(user=user, recipe=recipe)
    data = {'success': 'True'}
    if not purchase.exists():
        Purchase.objects.create(user=user, recipe=recipe)
        return JsonResponse(data)
    data['success'] = 'False'       
    return JsonResponse(data)


@login_required()
def button_delete_purchases(request, id):
    user = request.user
    recipe = get_object_or_404(Recipe, id=id)
    purchase = Purchase.objects.filter(user=user, recipe=recipe)
    data = {'success': 'True'} 
    if not purchase.exists():
        data['success'] = 'False'
        return JsonResponse(data)
    purchase.delete()
    return JsonResponse(data)


@login_required()
def delete_purchases(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    purchase.delete()
    purchase_list = Purchase.objects.filter(user=request.user)
    return render(
        request,
        'purchases.html',
        {'purchase_list': purchase_list,}
    )


@login_required()
def purchases_view(request):
    purchase_list = Purchase.objects.filter(user=request.user)
    count_purchase = Purchase.objects.filter(user=request.user).count()
    return render(
        request,
        'purchases.html',
        {'purchase_list': purchase_list, 'count_purchase': count_purchase}
    )


@login_required
def purchases_download(request):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="recipes.pdf"'
    pdf = canvas.Canvas(response, pagesize='A4', pageCompression=0)

    title = 'My shopping list | Foodgram'
    pdf.setTitle(title)
    pdf.setFont('Helvetica', 22)
    pdf.drawCentredString(270, 770, title)

    user = get_object_or_404(User, username=request.user)
    purchase_dict = {}
    purchase_list = Purchase.objects.filter(user=user)
    if purchase_list.count() == 0:
        return redirect('purchases')
    k = 0
    for purchase in purchase_list:
        pdf.setFont('Helvetica', 18)
        pdf.drawCentredString(120, 750 - k, purchase.recipe.recipe_name)

        recipe_ingredient_list = RecipeIngredient.objects.filter(recipe__id=purchase.recipe.id)
        h = 1
        num = 1
        for recipe_ingredient in recipe_ingredient_list:
            title = recipe_ingredient.ingredient.title
            amount = recipe_ingredient.amount
            dimension = recipe_ingredient.ingredient.dimension
            if title not in purchase_dict:
                purchase_dict[title] = [amount, dimension]
            else:
                purchase_dict[title][0] += amount
            pdf.setFont('Helvetica', 16)
            pdf.drawCentredString(100, 740 - h, f'{num}: {purchase_dict[title]} - {purchase_dict[title][0]} {purchase_dict[title][1]}')
            h += 100
            num += 1
        k = k + 15 * h
    pdf.save()
    return response

    # reportlab.rl_config.TTFSearchPath.append(
    #     str(settings.BASE_DIR) + "/Library/Fonts/"
    # )
    # user = get_object_or_404(User, username=request.user)
    # purchase_dict = {}
    # purchase_list = Purchase.objects.filter(user=user)
    # if purchase_list.count() == 0:
    #     return redirect('purchases')
    # for purchase in purchase_list:
    #     recipe_ingredient_list = RecipeIngredient.objects.filter(recipe__id=purchase.recipe.id)
    #     for recipe_ingredient in recipe_ingredient_list:
    #         title = recipe_ingredient.ingredient.title
    #         amount = recipe_ingredient.amount
    #         dimension = recipe_ingredient.ingredient.dimension
    #         if title not in purchase_dict:
    #             purchase_dict[title] = [amount, dimension]
    #         else:
    #             purchase_dict[title][0] += amount
    # response = HttpResponse(content_type="application/pdf")
    # response["Content-Disposition"] = 'attachment; filename="recipes.pdf"'
    # p = canvas.Canvas(response, pagesize='A4', pageCompression=0)
    # # pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
    # p.setFont("Helvetica", 20)
    # x = 50
    # y = 750
    # for num, el in enumerate(purchase_dict):
    #     if y <= 100:
    #         y = 700
    #         p.showPage()
    #         p.setFont("Helvetica", 20)
    #     p.drawString(
    #         x, y, f"№{num + 1}: {el} - {purchase_dict[el][0]} {purchase_dict[el][1]}"
    #     )
    #     y -= 30
    # p.showPage()
    # p.save()
    # return response


def add_favorites(request):
    user = request.user
    json_data = json.loads(request.body.decode())
    recipe_id = int(json_data['id'])
    recipe = get_object_or_404(Recipe, id=recipe_id)
    favorite = Favorite.objects.filter(user=user, recipe=recipe)
    data = {'success': 'True'}
    if not favorite.exists():
        Favorite.objects.create(user=user, recipe=recipe)
        return JsonResponse(data)
    data['success'] = 'False'       
    return JsonResponse(data)


def favorites_view(request):
    tags = request.GET.getlist('tags')
    favorite_list = Favorite.objects.filter(user=request.user)
    recipe_list = favorite_list.prefetch_related('recipe').filter(recipe__tags__slug__in=tags).distinct()
    paginator = Paginator(recipe_list, PAGINATION_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    count_purchase = Purchase.objects.filter(user=request.user).count()
    return render(
        request,
        'favorites.html',
        {'page': page, 'paginator': paginator, 'tags': tags, 'count_purchase': count_purchase,}
    )


def delete_favorites(request, id):
    user = request.user
    recipe = get_object_or_404(Recipe, id=id)
    favorite = Favorite.objects.filter(user=user, recipe=recipe)
    data = {'success': 'True'} 
    if not favorite.exists():
        data['success'] = 'False'
        return JsonResponse(data)
    favorite.delete()
    return JsonResponse(data)


@login_required()
def add_subscriptions(request):
    user = request.user
    json_data = json.loads(request.body.decode())
    author_id = int(json_data['id'])
    author = get_object_or_404(User, id=author_id)
    follow = Follow.objects.filter(user=user, author=author)
    data = {'success': 'True'}
    if not follow.exists():
        Follow.objects.create(user=user, author=author)
        return JsonResponse(data)
    data['success'] = 'False'       
    return JsonResponse(data)


@login_required()
def subscriptions_view(request):
    user = request.user
    follow_list = user.follower.all()
    paginator = Paginator(follow_list, PAGINATION_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    count_purchase = Purchase.objects.filter(user=request.user).count()
    return render(
        request,
        'follow.html',
        {'page': page, 'paginator': paginator, 'count_purchase': count_purchase,}
    )


@login_required()
def delete_subscriptions(request, id):
    user = request.user
    author = get_object_or_404(User, id=id)
    follow = Follow.objects.filter(user=user, author=author)
    data = {'success': 'True'} 
    if not follow.exists():
        data['success'] = 'False'
        return JsonResponse(data)
    follow.delete()
    return JsonResponse(data)


#@cache_page(20, key_prefix='index_page')
def index(request):
    tags = request.GET.getlist('tags')
    recipe_list = Recipe.objects.prefetch_related('tags').filter(tags__slug__in=tags).distinct()
    paginator = Paginator(recipe_list, PAGINATION_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if not request.user.is_authenticated:
        context = {'page': page, 'paginator': paginator, 'tags': tags,} 
    else:
        count_purchase = Purchase.objects.filter(user=request.user).count()
        context = {'page': page, 'paginator': paginator, 'count_purchase': count_purchase, 'tags': tags,}
    return render(request, 'index.html', context)


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


@login_required()
def new_recipe(request):
    """Функция создания нового рецепта."""
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    count_purchase = Purchase.objects.filter(user=request.user).count()
    if not form.is_valid():
        return render(request, 'new_recipe.html', {'form': form, 'count_purchase': count_purchase,})   
    recipe = save_recipe(request, form)
    return redirect('index')


def recipe_view(request, recipe_slug):
    recipe = get_object_or_404(Recipe, slug=recipe_slug)
    recipe_ingredient_list = RecipeIngredient.objects.filter(recipe__slug=recipe_slug)
    if not request.user.is_authenticated:
        context = dict(recipe=recipe, recipe_ingredient_list=recipe_ingredient_list,)
        return render(request, 'recipe.html', context)
    count_purchase = Purchase.objects.filter(user=request.user).count()
    favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
    star = False
    if favorite.exists():
        star = True
    context = dict(
        recipe=recipe, 
        recipe_ingredient_list=recipe_ingredient_list, 
        count_purchase=count_purchase,
        star=star,
        )
    return render(request, 'recipe.html', context)


@login_required()
def edit_recipe(request, form, instance):
    with transaction.atomic():
        RecipeIngredient.objects.filter(recipe__slug=instance.slug).delete()
        return save_recipe(request, form)


def recipe_delete(request, recipe_slug):
    recipe = get_object_or_404(Recipe, slug=recipe_slug)
    if not request.user.is_superuser:
        if request.user != recipe.author:
            return redirect('recipe', recipe_slug=recipe_slug)
    recipe.delete()
    return redirect('index')


@login_required()
def recipe_edit(request, recipe_slug):
    """Функция редактирования созданного рецепта."""
    flag = True
    recipe = get_object_or_404(Recipe, slug=recipe_slug)
    if not request.user.is_superuser:
        if request.user != recipe.author:
            return redirect('recipe', recipe_slug=recipe_slug)
    form = RecipeForm(request.POST or None, files=request.FILES or None, instance=recipe)
    recipe_ingredient_list = RecipeIngredient.objects.filter(recipe__slug=recipe_slug)
    count_purchase = Purchase.objects.filter(user=request.user).count()
    context = dict(
        form=form,
        flag=flag,
        recipe=recipe, 
        recipe_ingredient_list=recipe_ingredient_list,
        count_purchase=count_purchase,
        )
    if not form.is_valid():
        return render(request, 'new_recipe.html', context)
    edit_recipe(request, form, instance=recipe)
    return redirect('recipe', recipe_slug)

    
def profile(request, username):
    tags = request.GET.getlist('tags')
    author = get_object_or_404(User, username=username)
    author_recipes = author.recipes_user.all()
    recipe_list = author_recipes.prefetch_related('tags').filter(tags__slug__in=tags).distinct()
    paginator = Paginator(recipe_list, PAGINATION_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if not request.user.is_authenticated:
        context = {'author': author, 'page': page, 'paginator': paginator, 'tags': tags,}
        return render(request, 'profile.html', context)
    count_purchase = Purchase.objects.filter(user=request.user).count()
    context = {'author': author, 'page': page, 'paginator': paginator, 'tags': tags, 'count_purchase': count_purchase}
    return render(request, 'profile.html', context)
