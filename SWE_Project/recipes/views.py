from django.shortcuts import render


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


def home(request):
    return render(request, "home.html")


def login_view(request):
    return render(request, "login.html")


def signup_view(request):
    return render(request, "signup.html")


def pet_customizer(request):
    return render(request, "main.html")


def profile_view(request):
    return render(request, "profile.html")


def tutorial_view(request):
    return render(request, "tutorialsforhowitworks.html")


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
