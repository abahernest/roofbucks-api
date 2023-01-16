from django.db import models, transaction
from typing import Union, List, Dict

from users.models import User, USER_ROLES

CHOICES_FOR_STATUS = [
    ("UNREAD", "unread notifications"),
    ("READ", "read notifications"),
]


class Notifications(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=256,
        choices=CHOICES_FOR_STATUS,
        default=CHOICES_FOR_STATUS[0][0])
    user_role = models.CharField(
        max_length=256,
        choices=USER_ROLES,
        default=USER_ROLES[0][0])
    message = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Notifications"

    @classmethod
    @transaction.atomic
    def new_entry(cls, user: User, message: str):
        try:
            notification = cls.objects.create(
                user=user, 
                user_role = user.role, 
                message=message)

            return notification
            
        except Exception as e:
            raise e


    @classmethod
    @transaction.atomic
    def new_bulk_entry(cls, notificationArray: List[Dict[str, Union[str, User]]]):
        try:
            notificationList=[]
            for item in notificationArray:
                user = item.get('user')
                user_role = user.role
                message = item.get('message')

                notificationList.append( 
                    cls(user=user,user_role=user_role,message=message) )

            notifications = cls.objects.bulk_create(notificationList)

            return notifications
            
        except Exception as e:
            raise e
