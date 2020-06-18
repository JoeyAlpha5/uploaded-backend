from django.shortcuts import render
from django.contrib.auth.models import User, Group
from  rest_framework import viewsets
from .serializers import UserSerializer, GroupSerializer
from django.http import JsonResponse, HttpResponse
from .models import UserAccount
from django.core import serializers
from app.models import Follow
from app.models import Post, View, Like, Repost, ChatFiles, Notifications, Tag
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import pyrebase
import base64
from django.core.files import File
import googlemaps
from time import sleep
import cloudinary
from datetime import date
import datetime
import pytz
from django.http import HttpResponse
from background_task import background
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client as TwilioRestClient
from django.conf import settings
import onesignal as onesignal_sdk
@csrf_exempt
def UserViewSet(request):
    if request.method == "GET" and request.GET["type"] == "login":
        email = request.GET["email"]
        password = request.GET["password"]
        # 
        mobile = request.GET["mobile"]

        user = User.objects.filter(email=email)
        ##set the sessions
        if User.objects.filter(email=email).exists():
            is_password = user[0].check_password(password)
            if is_password == True:
                response = JsonResponse({"data":"Authentication test passed", "username":user[0].username,"id":user[0].id})
            else:
                response = JsonResponse({"data":"Authentication test failed"})
        else:
            new_user = User()
            new_user.email = email
            new_user.username = mobile
            new_user.set_password(password)
            new_user.save()
            ## send email to new user
            message = Mail(
            from_email='info@uploadedstream.com',
            to_emails=new_user.email,
            subject='Uploaded Account Password',
            html_content='<strong>Your Uploaded credentials are as follows username: '+mobile+ ' and password is: '+password+'</strong>')
            ## send sms to users
            # to = '+'+str(mobile)
            # fromNum = "+18704740315"
            # message =  "Your Uploaded password is: #ABaTestUser, Please use this password when loging in to the app"
            # client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # client.messages.create(body=message, to=to, from_=fromNum)
            # response = JsonResponse({"data":"Authentication test passed", "username":new_user.username,"id":new_user.id})
            



    elif request.method == "GET" and request.GET["type"] == "places":
        search_input = request.GET["input"]
        gmaps = googlemaps.Client(key='AIzaSyAZc9GaA42di2bFYeIQj9hPuNhqZN6S5XA')
        places = gmaps.places_autocomplete(search_input, types='(cities)')
        print(places)
        response = JsonResponse({"data":places})


    ##get profile content
    elif request.method == "GET" and request.GET["type"] == "profile":
        email = request.GET["email"]
        user = User.objects.filter(email=email)
        ##
        user_acc = UserAccount.objects.filter(user=user[0])
        ##followers
        followers = Follow.objects.filter(followed=user[0]).count()

        ##
        following = Follow.objects.filter(follower=user_acc[0]).count()

        posts = Post.objects.filter(user=user[0])
        users_posts = Post.objects.filter(user=user[0]).count() 
        post_array = []
        ##user's postes
        for i in posts:
            #get post likes, comments and views
            views = View.objects.filter(post = i).count()
            likes = Like.objects.filter(post = i).count()
            # comments = Comment.objects.filter(post = i).count();
            if i.active:
                post_data = {"id":i.id,"post_file":str(i.post_file), "likes": likes, "views":views, "playlisted":i.playlisted}
                post_array.append(post_data)

        ##user's reposts
        repostests = Repost.objects.filter(user=user[0])
        for re in repostests:
            reposted_post = re.post
            #get post likes, comments and views
            views = View.objects.filter(post = reposted_post).count()
            likes = Like.objects.filter(post = reposted_post).count()
            post_data = {"id":reposted_post.id,"post_file":str(reposted_post.post_file), "likes": likes, "views":views,"reposted":True}
            post_array.append(post_data)
        

        if user_acc[0].image and user_acc[0].cover:
            returning_user = [{"cover":str(user_acc[0].cover),"first_name":user[0].first_name,"location":user_acc[0].location,"username":user_acc[0].user.username, "followers":followers,"following":following,"bio":user_acc[0].bio,"image":str(user_acc[0].image),"total_posts":users_posts, "website":user_acc[0].website}]
        elif user_acc[0].cover:
            returning_user = [{"cover":str(user_acc[0].cover),"first_name":user[0].first_name,"location":user_acc[0].location,"username":user_acc[0].user.username, "followers":followers,"following":following,"bio":user_acc[0].bio, "total_posts":users_posts, "website":user_acc[0].website}]
        elif user_acc[0].image:
            returning_user = [{"image":str(user_acc[0].image),"first_name":user[0].first_name,"location":user_acc[0].location,"username":user_acc[0].user.username, "followers":followers,"following":following,"bio":user_acc[0].bio, "total_posts":users_posts, "website":user_acc[0].website}]
        else:
            returning_user = [{"first_name":user[0].first_name,"location":user_acc[0].location,"username":user_acc[0].user.username, "followers":followers,"following":following,"bio":user_acc[0].bio, "total_posts":users_posts, "website":user_acc[0].website}]
            


        response = JsonResponse({"Response": returning_user,"posts":post_array})


    elif request.method == "GET" and request.GET["type"] == "getPost":
        post_id = request.GET["post"]
        user_email = request.GET["email"]
        post = Post.objects.filter(id=post_id)
        user = User.objects.filter(email=user_email)
        user_acc = UserAccount.objects.filter(user=post[0].user)

        if user_acc[0].image:
            image = str(user_acc[0].image)
        else:
            image = "none"

        post_array = []
        for i in post:
            #get post likes, comments and views
            views = View.objects.filter(post = i).count()
            likes = Like.objects.filter(post = i).count()
            liked = Like.objects.filter(user=user[0],post=i).count()
            repost_count = Repost.objects.filter(post=i).count()
            # comments = Comment.objects.filter(post = i).count();
            data = {"image":image,"user_id":i.user.id,"user_email":i.user.email,"genre":i.genre,"liked":liked,"post_id":i.id,"username":i.user.username,"like":likes,"description":i.description,"reposts":repost_count, "file": str(i.post_file)}
            post_array.append(data)
        
        response = JsonResponse({"post":post_array})
        
    elif request.method == "GET" and request.GET["type"] == "search":
        user = User.objects.filter(email=request.GET["email"])
        users = []
        all_users = User.objects.all()
        Term = request.GET["Term"].lower()
        print(Term)
        for u in all_users:
            print(u.username)
            if Term in u.first_name.lower() and Term != "" or Term in u.last_name.lower() and Term != "" or Term in u.username.lower() and Term != "":
                user_acc = UserAccount.objects.filter(user=u)
                if user_acc[0].image:
                    data = {"email":u.email,"id":u.id,"first_name": u.first_name, "last_name": u.last_name,"image":str(user_acc[0].image),"username":u.username }
                else:
                    data = {"email":u.email,"id":u.id,"first_name": u.first_name, "last_name": u.last_name,"username":u.username}
                users.append(data)

        response = JsonResponse({"Response": users})



    # elif request.method == "GET" and request.GET["type"] == "searchPlaces":
    #     user = User.objects.filter(email=request.GET["email"])
    #     post_locations = []
    #     all_users = User.objects.all()
    #     Term = request.GET["Term"].lower()
    #     print(Term)
    #     user_acc = UserAccount.objects.all()
    #     for acc in user_acc:
    #         if acc.user != user[0]:
    #             if Term in acc.location:
    #                 posts = Post.objects.filter(location = acc.location)
    #                 for p in posts:
    #                     if p.active == True and p.current_feed_play == True
    #                         data = {"post_image":str(p.post_file),"post_id":p.id}
    #                         post_locations.append(data)


        


    elif request.method == "GET" and request.GET["type"] == "searchPage":
        if 'count' not in request.GET:
            first_count = 0
            last_count = 16
        else:
            count = int(request.GET["count"])
            if count == 16:
                first_count = 0
                last_count = 16
            else:
                first_count = count + 1
                last_count = count + 7
        posts = Post.objects.all()[first_count:last_count]
        post_array = []
        
        for p in posts:
            if p.current_feed_play == True and p.active == True:
                likes = Like.objects.filter(post=p).count()
                item = {"username":p.user.username,"user_email":p.user.email,"post_id": p.id,"file":str(p.post_file), "date":p.date,"genre":p.genre,"likes":likes} 
                post_array.append(item)


        response = JsonResponse({"Response":post_array, "One": [post_array[0]] })


    elif request.method == "GET" and request.GET["type"] ==  "setViews":
        post_id = request.GET["post_id"]
        username = request.GET["username"]
        post = Post.objects.filter(id=post_id)
        user = User.objects.filter(username=username)
        view_exists = View.objects.filter(user=user[0],post=post[0]).exists()
        if view_exists == False:
            new_view = View()
            new_view.post = post[0]
            new_view.user = user[0]
            new_view.save()

        view_count = View.objects.filter(post=post[0]).count()
        return JsonResponse({"Response": view_exists, "view_count":view_count})


    elif request.method == "GET" and request.GET["type"] == "feed":
        current_user = User.objects.filter(email=request.GET["email"])
        current_user_user_account = UserAccount.objects.filter(user=current_user[0])
        feed = []
        # post = Post.objects.all().order_by("-date")
        if 'count' not in request.GET:
            post = Post.objects.order_by("-date")[:10]
        else:
            count = int(request.GET["count"])
            print("count is ", count)
            if count != 0:
                post = Post.objects.order_by("-date")[count:(count+11)]
            else:
                post = Post.objects.order_by("-date")[:10]


        # 11, 12, 13, 14, 15,16,17,18,19,20
        # print("following", followers)
        for p in post:
            following =  Follow.objects.filter(follower=current_user_user_account[0],followed=p.user)
            if following.exists():
                post_id = p.id
                genre= p.genre
                likes = Like.objects.filter(post=p).count()
                repost_count = Repost.objects.filter(post=p).count()
                ##check if the post is liked
                liked = Like.objects.filter(post=p, user=current_user[0]).count()
                reposted_by_this_user = Repost.objects.filter(post=p,user=current_user[0]).count()
                # comments = Comment.objects.filter(post=p).count()
                views = View.objects.filter(post=p).count()
                # get the number of posts 
                posts_count = Post.objects.filter(user=p.user).count()
                ##get owner profile
                user_profile = UserAccount.objects.filter(user=p.user)
                if user_profile[0].image:
                    profile_image = str(user_profile[0].image)
                else:
                    profile_image = "none"

                if p.active == True:
                    data = {"image":profile_image,"user_id":p.user.id,"user_email":p.user.email,"genre":genre,"liked":liked,"post_id":post_id,"username":p.user.username,"like":likes,"description":p.description,"reposts":repost_count, "file": str(p.post_file),"start":p.start_at,"post_count":posts_count,"reposted":reposted_by_this_user}
                    feed.append(data)
        
        if len(feed) == 0:
            for p in post:
                post_id = p.id
                genre= p.genre
                likes = Like.objects.filter(post=p).count()
                repost_count = Repost.objects.filter(post=p).count()
                ##check if the post is liked
                liked = Like.objects.filter(post=p, user=current_user[0]).count()
                reposted_by_this_user = Repost.objects.filter(post=p,user=current_user[0]).count()
                # comments = Comment.objects.filter(post=p).count()
                views = View.objects.filter(post=p).count()
                # get the number of posts 
                posts_count = Post.objects.filter(user=p.user).count()
                ##get owner profile
                user_profile = UserAccount.objects.filter(user=p.user)
                if user_profile[0].image:
                    profile_image = str(user_profile[0].image)
                else:
                    profile_image = "none"

                if p.active == True:
                    data = {"location":user_profile[0].location,"image":profile_image,"user_id":p.user.id,"user_email":p.user.email,"genre":genre,"liked":liked,"post_id":post_id,"username":p.user.username,"like":likes,"description":p.description,"reposts":repost_count, "file": str(p.post_file),"start":p.start_at,"post_count":posts_count,"reposted":reposted_by_this_user}
                    feed.append(data)


       
        response = JsonResponse({"Response": feed})


    elif request.method == "GET" and request.GET["type"] == "like":
        current_user = User.objects.filter(email=request.GET["email"])
        current_user_account = UserAccount.objects.filter(user=current_user[0])
        if current_user_account[0].image:
            image = str(current_user_account[0].image)
        else:
            image = "none"
        post = Post.objects.filter(id=request.GET["post"])
        ##check if the post is liked
        liked = Like.objects.filter(post=post[0], user=current_user[0]).exists()
        
        if liked == False:
            new_like = Like()
            new_like.post = post[0]
            new_like.user = current_user[0]
            new_like.save()
            # user = User.objects.filter(username=sender)
            tz = pytz.timezone('Africa/Johannesburg')
            time = str(datetime.datetime.now(tz))
            message = {"msg": current_user[0].username+" liked "+ post[0].user.username +"'s post", "profile": image, "post":post[0].id,"post_image":str(post[0].post_file),"useremail":current_user[0].email,"userid":current_user[0].id,"the_receiver":post[0].user.username,"first_name":current_user[0].first_name,"last_name":current_user[0].last_name,"thier_username":current_user[0].username,"date":time}
            fire_config = {
            "apiKey": "AIzaSyDnQA3dMGr6-LK2qoDk7L7Ltvm9W9L6vXE",
            "authDomain": "uploaded-9719b.firebaseapp.com",
            "databaseURL": "https://uploaded-9719b.firebaseio.com",
            "storageBucket": "",
            }
            firebase = pyrebase.initialize_app(fire_config)
            db = firebase.database()
            db.child("notification").push(message)
            notifcation_set = Notifications.objects.get(user=post[0].user)
            ##send notifications if user has allowed it
            # if notifcation_set.pushAll == True and notifcation_set.like == True:
            #     sendNotification(message['msg'], post[0].user.email)
            print("sender email is ")
            sendNotification(message['msg'],request.GET["email"], post[0].id)
        
        else:
            existing_like = Like.objects.filter(post=post[0],user=current_user[0])
            existing_like.delete()
        
        response = JsonResponse({"Response":liked})


    ##get another user's content
    elif request.method == "GET" and request.GET["type"] == "getUser_UD" and request.GET["email"]:
        user_id = request.GET["user_id"]
        ##get the user that's being searched for
        user = User.objects.filter(id=user_id)
        ##
        user_acc = UserAccount.objects.filter(user=user[0])
        ##followers
        followers = Follow.objects.filter(followed=user[0]).count()

        ##
        following = Follow.objects.filter(follower=user_acc[0]).count()

        posts = Post.objects.filter(user=user[0])
        users_posts = Post.objects.filter(user=user[0]).count() 
        post_array = []
        for i in posts:
            #get post likes, comments and views
            views = View.objects.filter(post = i).count()
            likes = Like.objects.filter(post = i).count()
            # comments = Comment.objects.filter(post = i).count();
            post_data = {"post_file":str(i.post_file), "likes": likes, "views":views, "playlisted":i.playlisted}
            post_array.append(post_data)
            print("post", i)

        ##check if the user already follows this individual
        current_user = User.objects.filter(email=request.GET["email"])
        current_user_user_account = UserAccount.objects.filter(user=current_user[0])
        already_following  = Follow.objects.filter(followed=user[0], follower=current_user_user_account[0]).exists()

        if user_acc[0].image and user_acc[0].cover:
            returning_user = [{"location":user_acc[0].location,"website":user_acc[0].website,"id":user[0].id,"already_following":already_following,"first_name":user[0].first_name,"last_name":user[0].last_name,"username":user_acc[0].user.username, "followers":followers,"following":following,"bio":user_acc[0].bio,"cover":str(user_acc[0].cover),"image":str(user_acc[0].image), "total_posts":users_posts}]
        elif user_acc[0].image:
            returning_user = [{"location":user_acc[0].location,"website":user_acc[0].website,"id":user[0].id,"already_following":already_following,"first_name":user[0].first_name,"last_name":user[0].last_name,"username":user_acc[0].user.username, "followers":followers,"following":following,"bio":user_acc[0].bio,"total_posts":users_posts,"image":str(user_acc[0].image)}]
        elif user_acc[0].cover:
            returning_user = [{"location":user_acc[0].location,"website":user_acc[0].website,"id":user[0].id,"already_following":already_following,"first_name":user[0].first_name,"last_name":user[0].last_name,"username":user_acc[0].user.username, "followers":followers,"following":following,"bio":user_acc[0].bio,"total_posts":users_posts,"cover":str(user_acc[0].cover)}]
        else:
            returning_user = [{"location":user_acc[0].location,"website":user_acc[0].website,"id":user[0].id,"already_following":already_following,"first_name":user[0].first_name,"last_name":user[0].last_name,"username":user_acc[0].user.username, "followers":followers,"following":following,"bio":user_acc[0].bio,"total_posts":users_posts}]


        response = JsonResponse({"Response": returning_user,"posts":post_array})

    ##following disabled
    # elif request.method == "GET" and request.GET["type"] == "Follow":
    #     current_user = User.objects.filter(email=request.GET["email"])
    #     current_user_user_account = UserAccount.objects.filter(user=current_user[0])

    #     ##other user
    #     other_user = User.objects.filter(id=request.GET["user_id"])

    #     following_exists = Follow.objects.filter(followed=other_user[0],follower=current_user_user_account[0])
    #     if following_exists.exists():
    #         following = Follow.objects.filter(followed=other_user[0],follower=current_user_user_account[0])
    #         following.delete()
    #     else:
    #         following = Follow()
    #         following.follower = current_user_user_account[0]
    #         following.followed = other_user[0]
    #         following.save()

        
    #         if current_user_user_account[0].image:
    #             image = str(current_user_user_account[0].image)
    #         else:
    #             image = "none"

    #         tz = pytz.timezone('Africa/Johannesburg')
    #         time = str(datetime.datetime.now(tz))
    #         message = {"msg":" Followed you", "profile": image,"useremail":current_user[0].email,"userid":current_user[0].id,"first_name":current_user[0].first_name,"last_name":current_user[0].last_name,"thier_username":current_user[0].username,"date":time}
    #         fire_config = {
    #         "apiKey": "AIzaSyDnQA3dMGr6-LK2qoDk7L7Ltvm9W9L6vXE",
    #         "authDomain": "uploaded-9719b.firebaseapp.com",
    #         "databaseURL": "https://uploaded-9719b.firebaseio.com",
    #         "storageBucket": "",
    #         }
    #         firebase = pyrebase.initialize_app(fire_config)
    #         db = firebase.database()
    #         db.child("notification").push(message)
    #         notifcation_set = Notifications.objects.get(user=other_user[0])
    #         if notifcation_set.pushAll == True and notifcation_set.follow == True:
    #             sendNotification(current_user[0].first_name +" Followed you", other_user[0].email)

    #         ##send notification
    #         # sendNotification(current_user[0].first_name +" Followed you", other_user[0].email)

    #     response = JsonResponse({"Response": following_exists.exists()})

    

    elif request.method == "GET" and request.GET["type"] == "updateNotifications":
        user_id = request.GET["user"]
        notification_info = request.GET["notificationInfo"]
        user = User.objects.filter(id=user_id)
        notification_entry = Notifications.objects.get(user=user[0])
        if notification_info == "allTrue":
            notification_entry.pushAll = True
            notification_entry.like = True
            notification_entry.upload = True
            notification_entry.comment = True
            notification_entry.features = True
            notification_entry.dm = True
            notification_entry.follow  = True
            notification_entry.tag  = True
            notification_entry.repost  = True
            notification_entry.save()
            print("all True")
        elif notification_info == "allFalse":
            notification_entry.pushAll = False
            notification_entry.like = False
            notification_entry.upload = False
            notification_entry.comment = False
            notification_entry.features = False
            notification_entry.dm = False
            notification_entry.follow  = False
            notification_entry.tag  = False
            notification_entry.repost  = False
            notification_entry.save()
            print("all True")

        response = JsonResponse({"Response": "Notification settings updated"})


    elif  request.method == "GET" and request.GET["type"] == "updateIndividualNotifications":
        user_id = request.GET["user"]
        notification_info = request.GET["notificationInfo"]
        user = User.objects.filter(id=user_id)
        notification_entry = Notifications.objects.get(user=user[0])
        notification_value = request.GET["NotificationsValue"]

        print("notification value is  "+str(notification_value))

        if notification_value == "false":
            notification_value = False
        else:
            notification_value = True

        if notification_info == "like":
            notification_entry.like = notification_value
        elif notification_info == "comment":
             notification_entry.comment = notification_value
        elif notification_info == "upload":
             notification_entry.upload = notification_value
        elif notification_info == "follow":
             notification_entry.follow = notification_value
        elif notification_info == "tag":
             notification_entry.tag = notification_value
        elif notification_info == "features":
             notification_entry.features = notification_value
        elif notification_info == "repost":
            notification_entry.repost = notification_value
        elif notification_info == "dm":
            notification_entry.dm = notification_value
        
        notification_entry.save()

        response = JsonResponse({"Response": "Notification settings updated"})

    elif request.method == "GET" and request.GET["type"] == "getNotificationSettings":
        user_id = request.GET["user"]
        user = User.objects.filter(id=user_id)
        notification_entry = Notifications.objects.get(user=user[0])

        response = JsonResponse({"pushAll":notification_entry.pushAll,"like":notification_entry.like, "follow":notification_entry.follow, "dm": notification_entry.dm, "repost":notification_entry.repost,"tag":notification_entry.tag, "comment":notification_entry.comment,"upload":notification_entry.upload,"features":notification_entry.features})

    elif request.method == "GET" and request.GET["type"] == "repost":
        email = request.GET["email"]
        post = request.GET["post"]

        user = User.objects.filter(email=email)
        repost = Post.objects.filter(id=post)
        user_acc = UserAccount.objects.filter(user=user[0])

        if user_acc[0].image:
            image = str(user_acc[0].image)
        else:
            image = "none"

        ##check if repost already exists
        repost_exists = Repost.objects.filter(post=repost[0],user=user[0])
        if repost_exists.exists():
            
            print("Repost already exists")
            reposted_item = Repost.objects.get(post=repost[0],user=user[0])
            reposted_item.delete()
            repost_count = Repost.objects.filter(post=repost[0]).count()
            response = JsonResponse({"Response": repost_count})
        else:
            re_post = Repost()
            re_post.post = repost[0]
            re_post.user = user[0]
            re_post.save()
            repost_count = Repost.objects.filter(post=repost[0]).count()
            tz = pytz.timezone('Africa/Johannesburg')
            time = str(datetime.datetime.now(tz))
            message = {"msg":" reposted a post", "profile": image, "post":repost[0].id,"post_image":str(repost[0].post_file),"useremail":user[0].email,"userid":user[0].id,"the_receiver":repost[0].user.username,"first_name":user[0].first_name, "last_name":user[0].last_name,"thier_username":user[0].username,"date":time }         
            fire_config = {
            "apiKey": "AIzaSyDnQA3dMGr6-LK2qoDk7L7Ltvm9W9L6vXE",
            "authDomain": "uploaded-9719b.firebaseapp.com",
            "databaseURL": "https://uploaded-9719b.firebaseio.com",
            "storageBucket": "",
            }
            firebase = pyrebase.initialize_app(fire_config)
            db = firebase.database()
            db.child("notification").push(message)
            db.child("comments").push({"comment":message['msg'],"post":repost[0].id,"user": user[0].username})
            ##
            notifcation_set = Notifications.objects.get(user=repost[0].user)
            # if notifcation_set.pushAll == True and notifcation_set.repost == True:
            #     sendNotification(message['msg'], repost[0].user.email)
            sendNotification(message['msg'], email)

            # sendNotification(message['msg'], repost[0].user.email)
            print("Repost added")
            

            response = JsonResponse({"Response": repost_count })

    elif request.method == "GET" and request.GET["type"] == "registerDevice":
        email = request.GET["email"]
        user_id = request.GET["userId"]

        print("user toke is ", user_id)
        user = User.objects.get(email=email)
        user_acc = UserAccount.objects.get(user=user)

        user_acc.oneSignalId = user_id
        user_acc.save()

        response = JsonResponse({"Response": "User id saved"})


    elif request.method == "GET" and request.GET["type"] == "deletePost":
        post_id = request.GET["id"]
        post = Post.objects.filter(id=post_id)
        post[0].delete()

        response = JsonResponse({"Response": "Post has been deleted"})


    elif request.method == "GET" and request.GET["type"] == "sendMessageNotif":
        sender = request.GET["sender"]
        to = request.GET["to"]
        message = request.GET["message"]
        to_email = User.objects.filter(username=to)
        custom_message = " sent you a message: "+message



        tz = pytz.timezone('Africa/Johannesburg')
        time = (datetime.datetime.now(tz))
        message = {"msg":custom_message,"userid":user[0].id,"to":to,"first_name":user[0].first_name, "last_name":user[0].last_name,"sender":sender,"date":time  }         
        #message = {"msg":custom_message, "sender": sender, "to":to}         
        fire_config = {
        "apiKey": "AIzaSyDnQA3dMGr6-LK2qoDk7L7Ltvm9W9L6vXE",
        "authDomain": "uploaded-9719b.firebaseapp.com",
        "databaseURL": "https://uploaded-9719b.firebaseio.com",
        "storageBucket": "",
        }
        firebase = pyrebase.initialize_app(fire_config)
        db = firebase.database()
        db.child("notification").push(message)
        notifcation_set = Notifications.objects.get(user=to_email[0])
        # if notifcation_set.pushAll == True and notifcation_set.dm == True:
        #     sendNotification(message['msg'], to_email[0].email)
        sendNotification(custom_message, to_email[0].email)

        response = JsonResponse({"Response": "Message sent"})


    elif request.method == "GET" and request.GET["type"] == "sendCommentNotification":
        # {type: 'sendCommentNotification', post:post_id,sender:sender,message:message}
        sender = request.GET["sender"]
        sender_user = User.objects.get(username=sender)
        post = Post.objects.get(id=request.GET["post"]) 
        to = post.user.email
        sender_user = User.objects.filter(username=sender)
        user = User.objects.filter(username=sender)
        tz = pytz.timezone('Africa/Johannesburg')
        time = str(datetime.datetime.now(tz))
        custom_message = sender_user[0].username+ " commented on "+post.user.username+"'s post: "+request.GET["message"]
        #sender user_acc
        sender_user_acc = UserAccount.objects.get(user=sender_user[0])


        message = {"msg":custom_message,"profile":str(sender_user_acc.image),"post":post.id,"comment_to":post.user.username,"userid":sender_user[0].id,"to":post.user.username,"post_image":str(post.post_file),"first_name":sender_user[0].first_name, "last_name":sender_user[0].last_name,"sender":sender,"date":time }   
        fire_config = {
        "apiKey": "AIzaSyDnQA3dMGr6-LK2qoDk7L7Ltvm9W9L6vXE",
        "authDomain": "uploaded-9719b.firebaseapp.com",
        "databaseURL": "https://uploaded-9719b.firebaseio.com",
        "storageBucket": "",
        }
        firebase = pyrebase.initialize_app(fire_config)
        db = firebase.database()
        db.child("notification").push(message)
        notifcation_set = Notifications.objects.get(user=post.user)
        if sender != post.user.username:
            #  if notifcation_set.pushAll == True and notifcation_set.comment == True:
            #     sendNotification(custom_message, to) 
            sendNotification(custom_message,sender_user.email,post.id)  
        else:
            print("can't send notification to owner")

        response = JsonResponse({"Response": "Message sent"})    



    elif request.method == "GET" and request.GET["type"] == "getUserFeed":
        user = User.objects.filter(username=request.GET["username"])
        current_user = User.objects.filter(email=request.GET["email"])
        current_user_user_account = UserAccount.objects.filter(user=current_user[0])
        feed = []
        sleep(0.2)
        post = Post.objects.filter(user=user[0])
        # print("following", followers)
        
        for p in post:
            post_id = p.id
            genre= p.genre
            likes = Like.objects.filter(post=p).count()
            repost_count = Repost.objects.filter(post=p).count()
            ##check if the post is liked
            liked = Like.objects.filter(post=p, user=current_user[0]).count()
            reposted_by_this_user = Repost.objects.filter(post=p,user=current_user[0]).count()
            # comments = Comment.objects.filter(post=p).count()
            views = View.objects.filter(post=p).count()

            ##get owner profile
            user_profile = UserAccount.objects.filter(user=p.user)
            if user_profile[0].image:
                profile_image = str(user_profile[0].image)
            else:
                profile_image = "none"

            if p.active == True:
                data = {"image":profile_image,"user_id":p.user.id,"user_email":p.user.email,"genre":genre,"liked":liked,"post_id":post_id,"username":p.user.username,"like":likes,"description":p.description,"reposts":repost_count, "file": str(p.post_file),"start":p.start_at,"reposted":reposted_by_this_user}
                feed.append(data)
       
        response = JsonResponse({"Response": feed})


    elif request.method == "GET" and request.GET["type"] == "getDuration":
        post = Post.objects.get(id=request.GET["post"])
        duration = post.start_at
        current_playing_vid = Post.objects.get(user=post.user,current_feed_play=True)
        previous_play_post = request.GET["post"]
        user_name = post.user.username
        response = JsonResponse({"Response": [duration,current_playing_vid.id,user_name,previous_play_post]})


    elif request.method == "GET" and request.GET["type"] == "resetPost":
        post = Post.objects.get(id=request.GET["post"])
        post.start_at = 0
        post.save()

        response = JsonResponse({"Response": "Reset successfull"})

    elif request.method == "GET" and request.GET["type"] == "getTags":
        username = request.GET["username"]
        returning_users = []
        if username == "@":
            user_list = User.objects.all()[:10]
            for u in user_list:
                print(u)
                print(user_list)
                user = {"username":u.username}
                returning_users.append(user)
        
        response = JsonResponse({"users": returning_users})


    elif request.method == "GET" and request.GET["type"] == "notification_post":
        notification_id = request.GET["id"]
        onesignal_client = onesignal_sdk.Client(app_auth_key="ODM2NDQ4MTQtYzNiZC00MDA4LWI3YTQtYmZiZGY0ZjhjOGJl", app_id="213117e1-5258-44df-9de4-7206c18669b9")
        onesignal_response = onesignal_client.view_notification(notification_id)
        print(onesignal_response.json()["data"]["post_id"])
        post = Post.objects.get(id=int(onesignal_response.json()["data"]["post_id"]))
        response = JsonResponse({"Response": post.user.username})
            


    elif request.method == "GET" and request.GET["type"] == "getFollowing":
        user = User.objects.get(username=request.GET["username"])
        user_acc = UserAccount.objects.get(user=user)
        following = Follow.objects.filter(follower=user_acc)
        followers = Follow.objects.filter(followed=user)
        following_array = []
        for fs in followers:
            data = {"id":fs.follower.user.id,"email":fs.follower.user.email,"username":fs.follower.user.username,"follower":True,"profile_image":str(fs.follower.image),"first_name":fs.follower.user.first_name,"last_name":fs.follower.user.last_name }
            following_array.append(data)

        for fr in following:
            following_user_acc = UserAccount.objects.get(user=fr.followed)
            data = {"id":following_user_acc.user.id,"email":following_user_acc.user.email,"username":following_user_acc.user.username,"follower":False,"profile_image":str(following_user_acc.image),"first_name":following_user_acc.user.first_name,"last_name":following_user_acc.user.last_name }
            following_array.append(data)

        response = JsonResponse({"Response": following_array})



    if request.method == "POST" and request.POST["type"] == "upload":
        email = request.POST["email"]
        # _file = request.FILES["file"]
        _file = request.POST["file"]
        description = request.POST["description"]
        genre = request.POST["genre"]
        playlisted = request.POST["playlisted"]
        publish_date = request.POST["publish"]
        video_duration = request.POST["duration"]
        tags = request.POST["tags"]
        user = User.objects.get(email=email)
        
        print("uploading playlist by", email)

        ##true
        if playlisted == 'true':
            playlisted = True
        else:
            playlisted = False

        new_post = Post()
        new_post.user = user
        new_post.description = description
        new_post.playlisted = playlisted
        new_post.post_file = _file
        new_post.genre = genre
        new_post.scheduled_for  =  publish_date
        new_post.video_length = video_duration
        new_post.save()

        print(tags)
        for t in tags:
            if t != ",":
                tagged_user = User.objects.get(id=t)
                mess = " tagged you in their latest upload 🏷️🏷️"
                follower = tagged_user.email
                sender_user_acc = UserAccount.objects.get(user=user)
                ##notifications
                tz = pytz.timezone('Africa/Johannesburg')
                time = str(datetime.datetime.now(tz))
                message = {"msg":mess,"profile":str(sender_user_acc.image),"post":new_post.id,"comment_to":new_post.user.username,"userid":sender_user_acc.user.id,"to":tagged_user.username,"post_image":str(new_post.post_file),"first_name":sender_user_acc.user.first_name, "last_name":sender_user_acc.user.last_name,"sender":sender_user_acc.user.username,"date":time }   
                fire_config = {
                "apiKey": "AIzaSyDnQA3dMGr6-LK2qoDk7L7Ltvm9W9L6vXE",
                "authDomain": "uploaded-9719b.firebaseapp.com",
                "databaseURL": "https://uploaded-9719b.firebaseio.com",
                "storageBucket": "",
                }
                firebase = pyrebase.initialize_app(fire_config)
                db = firebase.database()
                db.child("notification").push(message)
                notifcation_set = Notifications.objects.get(user=tagged_user)
                if sender != post.user.username:
                    # if notifcation_set.pushAll == True and notifcation_set.upload == True:
                    #     sendNotification(mess, follower) 
                    sendNotification(custom_message, to)  
                
                # sendNotification(mess, follower) 
                new_tag = Tag()
                new_tag.post = new_post
                new_tag.taged_user = tagged_user
                new_tag.save()

        response = JsonResponse({"newly created post_id": new_post.id})
    
    elif request.method == "POST" and request.POST["type"] == "updateProfile":
        first_name = request.POST["first_name"]
        user_name = request.POST["user_name"]
        location = request.POST["location"]
        website = request.POST["website"]
        bio = request.POST["bio"]
        email = request.POST["email"]
        print("user detail ",first_name,user_name,location,website,bio,email)
        if 'file' not in request.FILES:
            _file = ""
            print("files not set")
        else:
            _file = request.FILES["file"]
            print("files set")

        
        user = User.objects.get(email=email)
        print("selected user ", user.id)
        user.first_name = first_name
        user.username= user_name
        user.save()

        user_account = UserAccount.objects.get(user=user)
        if 'file' not in request.FILES:
            print("no file to save")
            user_account.location = location
            user_account.website = website
            user_account.bio = bio
            user_account.save()
        else:
            user_account.image = _file
            user_account.location = location
            user_account.website = website
            user_account.bio = bio
            user_account.save()

        response = JsonResponse({"Response": "Updated"})

    elif request.method == "POST" and request.POST["type"] == "uploadCover":
        _file = request.FILES["file"]
        user = User.objects.get(email=request.POST["email"])
        user_acc = UserAccount.objects.get(user=user)

        user_acc.cover = _file
        user_acc.save()
        response = JsonResponse({"Response": str(user_acc.cover)})


    elif request.method == "POST" and request.POST["type"] == "uploadCroppedCover":
        _file = request.FILES["file"]
        user = User.objects.get(email=request.POST["email"])
        user_acc = UserAccount.objects.get(user=user)

        user_acc.cover = _file
        user_acc.save()
            
        response = JsonResponse({"Response": str(user_acc.cover)})
    
    elif request.method == "POST" and request.POST["type"] == "chatFileUpload":
        _file = request.FILES["file"]
        file_name = request.POST["id"]

        new_file = ChatFiles()
        new_file.file_name = file_name
        new_file.post_file = _file
        new_file.save()
        response = JsonResponse({"Response": str(new_file.post_file)})


    elif request.method == "POST" and request.POST["type"] == "testSignUp":
        username = request.POST["username"]
        email = request.POST["email"]
        mobile = request.POST["mobile"]
        password =  "#ABaTestUser"
        new_user = User()
        new_user.username = username
        new_user.first_name = username
        new_user.email = email
        new_user.set_password(password)
        new_user.save()

        print(username)
        print(email)
        message = Mail(
        from_email='info@uploadedstream.com',
        to_emails=email,
        subject='Uploaded Account Password',
        html_content='<strong>Your Uploaded password is: #ABaTestUser, Please wait for 1 - 2 hours before the app is made available to you</strong>')

        message_2 = Mail(
        from_email='info@uploadedstream.com',
        to_emails='info@uploadedstream.com',
        subject='Uploaded Account - New Sign Up',
        html_content="<strong>A new user has signed up, their email is as follows: "+email+". Their mobile number is: "+ mobile+"</strong>")
        sg = SendGridAPIClient('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')
        response = sg.send(message_2)
        print(response.status_code)
        print(response.body)
        print(response.headers)

        response = JsonResponse({"Message":"Sign up successful"})

    elif request.method == "GET" and request.GET["type"] == "report":
        post_id = request.GET["post"]
        post_report_subject = request.GET["subject"]
        message_2 = Mail(
        from_email='info@uploadedstream.com',
        to_emails='info@uploadedstream.com',
        subject='Uploaded Account - A post has been reported',
        html_content="<strong>A user has reported a post on Uploaded, post ID is"+ post_id +", reason for reporting:"+ post_report_subject+"</strong>")
        sg = SendGridAPIClient('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')
        response = sg.send(message_2)

        response = JsonResponse({"Report":"post no."+post_id+" has been reported"})



        
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Headers"] = "*"
    return response

        





##notifications
def sendNotification(msg,user_email,post_id):
    # user = User.objects.filter(email=user_email)
    # user_acc = UserAccount.objects.filter(user=user[0])
    # player_id = user_acc[0].oneSignalId 
    # print("player id is ", player_id)

    ## send push to all users
    all_users = User.objects.all()
    current_user = User.objects.get(email=user_email)
    for u in all_users:
        if u != current_user:
            if UserAccount.objects.filter(user=u).exists():
                u_acc = UserAccount.objects.get(user=u)

                # create a onesignal client
                onesignal_client = onesignal_sdk.Client(app_auth_key="ODM2NDQ4MTQtYzNiZC00MDA4LWI3YTQtYmZiZGY0ZjhjOGJl", app_id="213117e1-5258-44df-9de4-7206c18669b9")

                # create a notification
                new_notification = onesignal_sdk.Notification(post_body={
                    "contents": {"en": msg, "tr": "Mesaj"},
                    # "included_segments": ["Active Users","Subscribed Users","Engaged Users"],
                    "include_player_ids": [u_acc.oneSignalId],
                    # "filters": [{"field": "tag", "key": "level", "relation": "=", "value": "10"}]
                })

                # add post body
                new_notification.post_body["data"] = {"post_id": post_id}

                # send notification, it will return a response
                onesignal_response = onesignal_client.send_notification(new_notification)
                print(onesignal_response.status_code)
                print(onesignal_response.json())
 
    # all_user_accounts = UserAccount.objects.all()
    # for u in all_user_accounts:
    #     # ##send emails
    #     # message_2 = Mail(
    #     # from_email='info@uploadedstream.com',
    #     # to_emails=u.user.email,
    #     # subject='Uploaded Account - New Sign Up',
    #     # html_content="<strong>"+msg+"</strong>")
    #     # sg = SendGridAPIClient('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')
    #     # sg.send(message_2)

    #     print("user id is "+u.oneSignalId)
    #     # Init the client
    #     os_app_id = "213117e1-5258-44df-9de4-7206c18669b9"
    #     os_apikey = "ODM2NDQ4MTQtYzNiZC00MDA4LWI3YTQtYmZiZGY0ZjhjOGJl"

    #     header = {"Content-Type": "application/json; charset=utf-8"}

    #     payload = {"app_id": os_app_id,"include_player_ids": [u.oneSignalId],"contents": {"en": msg} }
        
    #     req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
        
    #     print(req.status_code, req.reason)

    # # Init the client
    # os_app_id = "213117e1-5258-44df-9de4-7206c18669b9"
    # os_apikey = "ODM2NDQ4MTQtYzNiZC00MDA4LWI3YTQtYmZiZGY0ZjhjOGJl"

    # header = {"Content-Type": "application/json; charset=utf-8"}

    # payload = {"app_id": os_app_id,"include_player_ids": [player_id],"contents": {"en": msg} }
    
    # req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
    
    # print(req.status_code, req.reason)

    
def index(request):
    home_page = template_url = "authentication/index.html"
    return render(request, template_url)

def app(request):
    template_url = "authentication/app-main.html"
    return render(request, template_url)

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer