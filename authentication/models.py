from django.db import models
from django.core.validators import MinLengthValidator
from users.models import User

class EmailVerification(models.Model):
    is_verified                     = models.BooleanField(default=False)
    user                            = models.OneToOneField(to=User, on_delete=models.CASCADE)
    token                           = models.CharField(null=False, blank=False, max_length=6, validators=[MinLengthValidator(6)])
    token_expiry                    = models.DateTimeField()
    created_at                      = models.DateTimeField(auto_now_add=True)
    updated_at                      = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'EmailVerification'


class CompanyVerification(models.Model):
    is_verified = models.BooleanField(default=False)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    registration_number = models.CharField(null=False, blank=False,
                                           max_length=65, validators=[MinLengthValidator(4)], unique=True)
    reference_number = models.CharField(null=False, blank=False,
                                        max_length=12, validators=[MinLengthValidator(12)], unique=True)
    registered_company_name = models.CharField(null=False, blank=False,
                                        max_length=500, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'CompanyVerification'
