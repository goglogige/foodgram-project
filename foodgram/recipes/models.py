from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


User = get_user_model()


class Ingredient(models.Model):
    title = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='title',
    )
    dimension = models.CharField(
        max_length=20,
        verbose_name='dimension',
    )

    class Meta:
        ordering = ['title']
        verbose_name = 'ingredient'
        verbose_name_plural = 'ingredients'

    def __str__(self):
        return f'{self.title}-{self.dimension}'


class Tag(models.Model):
    title = models.CharField(
        verbose_name='tag name',
        max_length=50,
        db_index=True,
    )
    color = models.CharField(
        verbose_name='tag color',
        max_length=50,
    )
    slug = models.SlugField(
        max_length=50, 
        verbose_name="slug",
        unique="True",
    )

    def __str__(self):
        return self.title


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes_user',
        verbose_name='author'
    )
    recipe_name = models.CharField(
        max_length=200,
        verbose_name='recipe name',
    )
    pub_date = models.DateTimeField(
        verbose_name='date published',
        auto_now_add=True,
        db_index=True,
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=True,
        null=True,
        verbose_name='image',
    )
    recipe_description = models.TextField(
        verbose_name='recipe description',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='ingredients'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='tag',
        related_name='recipe_tags',
    )
    time = models.PositiveSmallIntegerField(
        verbose_name='cooking time',
    )
    slug = models.SlugField(
        max_length=255,
        unique='True',
        db_index=True,
        verbose_name='url',
    )

    def __str__(self):
        return self.recipe_name

    def get_absolute_url(self):
        return reverse('recipe', kwargs={'recipe_slug': self.slug})

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'recipe'
        verbose_name_plural = 'recipes'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ingredient',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='recipe',
        related_name='ingredients_amounts',
    )
    amount = models.DecimalField(
        max_digits=6,
        decimal_places=0,
        verbose_name='amount',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        unique_together = ('ingredient', 'recipe')
        ordering = ['ingredient']
        verbose_name = 'recipe ingredient'
        verbose_name_plural = 'recipe ingredients'

    def __str__(self):
        return f'{self.ingredient}-{self.recipe}'

    
class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created = models.DateTimeField('date of creation', auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'purchase'
        verbose_name_plural = 'purchases'
        
    def __str__(self):
        return f'{self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created = models.DateTimeField('date of creation', auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'favorite'
        verbose_name_plural = 'favorites'
        
    def __str__(self):
        return f'{self.recipe}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following"
    )

    def __str__(self):
        return f'follower: {self.user} author: {self.author}'

    class Meta:
        unique_together = ['author', 'user']