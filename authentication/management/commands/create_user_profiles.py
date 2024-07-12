from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from authentication.models import UserProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates UserProfiles for users that do not have one'

    def handle(self, *args, **options):
        users_without_profile = User.objects.filter(userprofile__isnull=True)
        for user in users_without_profile:
            UserProfile.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Created UserProfile for {user.username}'))

        self.stdout.write(self.style.SUCCESS(f'Created {users_without_profile.count()} UserProfiles'))