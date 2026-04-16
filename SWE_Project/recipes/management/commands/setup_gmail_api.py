from django.core.management.base import BaseCommand

from recipes.gmail_api import _load_gmail_credentials


class Command(BaseCommand):
    help = "Runs the Gmail API OAuth flow and stores a reusable token."

    def handle(self, *args, **options):
        _load_gmail_credentials()
        self.stdout.write(
            self.style.SUCCESS(
                "Gmail API authorization complete. Token saved for future email sends."
            )
        )
