from django.db import models
from authentication.models import UserAccount, User
import cloudinary
from cloudinary.models import CloudinaryField
from django.db.models.signals import post_save
import cloudinary.uploader
import cloudinary.api
# Create your models here.
genres = [("HipHop", "HipHop"), ("Jazz", "Jazz"), ("House", "House"), ("RNB","RNB"),("EDM","EDM"),("Qgom","Qgom"), ("Amapiano","Amapiano")]
class Notifications(models.Model):
    user =  models.ForeignKey(User, on_delete=models.CASCADE)
    pushAll = models.BooleanField(default=False)
    like = models.BooleanField(default=False)
    upload = models.BooleanField(default=False)
    comment = models.BooleanField(default=False)
    features = models.BooleanField(default=False)
    dm = models.BooleanField(default=False)
    follow = models.BooleanField(default=False)
    tag = models.BooleanField(default=False)
    repost = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username

def create_notifications(sender, **kwargs):
    if kwargs["created"]:
        new_user = Notifications.objects.create(user=kwargs["instance"])
    
    
#listen for when a new user has been created, if so execute the create_notifications function
post_save.connect(create_notifications, sender=User)
    
class Post(models.Model):
    # post_file = CloudinaryField(resource_type='video',blank=True)
    post_file = models.CharField(max_length=500,blank=False,default="")
    user =  models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=150,blank=False,default="")
    genre = models.CharField(max_length=150,blank=False,default="") 
    date = models.DateField(auto_now_add=True)
    # date.editable = True
    playlisted = models.BooleanField(default=True)
    reposted = models.BooleanField(default=False)
    current_feed_play = models.BooleanField(default=True)
    video_length = models.CharField(max_length=150,blank=True,default="")
    start_at = models.CharField(max_length=150,blank=False,default=0)
    active = models.BooleanField(default=False)
    scheduled_for = models.CharField(max_length=150, blank=True,default="")
    first_play = models.BooleanField(default=True)
    objects = models.Manager()


class Tag(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    taged_user =  models.ForeignKey(User, on_delete=models.CASCADE)

class Repost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE,default="")
    objects = models.Manager()
    def __str__(self):
        return self.post.description

class Like(models.Model):
    post =  models.ForeignKey(Post, on_delete=models.CASCADE)
    user =  models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    objects = models.Manager()

class View(models.Model):
    post =  models.ForeignKey(Post, on_delete=models.CASCADE)
    user =  models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    objects = models.Manager()

# class Comment(models.Model):
#     post =  models.ForeignKey(Post, on_delete=models.CASCADE)
#     user =  models.ForeignKey(User, on_delete=models.CASCADE)
#     date = models.DateField(auto_now_add=True)
#     comment = models.CharField(max_length=150,blank=False)
#     objects = models.Manager()


# class Chat(models.Model):
#     user_one = models.ForeignKey(User, on_delete=models.CASCADE)
#     user_two = models.ForeignKey(user, on_delete=models.CASCADE)



class Follow(models.Model):
    follower =  models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    followed =  models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    objects = models.Manager()

class ChatFiles(models.Model):
    file_name = models.CharField(max_length=150,blank=False,default="")
    post_file = models.FileField(upload_to='images')

