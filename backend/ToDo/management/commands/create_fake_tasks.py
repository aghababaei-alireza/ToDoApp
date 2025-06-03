from django.core.management.base import BaseCommand
from faker import Faker
import random
from datetime import datetime, timezone
from Account.models import User
from ToDo.models import Task


class Command(BaseCommand):
    help = "Create a user and generate 5 fake tasks."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker()

    def handle(self, *args, **options):
        # Create fake user
        user = User.objects.create_user(
            email=self.fake.email(),
            password="fake@123456",
            is_verified=True
        )

        # Create tasks
        for _ in range(5):
            Task.objects.create(
                user=user,
                title=self.fake.sentence(nb_words=5),
                description=self.fake.paragraph(nb_sentences=4),
                due_date=datetime.now(tz=timezone.utc) +
                self.fake.time_delta(end_datetime="+30d"),
                completed=random.choice([True, False])
            )

        self.stdout.write(self.style.SUCCESS(
            f"Successfully created user and tasks.\nCreated user:\n\tEmail = {user.email}\n\tPassword = {'fake@123456'}"))
