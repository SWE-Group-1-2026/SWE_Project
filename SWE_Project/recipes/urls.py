from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("pet/", views.pet_customizer, name="pet_customizer"),
    path("profile/", views.profile_view, name="profile"),
    path("how-it-works/", views.tutorial_view, name="tutorial"),
    path("recipes/", views.search_recipes, name="search"),
    path("recipe/<str:id>/", views.recipe_detail, name="recipe_detail"),
]
