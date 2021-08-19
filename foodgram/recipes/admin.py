from typing import Tuple

from django.contrib import admin

from .models import (
    Ingredient, Recipe, RecipeIngredient, Tag, Purchase, Favorite, Follow, 
)


class IngredientAdmin(admin.ModelAdmin):
    list_display: Tuple[int, str, str] = (
        "pk",
        "title",
        "dimension",
    )
    search_fields = ("title",)
    empty_value_display = "-пусто-"


class TagAdmin(admin.ModelAdmin):
    list_display: Tuple[int, str, str, str] = (
        "pk",
        "title",
        "color",
        "slug",
    )
    search_fields = ("title",)
    empty_value_display = "-пусто-"    


class RecipeAdmin(admin.ModelAdmin):
    list_display: Tuple[int, str, str, object, str, str] = (
        "pk",
        "author",
        "recipe_name",
        "image",
        "pub_date",
        "slug",
    )
    prepopulated_fields = {"slug": ("recipe_name", )}
    search_fields = ("recipe_name",)
    list_filter = ("author",)
    empty_value_display = "-пусто-"


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display: Tuple[int, str, str, float] = (
        "pk",
        "ingredient",
        "recipe",
        "amount",
    )
    search_fields = ("ingredient_name",)
    empty_value_display = "-пусто-"


class PurchaseAdmin(admin.ModelAdmin):
    list_display: Tuple[int, str, str, float] = (
        "pk",
        "user",
        "recipe",
        "created",
    )
    search_fields = ("user",)
    empty_value_display = "-пусто-"


class FavoriteAdmin(admin.ModelAdmin):
    list_display: Tuple[int, str, str,str] = (
        "pk",
        "user",
        "recipe",
        "created",
    )
    search_fields = ("user",)
    empty_value_display = "-пусто-"
    

class FollowAdmin(admin.ModelAdmin):
    list_display: Tuple[int, str, str] = (
        "pk",
        "user",
        "author",
    )
    search_fields = ("author",)
    empty_value_display = "-пусто-"


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Follow, FollowAdmin)
