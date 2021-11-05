from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class PositiveIntegerWithoutZeroField(models.PositiveSmallIntegerField):
    description = _("Positive integer without zero")

    def __str__(self):
        return "PositiveIntegerWithoutZeroField"

    def formfield(self, **kwargs):
        return super().formfield(**{
            'min_value': 1,
            **kwargs,
        })


class PositiveDecimalWithoutZeroField(models.DecimalField):
    description = _("Positive decimal without zero")

    def __str__(self):
        return "PositiveDecimalWithoutZeroField"

    def formfield(self, **kwargs):
        return super().formfield(**{
            'min_value': 1,
            **kwargs,
        })


User = get_user_model()


class Ingredient(models.Model):
    title = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='название ингредиента',
    )
    dimension = models.CharField(
        max_length=20,
        verbose_name='единица измерения',
    )

    class Meta:
        ordering = ['title']
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return f'{self.title}-{self.dimension}'


class Tag(models.Model):
    title = models.CharField(
        verbose_name='название тега',
        max_length=50,
        db_index=True,
    )
    color = models.CharField(
        verbose_name='цвет тега',
        max_length=50,
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name="слаг ингредиента",
        unique="True",
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.title


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes_user',
        verbose_name='автор'
    )
    recipe_name = models.CharField(
        max_length=200,
        unique='True',
        error_messages={'unique':"Рецепт с таким именем уже существует. "
            "Используйте пожалуйста другое имя рецепта."},
        verbose_name='название рецепта',
    )
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True,
        db_index=True,
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=False,
        verbose_name='изображение',
    )
    recipe_description = models.TextField(
        verbose_name='описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='тег',
        related_name='recipe_tags',
    )
    time = PositiveIntegerWithoutZeroField(
        verbose_name='время приготовления',
        validators=[MinValueValidator(
            limit_value=1,
            message='Не менее 1 минуты'
        )],
    )
    slug = models.SlugField(
        max_length=255,
        unique='True',
        db_index=True,
        verbose_name='URL рецепта',
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.recipe_name

    def get_absolute_url(self):
        return reverse('recipe', kwargs={'recipe_slug': self.slug})


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
        related_name='ingredients_amounts',
    )
    amount = PositiveDecimalWithoutZeroField(
        max_digits=7,
        decimal_places=1,
        verbose_name='количество',
        validators=[MinValueValidator(
            limit_value=1,
            message='Введите не менее 1 единицы ингредиента!',
        )],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_recipe',
            )
        ]
        ordering = ['ingredient']
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'ингредиенты в рецепте'

    def __str__(self):
        return f'{self.ingredient}-{self.recipe}'


class Purchase(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь',
        related_name='purchases',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
    )
    created = models.DateTimeField('date of creation', auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'покупка'
        verbose_name_plural = 'покупки'

    def __str__(self):
        return f'{self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
    )
    created = models.DateTimeField('date of creation', auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite',
            )
        ]
        ordering = ['-created']
        verbose_name = 'избранный'
        verbose_name_plural = 'избранные'

    def __str__(self):
        return f'{self.recipe}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name='подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name='автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_follow',
            )
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'

    def __str__(self):
        return f'follower: {self.user} author: {self.author}'
