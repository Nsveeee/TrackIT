from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create demo users for Admin/Developer/Reporter roles."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Reset passwords/roles for demo users if they already exist.",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        reset = bool(options.get("reset"))

        demo = [
            {"username": "admin", "password": "Admin@12345", "role": "ADMIN"},
            {"username": "developer", "password": "Dev@12345", "role": "DEV"},
            {"username": "developer2", "password": "Dev@12345", "role": "DEV"},
            {"username": "developer3", "password": "Dev@12345", "role": "DEV"},
            {"username": "reporter", "password": "Reporter@12345", "role": "REPORTER"},
            {"username": "reporter2", "password": "Reporter@12345", "role": "REPORTER"},
            {"username": "reporter3", "password": "Reporter@12345", "role": "REPORTER"},
        ]

        for u in demo:
            user, created = User.objects.get_or_create(username=u["username"])
            if created or reset:
                user.role = u["role"]
                user.set_password(u["password"])
                user.save()

            status = "created" if created else ("updated" if reset else "exists")
            self.stdout.write(
                self.style.SUCCESS(
                    f"{status}: {u['username']} ({u['role']}) / {u['password'] if (created or reset) else '***'}"
                )
            )

        self.stdout.write(self.style.WARNING("These credentials are for local development only."))
