from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone


MONGO_URI = (
    "mongodb+srv://eeshakondlapudi_db_user:Eesha1234@cluster1.sveryx9.mongodb.net/"
    "?appName=Cluster1"
)


def _get_recipe_collection():
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
        db = client["SousPaw"]
        return db["Recipes"], None
    except PyMongoError:
        return (
            None,
            "Recipe search is temporarily unavailable because the MongoDB service could not be reached.",
        )
    except Exception:
        return (
            None,
            "Recipe search is temporarily unavailable because the MongoDB service could not be reached.",
        )


def _get_mongo_database():
    try:
        import certifi
        from pymongo import MongoClient
        from pymongo.errors import PyMongoError
    except ImportError:
        return None, "MongoDB dependencies are unavailable."

    try:
        client = MongoClient(
            MONGO_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=2000,
            connectTimeoutMS=2000,
            socketTimeoutMS=2000,
        )
        return client["SousPaw"], None
    except PyMongoError:
        return None, "MongoDB could not be reached."
    except Exception:
        return None, "MongoDB could not be reached."


def _sync_user_login_document(user, event_type):
    db, _ = _get_mongo_database()
    if db is None:
        return

    user_login_collection = db["userLogin"]
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
        update_fields["last_login_at"] = now

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


def home(request):
    return render(request, "home.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("pet_customizer")

    context = {"error_message": None, "submitted_email": ""}

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        context["submitted_email"] = email

        if not email or not password:
            context["error_message"] = "Please enter your email and password."
        else:
            user = authenticate(request, username=email, password=password)
            if user is None:
                context["error_message"] = "Incorrect email or password. Please try again."
            else:
                login(request, user)
                _sync_user_login_document(user, "login")
                return redirect("pet_customizer")

    return render(request, "login.html", context)


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("pet_customizer")

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
            )
            login(request, user)
            _sync_user_login_document(user, "signup")
            return redirect("pet_customizer")

    return render(request, "signup.html", context)


@login_required
def pet_customizer(request):
    return render(request, "main.html")


@login_required
def profile_view(request):
    return render(request, "profile.html")


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


def recipe_detail(request, id):
    collection, error_message = _get_recipe_collection()
    if collection is None:
        return render(
            request,
            "recipe.html",
            {"error": error_message},
        )

    try:
        from bson.objectid import ObjectId
    except ImportError:
        return render(
            request,
            "recipe.html",
            {"error": "Recipe details are unavailable until MongoDB dependencies are installed."},
        )

    try:
        recipe = collection.find_one({"_id": ObjectId(id)})

        if not recipe:
            return render(request, "recipe.html", {"error": "Recipe not found"})

        recipe["_id"] = str(recipe["_id"])
        return render(request, "recipe.html", {"recipe": recipe})
    except Exception:
        return render(
            request,
            "recipe.html",
            {"error": "Recipe details are temporarily unavailable or the recipe ID is invalid."},
        )
