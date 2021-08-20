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
    list_display: Tuple[int, str, str, str, object, str, str, int] = (
        "pk",
        "author",
        "recipe_name",
        "get_tags",
        "image",
        "pub_date",
        "slug",
        "get_count_favorite",
    )
    prepopulated_fields = {"slug": ("recipe_name", )}
    search_fields = ["author__username", "recipe_name", "tags__slug",]
    list_filter = ("author",)
    empty_value_display = "-пусто-"

    def get_tags(self, obj):
        return ", ".join([item.slug for item in obj.tags.all()])

    def get_count_favorite(self, obj):
        favorite_list = Favorite.objects.filter(recipe__recipe_name=obj.recipe_name)
        count = favorite_list.count()
        return count


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
    list_display: Tuple[int, str, str, str] = (
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
