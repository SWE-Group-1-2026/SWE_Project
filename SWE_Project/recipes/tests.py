import re
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.core import mail
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from . import views
from .models import PetProfile, SavedRecipe


class EmailVerificationTests(TestCase):
    def test_signup_creates_inactive_user_and_sends_verification_email(self):
        response = self.client.post(
            reverse("signup"),
            {
                "email": "newuser@example.com",
                "password": "strongpass123",
                "confirm_password": "strongpass123",
            },
        )

        user = User.objects.get(username="newuser@example.com")
        self.assertFalse(user.is_active)
        self.assertRedirects(
            response,
            f"{reverse('verify_email_notice')}?email=newuser%40example.com",
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Verify your SousPaw account", mail.outbox[0].subject)
        self.assertIn("verify-email", mail.outbox[0].body)

    @override_settings(EMAIL_PROVIDER="gmail_api")
    @patch("recipes.views.send_gmail_api_message")
    def test_signup_can_send_verification_email_with_gmail_api(self, mock_send_gmail_api_message):
        response = self.client.post(
            reverse("signup"),
            {
                "email": "gmailapi@example.com",
                "password": "strongpass123",
                "confirm_password": "strongpass123",
            },
        )

        self.assertRedirects(
            response,
            f"{reverse('verify_email_notice')}?email=gmailapi%40example.com",
        )
        mock_send_gmail_api_message.assert_called_once()

    def test_unverified_user_is_redirected_to_verify_notice_on_login(self):
        User.objects.create_user(
            username="pending@example.com",
            email="pending@example.com",
            password="testpass123",
            is_active=False,
        )

        response = self.client.post(
            reverse("login"),
            {
                "email": "pending@example.com",
                "password": "testpass123",
            },
        )

        self.assertRedirects(
            response,
            f"{reverse('verify_email_notice')}?email=pending%40example.com",
        )

    def test_verification_link_activates_account_and_allows_login(self):
        self.client.post(
            reverse("signup"),
            {
                "email": "verified@example.com",
                "password": "strongpass123",
                "confirm_password": "strongpass123",
            },
        )

        email_body = mail.outbox[0].body
        match = re.search(r"http://testserver(?P<path>/verify-email/[^\\s]+/[^\\s/]+/)", email_body)
        self.assertIsNotNone(match)

        verify_response = self.client.get(match.group("path"))
        self.assertContains(verify_response, "Your email is confirmed")

        user = User.objects.get(username="verified@example.com")
        user.refresh_from_db()
        self.assertTrue(user.is_active)

        login_response = self.client.post(
            reverse("login"),
            {
                "email": "verified@example.com",
                "password": "strongpass123",
            },
        )
        self.assertRedirects(login_response, reverse("pet_customizer"))

    @patch("recipes.views._send_verification_email", side_effect=Exception("smtp failed"))
    def test_signup_shows_friendly_error_when_email_send_fails(self, _mock_send_email):
        response = self.client.post(
            reverse("signup"),
            {
                "email": "mailfail@example.com",
                "password": "strongpass123",
                "confirm_password": "strongpass123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "send the verification email right now")
        self.assertFalse(User.objects.filter(username="mailfail@example.com").exists())

    @override_settings(EMAIL_PROVIDER="bad-value")
    def test_signup_shows_friendly_error_for_invalid_email_provider(self):
        response = self.client.post(
            reverse("signup"),
            {
                "email": "badprovider@example.com",
                "password": "strongpass123",
                "confirm_password": "strongpass123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "send the verification email right now")
        self.assertFalse(User.objects.filter(username="badprovider@example.com").exists())


class PetCustomizerViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="chef@example.com",
            email="chef@example.com",
            password="testpass123",
        )

    def test_pet_customizer_loads_saved_pet_profile(self):
        PetProfile.objects.create(
            user=self.user,
            name="Biscuit",
            species=PetProfile.SPECIES_CAT,
            gender=PetProfile.GENDER_FEMALE,
        )
        self.client.login(username="chef@example.com", password="testpass123")

        response = self.client.get(reverse("pet_customizer"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Biscuit"', html=False)
        self.assertContains(response, "Gender: Female")

    def test_pet_customizer_saves_posted_profile(self):
        self.client.login(username="chef@example.com", password="testpass123")

        response = self.client.post(
            reverse("pet_customizer"),
            {
                "name": "Mochi",
                "species": PetProfile.SPECIES_CAT,
                "gender": PetProfile.GENDER_FEMALE,
            },
        )

        self.assertEqual(response.status_code, 200)
        pet_profile = PetProfile.objects.get(user=self.user)
        self.assertEqual(pet_profile.name, "Mochi")
        self.assertEqual(pet_profile.species, PetProfile.SPECIES_CAT)
        self.assertEqual(pet_profile.gender, PetProfile.GENDER_FEMALE)
        self.assertContains(response, "Pet customization saved.")


class RecipeDetailViewTests(TestCase):
    @patch("recipes.views._get_recipe_collection")
    def test_recipe_detail_links_to_separate_steps_page(self, mock_get_collection):
        mock_collection = Mock()
        mock_collection.find_one.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            "id": "507f1f77bcf86cd799439011",
            "recipe_name": "Pumpkin Bites",
            "cuisine": "Homestyle",
            "duration": "20 minutes",
            "ingredients": ["Pumpkin", "Oats"],
            "recipe_steps": ["Mix ingredients", "Bake until soft"],
        }
        mock_get_collection.return_value = (mock_collection, None)

        response = self.client.get(reverse("recipe_detail", args=["507f1f77bcf86cd799439011"]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Start Cooking")
        self.assertContains(response, "Mix ingredients")
        self.assertContains(response, "Bake until soft")
        self.assertContains(response, reverse("recipe_steps", args=["507f1f77bcf86cd799439011"]))

    @patch("recipes.views._get_recipe_collection")
    def test_recipe_steps_renders_step_player_on_separate_page(self, mock_get_collection):
        mock_collection = Mock()
        mock_collection.find_one.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            "id": "507f1f77bcf86cd799439011",
            "recipe_name": "Pumpkin Bites",
            "cuisine": "Homestyle",
            "duration": "20 minutes",
            "ingredients": ["Pumpkin", "Oats"],
            "recipe_steps": ["Mix ingredients", "Bake until soft"],
        }
        mock_get_collection.return_value = (mock_collection, None)

        response = self.client.get(reverse("recipe_steps", args=["507f1f77bcf86cd799439011"]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-step-current', html=False)
        self.assertContains(response, "Previous")
        self.assertContains(response, "Next")
        self.assertContains(response, "Restart")

    @patch("recipes.views._get_recipe_collection")
    def test_authenticated_user_can_save_recipe_from_detail_page(self, mock_get_collection):
        user = User.objects.create_user(
            username="saved@example.com",
            email="saved@example.com",
            password="testpass123",
        )
        self.client.login(username="saved@example.com", password="testpass123")

        mock_collection = Mock()
        mock_collection.find_one.return_value = {
            "_id": "507f1f77bcf86cd799439011",
            "id": "507f1f77bcf86cd799439011",
            "recipe_name": "Pumpkin Bites",
            "cuisine": "Homestyle",
            "duration": "20 minutes",
            "ingredients": ["Pumpkin", "Oats"],
            "recipe_steps": ["Mix ingredients", "Bake until soft"],
        }
        mock_get_collection.return_value = (mock_collection, None)

        response = self.client.post(
            reverse("toggle_saved_recipe", args=["507f1f77bcf86cd799439011"]),
            {"next": reverse("recipe_detail", args=["507f1f77bcf86cd799439011"])},
        )

        self.assertRedirects(response, reverse("recipe_detail", args=["507f1f77bcf86cd799439011"]))
        saved_recipe = SavedRecipe.objects.get(user=user, recipe_id="507f1f77bcf86cd799439011")
        self.assertEqual(saved_recipe.recipe_name, "Pumpkin Bites")


class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="profile@example.com",
            email="profile@example.com",
            password="testpass123",
        )

    def test_profile_requires_login(self):
        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_profile_lists_saved_recipes(self):
        SavedRecipe.objects.create(
            user=self.user,
            recipe_id="abc123",
            recipe_name="Blueberry Biscuits",
            cuisine="Bakery",
            duration="35 minutes",
        )
        self.client.login(username="profile@example.com", password="testpass123")

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Blueberry Biscuits")
        self.assertContains(response, "Open Recipe")

    def test_profile_shows_regular_user_role_without_admin_link(self):
        self.client.login(username="profile@example.com", password="testpass123")

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Role: User")
        self.assertNotContains(response, reverse("admin_dashboard"))


class AdminAccessTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin@example.com",
            email="admin@example.com",
            password="testpass123",
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="testpass123",
        )

    def test_admin_dashboard_requires_login(self):
        response = self.client.get(reverse("admin_dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_regular_user_cannot_open_admin_dashboard(self):
        self.client.login(username="user@example.com", password="testpass123")

        response = self.client.get(reverse("admin_dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_admin_login_redirects_to_admin_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {
                "email": "admin@example.com",
                "password": "testpass123",
            },
        )

        self.assertRedirects(response, reverse("admin_dashboard"))

    def test_admin_user_can_open_admin_dashboard_and_see_user_roles(self):
        SavedRecipe.objects.create(
            user=self.regular_user,
            recipe_id="admin-check",
            recipe_name="Admin Recipe",
            cuisine="Testing",
            duration="15 minutes",
        )
        self.client.login(username="admin@example.com", password="testpass123")

        response = self.client.get(reverse("admin_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin Dashboard")
        self.assertContains(response, "admin@example.com")
        self.assertContains(response, "user@example.com")
        self.assertContains(response, "Admins")
        self.assertContains(response, "Saved recipes: 1")

    def test_admin_profile_shows_extra_options(self):
        self.client.login(username="admin@example.com", password="testpass123")

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Role: Admin")
        self.assertContains(response, reverse("admin_dashboard"))
        self.assertContains(response, reverse("admin_add_recipe"))

    def test_regular_user_cannot_open_admin_recipe_form(self):
        self.client.login(username="user@example.com", password="testpass123")

        response = self.client.get(reverse("admin_add_recipe"))

        self.assertEqual(response.status_code, 403)

    @patch("recipes.views._get_mongo_database")
    def test_admin_can_add_recipe_from_form(self, mock_get_mongo_database):
        insert_result = Mock(inserted_id="507f1f77bcf86cd799439012")
        mock_recipe_collection = Mock()
        mock_recipe_collection.insert_one.return_value = insert_result
        mock_db = {views.MONGO_RECIPE_COLLECTION: mock_recipe_collection}
        mock_get_mongo_database.return_value = (mock_db, None)

        self.client.login(username="admin@example.com", password="testpass123")

        response = self.client.post(
            reverse("admin_add_recipe"),
            {
                "recipe_name": "Pumpkin Bites",
                "cuisine": "Homestyle",
                "duration": "20 minutes",
                "ingredients": "Pumpkin\nOats\nCinnamon",
                "recipe_steps": "Mix ingredients\nBake until soft",
            },
        )

        self.assertRedirects(
            response,
            reverse("recipe_detail", args=["507f1f77bcf86cd799439012"]),
        )
        mock_recipe_collection.insert_one.assert_called_once()
        saved_document = mock_recipe_collection.insert_one.call_args.args[0]
        self.assertEqual(saved_document["recipe_name"], "Pumpkin Bites")
        self.assertEqual(saved_document["cuisine"], "Homestyle")
        self.assertEqual(saved_document["duration"], "20 minutes")
        self.assertEqual(saved_document["ingredients"], ["Pumpkin", "Oats", "Cinnamon"])
        self.assertEqual(saved_document["recipe_steps"], ["Mix ingredients", "Bake until soft"])
        self.assertEqual(saved_document["created_by"], "admin@example.com")

    @patch("recipes.views._get_mongo_database")
    def test_admin_add_recipe_shows_validation_error_for_missing_steps(self, mock_get_mongo_database):
        self.client.login(username="admin@example.com", password="testpass123")

        response = self.client.post(
            reverse("admin_add_recipe"),
            {
                "recipe_name": "Pumpkin Bites",
                "cuisine": "Homestyle",
                "duration": "20 minutes",
                "ingredients": "Pumpkin\nOats",
                "recipe_steps": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add at least one recipe step.")
        mock_get_mongo_database.assert_not_called()
