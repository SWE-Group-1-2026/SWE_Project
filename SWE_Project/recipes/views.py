import logging
import os
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils import timezone

from .gmail_api import send_gmail_api_message
from .models import PetProfile, SavedRecipe


logger = logging.getLogger(__name__)

MONGO_URI = (
    os.getenv("MONGO_URI")
    or "mongodb+srv://eeshakondlapudi_db_user:Eesha1234@cluster1.sveryx9.mongodb.net/"
    "?appName=Cluster1"
)
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "SousPaw")
MONGO_RECIPE_COLLECTION = os.getenv("MONGO_RECIPE_COLLECTION", "Recipes")
MONGO_USER_COLLECTION = os.getenv("MONGO_USER_COLLECTION", "userLogin")


def _is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _require_admin(request):
    if _is_admin(request.user):
        return None
    return HttpResponseForbidden("You do not have permission to access this page.")


def _get_post_login_redirect(user):
    if _is_admin(user):
        return "admin_dashboard"
    return "pet_customizer"


def _parse_multiline_list(raw_value):
    return [item.strip() for item in raw_value.splitlines() if item.strip()]


def _build_recipe_form_context(recipe=None, error_message=None, success_message=None):
    recipe = recipe or {}
    return {
        "error_message": error_message,
        "success_message": success_message,
        "form_values": {
            "recipe_name": recipe.get("recipe_name", ""),
            "cuisine": recipe.get("cuisine", ""),
            "duration": recipe.get("duration", ""),
            "ingredients": "\n".join(recipe.get("ingredients", [])),
            "recipe_steps": "\n".join(recipe.get("recipe_steps", [])),
        },
    }


def _get_recipe_collection_and_object_id(id):
    collection, error_message = _get_recipe_collection()
    if collection is None:
        return None, None, error_message

    try:
        from bson.objectid import ObjectId
    except ImportError:
        return None, None, "Recipe editing is unavailable until MongoDB dependencies are installed."

    try:
        return collection, ObjectId(id), None
    except Exception:
        return None, None, "The recipe ID is invalid."


def _get_mongo_client():
    try:
        import certifi
        from pymongo import MongoClient
        from pymongo.errors import PyMongoError
    except ImportError:
        return None, "Recipe search is unavailable until the MongoDB dependencies are installed."

    try:
        client = MongoClient(
            MONGO_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=2000,
            connectTimeoutMS=2000,
            socketTimeoutMS=2000,
        )
        client.admin.command("ping")
        return client, None
    except PyMongoError as exc:
        logger.warning("MongoDB connection failed: %s", exc)
        return (
            None,
            "Recipe search is temporarily unavailable because MongoDB could not be reached.",
        )
    except Exception as exc:
        logger.exception("Unexpected MongoDB connection failure: %s", exc)
        return (
            None,
            "Recipe search is temporarily unavailable because MongoDB could not be reached.",
        )


def _get_recipe_collection():
    client, error_message = _get_mongo_client()
    if client is None:
        return None, error_message
    return client[MONGO_DB_NAME][MONGO_RECIPE_COLLECTION], None


def _get_mongo_database():
    client, error_message = _get_mongo_client()
    if client is None:
        return None, error_message or "MongoDB could not be reached."
    return client[MONGO_DB_NAME], None


def _sync_user_login_document(user, event_type):
    db, _ = _get_mongo_database()
    if db is None:
        return

    user_login_collection = db[MONGO_USER_COLLECTION]
    now = timezone.now().isoformat()
    update_fields = {
        "email": user.email,
        "django_user_id": user.id,
        "username": user.username,
        "last_event": event_type,
        "last_login_at": now if event_type == "login" else None,
        "updated_at": now,
    }

    if event_type == "signup":
        update_fields["signup_at"] = now
        update_fields["last_login_at"] = None

    try:
        user_login_collection.update_one(
            {"django_user_id": user.id},
            {
                "$set": update_fields,
                "$setOnInsert": {
                    "created_at": now,
                },
            },
            upsert=True,
        )
    except Exception as exc:
        logger.warning("Failed to sync user login document to MongoDB: %s", exc)


def _verification_notice_redirect(email):
    return redirect(f"{reverse('verify_email_notice')}?{urlencode({'email': email})}")


def _send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verification_link = request.build_absolute_uri(
        reverse("verify_email_confirm", args=[uid, token])
    )

    subject = "Verify your SousPaw account"
    message = (
        f"Hi {user.email},\n\n"
        "Thanks for signing up for SousPaw.\n"
        "Please verify your email address by clicking the link below:\n\n"
        f"{verification_link}\n\n"
        "If you did not create this account, you can ignore this email."
    )

    if settings.EMAIL_PROVIDER == "gmail_api":
        send_gmail_api_message(
            to_email=user.email,
            subject=subject,
            body=message,
        )
        return

    if settings.EMAIL_PROVIDER != "django":
        raise ImproperlyConfigured(
            "EMAIL_PROVIDER must be either 'django' or 'gmail_api'."
        )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def home(request):
    return render(request, "home.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect(_get_post_login_redirect(request.user))

    context = {"error_message": None, "submitted_email": ""}

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        context["submitted_email"] = email

        if not email or not password:
            context["error_message"] = "Please enter your email and password."
        else:
            existing_user = User.objects.filter(username=email).first()
            if (
                existing_user is not None
                and not existing_user.is_active
                and existing_user.check_password(password)
            ):
                return _verification_notice_redirect(email)

            user = authenticate(request, username=email, password=password)
            if user is None:
                context["error_message"] = "Incorrect email or password. Please try again."
            else:
                login(request, user)
                _sync_user_login_document(user, "login")
                return redirect(_get_post_login_redirect(user))

    return render(request, "login.html", context)


def signup_view(request):
    if request.user.is_authenticated:
        return redirect(_get_post_login_redirect(request.user))

    context = {
        "error_message": None,
        "success_message": None,
        "submitted_email": "",
    }

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        context["submitted_email"] = email

        if not email:
            context["error_message"] = "Please enter a valid email address."
        elif len(password) < 8:
            context["error_message"] = "Password must be at least 8 characters long."
        elif password != confirm_password:
            context["error_message"] = "Passwords do not match."
        elif User.objects.filter(username=email).exists():
            context["error_message"] = "That email is already registered."
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                is_active=False,
            )
            try:
                _sync_user_login_document(user, "signup")
                _send_verification_email(request, user)
            except Exception:
                user.delete()
                context["error_message"] = (
                    "We couldn't send the verification email right now. "
                    "Please check your email settings and try again."
                )
            else:
                return _verification_notice_redirect(email)

    return render(request, "signup.html", context)


def verify_email_notice(request):
    return render(
        request,
        "verify_email.html",
        {
            "submitted_email": request.GET.get("email", "").strip(),
        },
    )


def verify_email_confirm(request, uidb64, token):
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        return render(request, "verify_email_result.html", {"verification_success": False})

    if not user.is_active:
        user.is_active = True
        user.save(update_fields=["is_active"])

    return render(
        request,
        "verify_email_result.html",
        {
            "verification_success": True,
            "login_url": reverse("login"),
        },
    )


@login_required
def pet_customizer(request):
    pet_profile, _ = PetProfile.objects.get_or_create(user=request.user)
    error_message = None
    success_message = None

    if request.method == "POST":
        name = request.POST.get("name", "").strip() or "Lucky"
        species = request.POST.get("species", "")
        gender = request.POST.get("gender", "")

        if len(name) > 50:
            error_message = "Pet name must be 50 characters or fewer."
        elif species not in dict(PetProfile.SPECIES_CHOICES):
            error_message = "Please choose a valid species."
        elif gender not in dict(PetProfile.GENDER_CHOICES):
            error_message = "Please choose a valid gender."
        else:
            pet_profile.name = name
            pet_profile.species = species
            pet_profile.gender = gender
            pet_profile.save()
            success_message = "Pet customization saved."

    return render(
        request,
        "main.html",
        {
            "pet_profile": pet_profile,
            "species_choices": PetProfile.SPECIES_CHOICES,
            "gender_choices": PetProfile.GENDER_CHOICES,
            "error_message": error_message,
            "success_message": success_message,
        },
    )


@login_required
def profile_view(request):
    return render(
        request,
        "profile.html",
        {
            "saved_recipes": request.user.saved_recipes.all(),
            "is_admin": _is_admin(request.user),
        },
    )


@login_required
def admin_dashboard(request):
    denied_response = _require_admin(request)
    if denied_response is not None:
        return denied_response

    users = (
        User.objects.order_by("email", "username")
        .annotate(saved_recipe_count=Count("saved_recipes"))
    )

    return render(
        request,
        "admin_dashboard.html",
        {
            "total_users": users.count(),
            "total_admins": sum(1 for user in users if _is_admin(user)),
            "total_saved_recipes": SavedRecipe.objects.count(),
            "users": users,
        },
    )


@login_required
def admin_add_recipe(request):
    denied_response = _require_admin(request)
    if denied_response is not None:
        return denied_response

    context = _build_recipe_form_context()

    if request.method == "POST":
        recipe_name = request.POST.get("recipe_name", "").strip()
        cuisine = request.POST.get("cuisine", "").strip()
        duration = request.POST.get("duration", "").strip()
        ingredients_raw = request.POST.get("ingredients", "").strip()
        recipe_steps_raw = request.POST.get("recipe_steps", "").strip()

        context["form_values"] = {
            "recipe_name": recipe_name,
            "cuisine": cuisine,
            "duration": duration,
            "ingredients": ingredients_raw,
            "recipe_steps": recipe_steps_raw,
        }

        ingredients = _parse_multiline_list(ingredients_raw)
        recipe_steps = _parse_multiline_list(recipe_steps_raw)

        if not recipe_name:
            context["error_message"] = "Recipe name is required."
        elif not cuisine:
            context["error_message"] = "Cuisine is required."
        elif not duration:
            context["error_message"] = "Duration is required."
        elif not ingredients:
            context["error_message"] = "Add at least one ingredient."
        elif not recipe_steps:
            context["error_message"] = "Add at least one recipe step."
        else:
            db, error_message = _get_mongo_database()
            if db is None:
                context["error_message"] = error_message or "MongoDB could not be reached."
            else:
                recipe_collection = db[MONGO_RECIPE_COLLECTION]
                recipe_document = {
                    "recipe_name": recipe_name,
                    "cuisine": cuisine,
                    "duration": duration,
                    "ingredients": ingredients,
                    "recipe_steps": recipe_steps,
                    "created_by": request.user.email or request.user.username,
                    "created_at": timezone.now().isoformat(),
                }
                try:
                    result = recipe_collection.insert_one(recipe_document)
                except Exception:
                    context["error_message"] = (
                        "The recipe could not be saved right now. Please try again."
                    )
                else:
                    return redirect("recipe_detail", id=str(result.inserted_id))

    return render(request, "admin_recipe_form.html", context)


@login_required
def admin_edit_recipe(request, id):
    denied_response = _require_admin(request)
    if denied_response is not None:
        return denied_response

    collection, object_id, error_message = _get_recipe_collection_and_object_id(id)
    if collection is None:
        return render(
            request,
            "admin_recipe_form.html",
            _build_recipe_form_context(error_message=error_message),
        )

    recipe = collection.find_one({"_id": object_id})
    if not recipe:
        return render(
            request,
            "admin_recipe_form.html",
            _build_recipe_form_context(error_message="Recipe not found."),
        )

    context = _build_recipe_form_context(recipe)

    if request.method == "POST":
        recipe_name = request.POST.get("recipe_name", "").strip()
        cuisine = request.POST.get("cuisine", "").strip()
        duration = request.POST.get("duration", "").strip()
        ingredients_raw = request.POST.get("ingredients", "").strip()
        recipe_steps_raw = request.POST.get("recipe_steps", "").strip()

        context = {
            "recipe_id": id,
            "is_edit_mode": True,
            **_build_recipe_form_context(
                {
                    "recipe_name": recipe_name,
                    "cuisine": cuisine,
                    "duration": duration,
                    "ingredients": _parse_multiline_list(ingredients_raw),
                    "recipe_steps": _parse_multiline_list(recipe_steps_raw),
                }
            ),
        }

        ingredients = _parse_multiline_list(ingredients_raw)
        recipe_steps = _parse_multiline_list(recipe_steps_raw)

        if not recipe_name:
            context["error_message"] = "Recipe name is required."
        elif not cuisine:
            context["error_message"] = "Cuisine is required."
        elif not duration:
            context["error_message"] = "Duration is required."
        elif not ingredients:
            context["error_message"] = "Add at least one ingredient."
        elif not recipe_steps:
            context["error_message"] = "Add at least one recipe step."
        else:
            try:
                collection.update_one(
                    {"_id": object_id},
                    {
                        "$set": {
                            "recipe_name": recipe_name,
                            "cuisine": cuisine,
                            "duration": duration,
                            "ingredients": ingredients,
                            "recipe_steps": recipe_steps,
                            "updated_by": request.user.email or request.user.username,
                            "updated_at": timezone.now().isoformat(),
                        }
                    },
                )
            except Exception:
                context["error_message"] = (
                    "The recipe could not be updated right now. Please try again."
                )
            else:
                return redirect("recipe_detail", id=id)

        return render(request, "admin_recipe_form.html", context)

    return render(
        request,
        "admin_recipe_form.html",
        {
            "recipe_id": id,
            "is_edit_mode": True,
            **context,
        },
    )


def tutorial_view(request):
    return render(request, "tutorialsforhowitworks.html")


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")
    return redirect("home")


def search_recipes(request):
    query = request.GET.get("search", "").strip()
    results = []
    collection, error_message = _get_recipe_collection()

    if collection is None:
        pass
    else:
        try:
            if query:
                recipes = collection.find(
                    {
                        "$or": [
                            {"recipe_name": {"$regex": query, "$options": "i"}},
                            {"cuisine": {"$regex": query, "$options": "i"}},
                        ]
                    }
                )
            else:
                recipes = collection.find()

            for recipe in recipes:
                results.append(
                    {
                        "id": str(recipe["_id"]),
                        "name": recipe.get("recipe_name", ""),
                        "cuisine": recipe.get("cuisine", ""),
                        "time": recipe.get("duration", ""),
                    }
                )
        except Exception:
            error_message = (
                "Recipe search is temporarily unavailable because the MongoDB service could not be reached."
            )
            results = []

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {
                "recipes": results,
                "query": query,
                "error_message": error_message,
            }
        )

    return render(
        request,
        "search.html",
        {
            "recipes": results,
            "query": query,
            "error_message": error_message,
        },
    )


def _get_recipe_detail_context(id):
    collection, error_message = _get_recipe_collection()
    if collection is None:
        return {"error": error_message}

    try:
        from bson.objectid import ObjectId
    except ImportError:
        return {"error": "Recipe details are unavailable until MongoDB dependencies are installed."}

    try:
        recipe = collection.find_one({"_id": ObjectId(id)})

        if not recipe:
            return {"error": "Recipe not found"}

        recipe_id = str(recipe["_id"])
        recipe["_id"] = recipe_id
        recipe["id"] = recipe_id
        return {"recipe": recipe}
    except Exception:
        return {"error": "Recipe details are temporarily unavailable or the recipe ID is invalid."}


def recipe_detail(request, id):
    context = _get_recipe_detail_context(id)
    recipe = context.get("recipe")
    if request.user.is_authenticated and recipe:
        context["is_saved"] = SavedRecipe.objects.filter(
            user=request.user,
            recipe_id=recipe["id"],
        ).exists()
    return render(request, "recipe.html", context)


def recipe_steps(request, id):
    context = _get_recipe_detail_context(id)
    if request.user.is_authenticated:
        context["pet_profile"] = PetProfile.objects.filter(user=request.user).first()
    return render(request, "recipe_steps.html", context)


def tutorial(request):
    return render(request, "tutorial.html")

@login_required
def toggle_saved_recipe(request, id):
    if request.method != "POST":
        return redirect("recipe_detail", id=id)

    next_url = request.POST.get("next") or reverse("recipe_detail", args=[id])
    saved_recipe = SavedRecipe.objects.filter(user=request.user, recipe_id=id).first()

    if saved_recipe:
        saved_recipe.delete()
        return redirect(next_url)

    context = _get_recipe_detail_context(id)
    recipe = context.get("recipe")
    if not recipe:
        return redirect("recipe_detail", id=id)

    SavedRecipe.objects.create(
        user=request.user,
        recipe_id=recipe["id"],
        recipe_name=recipe.get("recipe_name", "Untitled Recipe"),
        cuisine=recipe.get("cuisine", ""),
        duration=recipe.get("duration", ""),
    )
    return redirect(next_url)
