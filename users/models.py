from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken

class UserManager(BaseUserManager):

    def create_user(self, firstname, lastname, email, password=None):
        if email is None:
            raise TypeError('Users should have an Email')
        if firstname is None:
            raise TypeError('Users should have a Firstname')
        if lastname is None:
            raise TypeError('Users should have a Lastname')

        user = self.model(lastname=lastname, firstname=firstname, email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None):
        if password is None:
            raise TypeError('Password should not be none')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google', 'email': 'email'}
USER_ROLES = [
            ("CUSTOMER","Clients/Customers/Buyers"),
            ("AGENT","Real Estate Agent")
        ]
IDENTITY_DOCUMENT_CHOICES = [
            ("NATIONAL_ID","National ID Card"),
            ("DRIVERS_LICENSE","Drivers License"),
            ("PASSPORT", "Passport")
            ]
            
class User(AbstractBaseUser, PermissionsMixin):
    phone                       = models.CharField(max_length=255, unique=True, null=True, blank=True)
    firstname                   = models.CharField(max_length=255)
    lastname                    = models.CharField(max_length=255)
    email                       = models.EmailField(max_length=255, unique=True, db_index=True)
    is_verified                 = models.BooleanField(default=False)
    is_active                   = models.BooleanField(default=True)
    is_staff                    = models.BooleanField(default=False)
    auth_provider               = models.CharField(
        max_length=255, blank=False,
        null=False, default=AUTH_PROVIDERS.get('email'))

    nationality                 = models.CharField(max_length=255)
    agency                      = models.CharField(max_length=255)
    title                       = models.CharField(max_length=255)
    summary                     = models.TextField(default="")

    role                        = models.CharField(
        max_length=255,
        choices= USER_ROLES,
        default= USER_ROLES[0][0]
    )
    secondary_phone             = models.CharField(max_length=255)
    date_of_birth               = models.DateField(null=True)
    address                     = models.TextField()
    city                        = models.CharField(max_length=255)
    country                     = models.CharField(max_length=255)
    identity_document_type      = models.CharField(
        max_length=255,
        choices= IDENTITY_DOCUMENT_CHOICES,
        default= IDENTITY_DOCUMENT_CHOICES[0][0]
    )
    identity_document_url       = ArrayField(models.URLField(), default=list)
    display_photo               = models.URLField()
    proof_of_address_document   = models.URLField()
    created_at                  = models.DateTimeField(auto_now_add=True)
    updated_at                  = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    objects = UserManager()

    def __str__(self):
        return f'{self.firstname} {self.lastname}'

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
    class Meta:
        db_table = "Users"