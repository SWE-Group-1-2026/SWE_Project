from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-dashboard/recipes/new/", views.admin_add_recipe, name="admin_add_recipe"),
    path("admin-dashboard/recipes/<str:id>/edit/", views.admin_edit_recipe, name="admin_edit_recipe"),
    path("verify-email/", views.verify_email_notice, name="verify_email_notice"),
    path(
        "verify-email/<uidb64>/<token>/",
        views.verify_email_confirm,
        name="verify_email_confirm",
    ),
    path("logout/", views.logout_view, name="logout"),
    path("pet/", views.pet_customizer, name="pet_customizer"),
    path("profile/", views.profile_view, name="profile"),
    path("how-it-works/", views.tutorial_view, name="tutorial"),
    path("recipes/", views.search_recipes, name="search"),
    path("recipe/<str:id>/", views.recipe_detail, name="recipe_detail"),
    path("recipe/<str:id>/save/", views.toggle_saved_recipe, name="toggle_saved_recipe"),
    path("recipe/<str:id>/start/", views.recipe_steps, name="recipe_steps"),
]
