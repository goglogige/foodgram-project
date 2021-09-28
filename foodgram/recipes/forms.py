from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Recipe, Tag, RecipeIngredient


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['recipe_name', 'time', 'recipe_description', 'image', 'tags']
        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
            'recipe_description': forms.Textarea(attrs={'rows': 8}),
        }
        choices = Tag.objects.all()

        labels = {
            'recipe_name': _('Название рецепта'),
            'tags': _('Тэги'),
            'time': _('Время приготовления'),
            'recipe_description': _('Описание'),
            'image': _('Загрузить фото'),
        }
        help_texts = {
            'recipe_name': _('Напишите название рецепта'),
            'tag': _('Выберите теги'),
            'time': _('Укажите время приготовления'),
            'recipe_description': _('Задайте описание рецепта'),
            'image': _('Выбрать файл'),
        }


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['amount', ]
        widgets = {
            'amount': forms.NumberInput(attrs={'step': 1, 'max': 1000, 'min': 0}),
        }
