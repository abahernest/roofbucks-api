from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import MinLengthValidator

from album.models import MediaAlbum, MediaFiles
from utils.constants import STAGES_OF_PROFILE_COMPLETION

class UserManager(BaseUserManager):

    def create_user(self, firstname, lastname, email, role, password=None):
        if email is None:
            raise TypeError('Users should have an Email')
        if firstname is None:
            raise TypeError('Users should have a Firstname')
        if lastname is None:
            raise TypeError('Users should have a Lastname')
        if role is None:
            raise TypeError('Users should have a role')

        user = self.model(lastname=lastname, firstname=firstname, email=self.normalize_email(email), role=role)
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


USER_ROLES = [
            ("SHAREHOLDER","ShareHolder/Customers/Buyers"),
            ("AGENT","Real Estate Agent")
        ]
IDENTITY_DOCUMENT_CHOICES = [
            ("NATIONAL_ID","National ID Card"),
            ("DRIVERS_LICENSE","Drivers License"),
            ("PASSPORT", "Passport")
            ]

def stagesOfProfileCompletion():
    return STAGES_OF_PROFILE_COMPLETION

class User(AbstractBaseUser, PermissionsMixin):
    phone                       = models.CharField(max_length=255, unique=True, null=True, blank=True)
    firstname                   = models.CharField(max_length=255)
    lastname                    = models.CharField(max_length=255)
    email                       = models.EmailField(max_length=255, unique=True, db_index=True)
    is_verified                 = models.BooleanField(default=False)
    is_active                   = models.BooleanField(default=True)
    is_staff                    = models.BooleanField(default=False)
    display_name                = models.CharField(max_length=255, unique=True, null=True, blank=True)


    nationality                 = models.CharField(max_length=255, null=True, blank=True)
    title                       = models.CharField(max_length=255, null=True, blank=True)
    summary                     = models.TextField(default="")

    role                        = models.CharField(
        max_length=255,
        choices= USER_ROLES,
        default= USER_ROLES[0][0]
    )
    secondary_phone             = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth               = models.DateField(null=True)
    address                     = models.TextField()
    city                        = models.CharField(max_length=255)
    country                     = models.CharField(max_length=255)
    identity_document_type      = models.CharField(
        max_length=255,
        choices= IDENTITY_DOCUMENT_CHOICES,
        default= IDENTITY_DOCUMENT_CHOICES[0][0]
    )
    identity_document_album = models.ForeignKey(MediaAlbum, null=True, on_delete=models.CASCADE)
    identity_document_number    = models.CharField(max_length=65, null=True)
    identity_document_expiry_date   = models.DateField(null=True)
    display_photo               = models.ImageField(upload_to='display_photo/')
    proof_of_address_document   = models.FileField(upload_to='proof_of_address/')
    stages_of_profile_completion = models.JSONField(default=stagesOfProfileCompletion)
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

    def get_company(self):
        company = Company.objects.filter(user=self).all()

        if len(company)<1:
            return None
        
        setattr(self,'company', company[0])
        return self.company

    def get_identity_documents(self):
        if not self.identity_document_album:
            return None

        documents = MediaFiles.objects.filter(album=self.identity_document_album).values('id', 'document').all()

        setattr(self, 'identity_documents', documents)
        return self.identity_documents

    class Meta:
        db_table = "Users"


class Company(models.Model):
    is_verified                 = models.BooleanField(default=False)
    user                        = models.OneToOneField(to=User, on_delete=models.CASCADE)
    registration_number         = models.CharField(null=False, blank=False, max_length=65, validators=[MinLengthValidator(4)], unique=True)
    reference_number            = models.CharField(null=False, blank=False, max_length=12, validators=[MinLengthValidator(12)], unique=True)
    registered_name             = models.CharField(null=False, blank=False,max_length=500, unique=True)
    email                       = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    phone                       = models.CharField(max_length=255, unique=True, null=True, blank=True)
    display_name                = models.CharField(max_length=255)
    website                     = models.CharField(max_length=255)
    city                        = models.CharField(max_length=255)
    country                     = models.CharField(max_length=255)
    description                 = models.TextField()
    company_logo                = models.ImageField(upload_to='company_logo/')
    certificate_of_incorporation   = models.FileField(upload_to='certificate_of_incorporation/')
    bank_information            = ArrayField(models.JSONField(default=dict), default= list)
    created_at                  = models.DateTimeField(auto_now_add=True)
    updated_at                  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Company'

    def get_reviews(self):
        setattr (self, 'reviews', Review.objects.filter(company=self))
        return self.reviews



class EmailVerification(models.Model):
    is_verified = models.BooleanField(default=False)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    token = models.CharField(null=False, blank=False,
                             max_length=6, validators=[MinLengthValidator(6)])
    token_expiry = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'EmailVerification'


class Review(models.Model):
    rating  = models.IntegerField(null=True)
    review  = models.TextField()
    company = models.ForeignKey(to=Company, null=False, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(to=User, null=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Reviews'