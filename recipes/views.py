import json

from urllib.parse import unquote

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls.base import reverse

from foodgram.settings import PAGINATION_SIZE
from .forms import RecipeForm
from .models import (
    User, Ingredient, Recipe, RecipeIngredient,
    Purchase, Favorite, Follow, Tag
)
from .utils import pdf_download, save_recipe, ObjectsProcessor


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
    query = unquote(request.GET.get('query'))
    data = list(Ingredient.objects.filter(
        title__startswith=query
    ).values(
        'title', 'dimension'))
    return JsonResponse(data, safe=False)


@login_required()
def add_purchases(request):
    return ObjectsProcessor(Purchase, request).add_obj()


@login_required()
def button_delete_purchases(request, id):
    return ObjectsProcessor(Purchase, request).delete_obj(id=id)


@login_required()
def delete_purchases(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    purchase.delete()
    purchase_list = Purchase.objects.filter(user=request.user)
    return render(
        request,
        'purchases.html',
        {'purchase_list': purchase_list, }
    )


@login_required()
def purchases_view(request):
    purchase_list = Purchase.objects.filter(user=request.user)
    count_purchase = purchase_list.count()
    return render(
        request,
        'purchases.html',
        {'purchase_list': purchase_list, 'count_purchase': count_purchase}
    )


@login_required
def purchases_download(request):
    return pdf_download(request)


@login_required()
def add_favorites(request):
    return ObjectsProcessor(Favorite, request).add_obj()


@login_required()
def delete_favorites(request, id):
    return ObjectsProcessor(Favorite, request).delete_obj(id=id)


@login_required()
def favorites_view(request):
    page = request.GET.getlist('page')
    path_with_page = f'{reverse("favorites_view")}?page={page}/'
    path_without_page = reverse("favorites_view")
    if request.get_full_path() == path_without_page or path_with_page:
        tag_list = Tag.objects.all()
        tags = [i.slug for i in tag_list]
    else:
        tags = request.GET.getlist('tags')
    favorite_list = Favorite.objects.filter(user=request.user)
    recipe_list = favorite_list.prefetch_related('recipe').filter(
        recipe__tags__slug__in=tags
    ).distinct()
    paginator = Paginator(recipe_list, PAGINATION_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    count_purchase = Purchase.objects.filter(user=request.user).count()
    purchase_and_favorite_recipe_id_list = list(Purchase.objects.filter(
        recipe__recipe_name__in=list(recipe_list)
    ).values('recipe_id'))
    recipe_id_list = [
        i['recipe_id'] for i in purchase_and_favorite_recipe_id_list
        ]
    purchase_and_favorite_recipe_list = list(Recipe.objects.filter(
        id__in=recipe_id_list
    ).values('recipe_name'))
    recipe_name_list = [
        i['recipe_name'] for i in purchase_and_favorite_recipe_list
        ]
    context = {
        'page': page, 'paginator': paginator,
        'tags': tags, 'count_purchase': count_purchase,
        'page_number': page_number,
        'recipe_name_list': recipe_name_list,
    }
    return render(request, 'favorites.html', context)


@login_required()
def add_subscriptions(request):
    user = request.user
    json_data = json.loads(request.body.decode())
    author_id = int(json_data['id'])
    author = get_object_or_404(User, id=author_id)
    Follow.objects.get_or_create(user=user, author=author)
    data = {'success': 'True'}
    return JsonResponse(data)


@login_required()
def subscriptions_view(request):
    user = request.user
    follow_list = user.follower.all()
    paginator = Paginator(follow_list, PAGINATION_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    count_purchase = Purchase.objects.filter(user=request.user).count()
    context = {
        'page': page, 'paginator': paginator,
        'count_purchase': count_purchase,
    }
    return render(request, 'follow.html', context)


@login_required()
def delete_subscriptions(request, id):
    user = request.user
    author = get_object_or_404(User, id=id)
    follow = user.follower.filter(author=author)
    data = {'success': 'True'}
    if follow.delete() == 0:
        data['success'] = 'False'
        return JsonResponse(data)
    return JsonResponse(data)


def index(request):
    page = request.GET.getlist('page')
    path_with_page = f'{reverse("index")}?page={page}/'
    path_without_page = reverse("index")
    if request.get_full_path() == path_without_page or path_with_page:
        tag_list = Tag.objects.all()
        tags = [i.slug for i in tag_list]
    else:
        tags = request.GET.getlist('tags')
    recipe_list = Recipe.objects.prefetch_related('tags').filter(
        tags__slug__in=tags
    ).distinct()
    paginator = Paginator(recipe_list, PAGINATION_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if not request.user.is_authenticated:
        context = {
            'page': page, 'paginator': paginator,
            'tags': tags, 'page_number': page_number,
        }
        return render(request, 'index.html', context)
    count_purchase = Purchase.objects.filter(user=request.user).count()
    section_favorite_list = Favorite.objects.filter(
        user=request.user,
        recipe__in=recipe_list,
    )
    favorite_recipes = [i.recipe.recipe_name for i in section_favorite_list]
    section_purchase_list = Purchase.objects.filter(
        user=request.user,
        recipe__in=recipe_list,
    )
    purchase_recipes = [i.recipe.recipe_name for i in section_purchase_list]
    context = {
        'page': page, 'paginator': paginator,
        'count_purchase': count_purchase, 'tags': tags,
        'page_number': page_number,
        'purchase_recipes': purchase_recipes,
        'favorite_recipes': favorite_recipes,
    }
    return render(request, 'index.html', context)


@login_required()
def new_recipe(request):
    """Функция создания нового рецепта."""
    form = RecipeForm(request.POST or None, files=request.FILES or None)
    count_purchase = Purchase.objects.filter(user=request.user).count()
    context = {'form': form, 'count_purchase': count_purchase, }
    if not form.is_valid():
        return render(request, 'new_recipe.html', context)
    save_recipe(request, form)
    return redirect('index')


def recipe_view(request, recipe_slug):
    recipe = get_object_or_404(Recipe, slug=recipe_slug)
    recipe_ingredient_list = RecipeIngredient.objects.filter(
        recipe__slug=recipe_slug
    )
    if not request.user.is_authenticated:
        context = dict(
            recipe=recipe,
            recipe_ingredient_list=recipe_ingredient_list,
        )
        return render(request, 'recipe.html', context)
    count_purchase = Purchase.objects.filter(user=request.user).count()
    purchase = Purchase.objects.filter(user=request.user, recipe=recipe)
    favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
    follow = Follow.objects.filter(user=request.user, author=recipe.author)
    star = False
    plus = False
    subs = False
    if favorite.exists():
        star = True
    if purchase.exists():
        plus = True
    if follow.exists():
        subs = True
    context = dict(
        recipe=recipe,
        recipe_ingredient_list=recipe_ingredient_list,
        count_purchase=count_purchase,
        star=star,
        plus=plus,
        subs=subs,
    )
    return render(request, 'recipe.html', context)


@login_required()
def edit_recipe(request, form, instance):
    with transaction.atomic():
        RecipeIngredient.objects.filter(recipe__slug=instance.slug).delete()
        return save_recipe(request, form)


@login_required()
def recipe_delete(request, recipe_slug):
    recipe = get_object_or_404(Recipe, slug=recipe_slug)
    if not request.user.is_superuser:
        if request.user != recipe.author:
            return redirect('recipe', recipe_slug=recipe_slug)
    recipe.delete()
    return redirect('index')


@login_required()
def recipe_edit(request, recipe_slug):
    flag = True
    recipe = get_object_or_404(Recipe, slug=recipe_slug)
    if not request.user.is_superuser:
        if request.user != recipe.author:
            return redirect('recipe', recipe_slug=recipe_slug)
    form = RecipeForm(
        request.POST or None,
        files=request.FILES or None,
        instance=recipe,
    )
    recipe_ingredient_list = RecipeIngredient.objects.filter(
        recipe__slug=recipe_slug
    )
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
    page = request.GET.getlist('page')
    pwp = f'{reverse("profile", kwargs={"username": username})}?page={page}/'
    path_without_page = reverse(
        "profile",
        kwargs={"username": username}
    )
    if request.get_full_path() == path_without_page or pwp:
        tag_list = Tag.objects.all()
        tags = [i.slug for i in tag_list]
    else:
        tags = request.GET.getlist('tags')
    author = get_object_or_404(User, username=username)
    author_recipes = author.recipes_user.all()
    recipe_list = author_recipes.prefetch_related('tags').filter(
        tags__slug__in=tags
    ).distinct()
    paginator = Paginator(recipe_list, PAGINATION_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if not request.user.is_authenticated:
        context = {
            'author': author, 'page': page,
            'paginator': paginator, 'tags': tags,
            'page_number': page_number,
        }
        return render(request, 'profile.html', context)
    count_purchase = Purchase.objects.filter(user=request.user).count()
    follow = Follow.objects.filter(
        user=request.user, author__username=username
    )
    subs = False
    if follow.exists():
        subs = True
    section_favorite_list = Favorite.objects.filter(
        user=request.user,
        recipe__in=recipe_list,
    )
    favorite_recipes = [i.recipe.recipe_name for i in section_favorite_list]
    section_purchase_list = Purchase.objects.filter(
        user=request.user,
        recipe__in=recipe_list,
    )
    purchase_recipes = [i.recipe.recipe_name for i in section_purchase_list]
    context = {
        'author': author, 'page': page,
        'paginator': paginator, 'tags': tags,
        'count_purchase': count_purchase,
        'page_number': page_number, 'subs': subs,
        'favorite_recipes': favorite_recipes,
        'purchase_recipes': purchase_recipes,
    }
    return render(request, 'profile.html', context)
