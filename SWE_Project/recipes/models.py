from django.contrib.auth.models import User
from django.db import models


class PetProfile(models.Model):
    SPECIES_DOG = "dog"
    SPECIES_CAT = "cat"
    SPECIES_CHOICES = [
        (SPECIES_DOG, "Dog"),
        (SPECIES_CAT, "Cat"),
    ]

    GENDER_MALE = "Male"
    GENDER_FEMALE = "Female"
    GENDER_CHOICES = [
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="pet_profile")
    name = models.CharField(max_length=50, default="Lucky")
    species = models.CharField(max_length=10, choices=SPECIES_CHOICES, default=SPECIES_DOG)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default=GENDER_MALE)

    def __str__(self):
        return f"{self.user.username}'s pet"


class SavedRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_recipes")
    recipe_id = models.CharField(max_length=64)
    recipe_name = models.CharField(max_length=255)
    cuisine = models.CharField(max_length=120, blank=True)
    duration = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "recipe_id"], name="unique_saved_recipe")
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} saved {self.recipe_name}"
