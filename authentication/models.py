from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
import cloudinary
from cloudinary.models import CloudinaryField
import cloudinary.uploader
import cloudinary.api
# from app.models import Post
# Create your models here.
gender_choices = [("Male","Male"),("Female","Female"),("Other","Other")]
class UserAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = CloudinaryField('image',blank=True)
    cover = CloudinaryField('image',blank=True)
    location = models.CharField(max_length=250, blank = True)
    website = models.URLField(blank=True,default="")
    mobile = models.BigIntegerField(default=0,blank=False)
    gender =  models.CharField(max_length=50, choices=gender_choices,default="", blank=False)
    bio = models.TextField(blank=True,default="")
    verified = models.BooleanField(default=False, blank=False)
    oneSignalId = models.CharField(default="",max_length=250,blank=True)
    objects = models.Manager()

    def __str__(self):
        return self.user.username

    


def create_user_account(sender, **kwargs):
    if kwargs["created"]:
        new_user = UserAccount.objects.create(user=kwargs["instance"])
    
    
#listen for when a new user has been created, if so execute the create_user_account function
post_save.connect(create_user_account, sender=User)
