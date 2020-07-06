from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    Manager for creating users and admins.
    """
    use_in_migrations = True

    def create_user(self, email, password):
        """
        Creates and saves a User with the given email.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=UserManager.normalize_email(email),
        )
        user.set_password(password)
        user.has_migrated_pwd = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of birth and password.
        """
        user = self.create_user(email, password=password)

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.has_migrated_pwd = True
        user.save(using=self._db)
        return user
