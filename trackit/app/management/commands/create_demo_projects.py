from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from app.models import Project


class Command(BaseCommand):
    help = "Create 2-3 demo projects and optionally assign developers."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Reset demo projects (update descriptions and developer assignments).",
        )

    def handle(self, *args, **options):
        reset = bool(options.get("reset"))
        User = get_user_model()

        projects = [
            {
                "name": "Website Revamp",
                "description": "UI/UX improvements, performance, and responsive fixes.",
            },
            {
                "name": "Payments & Billing",
                "description": "Payment gateway integrations, invoices, and subscription flows.",
            },
            {
                "name": "Mobile App",
                "description": "Android/iOS issues, API compatibility, and crash reports.",
            },
        ]

        devs = list(User.objects.filter(role="DEV"))

        for p in projects:
            obj, created = Project.objects.get_or_create(name=p["name"])
            if created or reset:
                obj.description = p["description"]
                obj.save()

                # By default assign all current developers to demo projects.
                obj.developers.set(devs)

            status = "created" if created else ("updated" if reset else "exists")
            self.stdout.write(self.style.SUCCESS(f"{status}: {obj.name}"))

        self.stdout.write(self.style.WARNING("Demo projects are for local development only."))

