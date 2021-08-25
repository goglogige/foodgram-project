from django.urls import include, path

from . import views


subscriptions_url = [
    path('', views.add_subscriptions, name='subscriptions'),
    path('view/', views.subscriptions_view, name='subscriptions_view'),
    path('<int:id>/', views.delete_subscriptions, name='delete_subscriptions'),
]

favorites_url = [
    path('', views.add_favorites, name='favorites'),
    path('view/', views.favorites_view, name='favorites_view'),
    path('<int:id>/', views.delete_favorites, name='delete_favorites'),
]

purchases_url = [
    path('', views.add_purchases, name='purchases'),
    path('view/', views.purchases_view, name='purchases_view'),
    path('download/', views.purchases_download, name='purchases_download'),
    path('<int:id>/', views.button_delete_purchases, name='button_delete_purchases'),
    path('delete/<int:purchase_id>/', views.delete_purchases, name='delete_purchases'),
]

urlpatterns = [
    path('', views.index, name='index'),
    path('purchases/', include(purchases_url)),
    path('favorites/', include(favorites_url)),
    path('subscriptions/', include(subscriptions_url)),
    path('ingredients/', views.ingredients, name='ingredients'),
    path('new-recipe/', views.new_recipe, name='new_recipe'),
    path('authors/<str:username>/', views.profile, name='profile'),
    path('<slug:recipe_slug>/', views.recipe_view, name='recipe'),
    path('<slug:recipe_slug>/edit/', views.recipe_edit, name='recipe_edit'),
    path('<slug:recipe_slug>/delete/', views.recipe_delete, name='recipe_delete'),
]
