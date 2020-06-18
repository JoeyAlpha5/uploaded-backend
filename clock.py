# # from django_cron import CronJobBase, Schedule
# from apscheduler.schedulers.blocking import BlockingScheduler
# import os
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uploaded.settings')
# import django
# django.setup()
# from app.models import Post, Follow
# from authentication.models import UserAccount
# from django.contrib.auth.models import User
# from datetime import date
# from datetime import date
# import datetime
# import requests
# import json
# import pytz


# # If you want all scheduled jobs to use this store by default,
# # use the name 'default' instead of 'djangojobstore'.
# sched = BlockingScheduler()
# @sched.scheduled_job('interval', seconds=1)
# def timed_job():
#     print("Cron is running every second")
#     all_videos = Post.objects.all()
#     for v in all_videos:
#         current_seconds = float(v.start_at)
#         video_duration = float(v.video_length)
#         video_playing = v.current_feed_play 
#         video_active = v.active
#         if video_duration < current_seconds and video_playing == True and video_active == True or video_duration == current_seconds and video_playing == True and video_active == True:
#             #reset video time
#             v.start_at = 0
#             v.save()
#             #set next playing video on user's feed
#             the_min_post = Post.objects.filter(user=v.user)           
#             posts_array = []
#             for p in the_min_post:
#                 post_id = p.id
#                 posts_array.append(post_id)
#                 posts_array.sort()
#             print("all post arrays "+str(posts_array))

#             get_min = min(posts_array)
#             print("min post "+str(get_min))
#             for x in posts_array:
#                 x_post = Post.objects.get(id=x)
#                 if x_post.current_feed_play == True:
#                     # posts_array.remove(x)
#                     x_post.current_feed_play = False
#                     x_post.save()
#                     ##
#                     current_index = posts_array.index(x)
#                     # posts_array = posts_array[current_index+1:]
#                     print("next posts for user: "+x_post.user.username+" post array length "+str(len(posts_array[current_index+1:])))
#                     if len(posts_array[current_index+1:]) == 0:
#                         posts_array = posts_array
#                     else:
#                         posts_array = posts_array[current_index+1:]
#                     print("posts array length "+str(len(posts_array)))
#                     nex_min = min(posts_array)
#                     print("new min "+str(nex_min))
#                     nex_min_post = Post.objects.get(id=nex_min)
#                     print(nex_min_post.current_feed_play)
#                     nex_min_post.current_feed_play = True
#                     nex_min_post.start_at = 0
#                     nex_min_post.save()
#                     #if video is playing for first time
#                     if nex_min_post.first_play  == True:
#                         nex_min_post.first_play = False
#                         nex_min_post.save()
#                         followers = Follow.objects.filter(followed=nex_min_post.user)
#                         for x in followers:
#                             follower = x.follower.user.email
#                             custom_message = nex_min_post.description+" Now Streaming ⚡"
#                             sendNotification(custom_message, follower) 
#                         print(new_post.id)
#                     return

#         else:
#             tz = pytz.timezone('Africa/Johannesburg')
#             today = date.today()
#             time = datetime.datetime.now(tz).time()
#             time_h = str(time.hour)+":"+str(time.minute)
#             date_d = str(today.day)+"/"+str(today.month)+"/"
#             d2 = str(date_d+time_h)
#             saved_date = v. scheduled_for
#             print("date is ", saved_date)
#             print("today date ", d2)
#             if saved_date != "":
#                 datetime_object = datetime.datetime.strptime(saved_date, '%d/%m/%H:%M')
#                 if datetime_object.day == today.day and datetime_object.month == today.month and datetime_object.minute < time.minute and datetime_object.hour <= time.hour:
#                     v.active = True
#                     v.scheduled_for = ""
#                     v.save()
#                     print("published post")
#                     followers = Follow.objects.filter(followed=v.user)
#                     for x in followers:
#                         follower = x.follower.user.email
#                         custom_message = x.followed.user.username+" Scheduled a new video to their channel"
#                         sendNotification(custom_message, follower) 
#                     print(new_post.id)

            
#             if video_playing == True and video_active == True:
#                 if video_duration < current_seconds or video_duration == current_seconds:
#                     v.start_at = 0
#                     v.save() 
#                 else:
#                     increment = current_seconds + 1
#                     v.start_at = increment
#                     v.save()
#                     print("cron job running "+str(increment)+" "+str(v.start_at))
#             else:
#                 v.start_at = 0
#                 v.save()


# ##notifications
# def sendNotification(msg,user_email):
#     user = User.objects.filter(email=user_email)
#     user_acc = UserAccount.objects.filter(user=user[0])
#     player_id = user_acc[0].oneSignalId 
#     print("player id is ", player_id)
#     # Init the client
#     os_app_id = "213117e1-5258-44df-9de4-7206c18669b9"
#     os_apikey = "ODM2NDQ4MTQtYzNiZC00MDA4LWI3YTQtYmZiZGY0ZjhjOGJl"

#     header = {"Content-Type": "application/json; charset=utf-8"}

#     payload = {"app_id": os_app_id,"include_player_ids": [player_id],"contents": {"en": msg} }
    
#     req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
    
#     print(req.status_code, req.reason)


# #set the current play for the user feed
# # @sched.scheduled_job('interval', seconds=1)
# # def timed_feed():
# #     users = User.objects.all()
# #     for u in users:
# #         users_posts = Post.objects.filter(user=u)
# #         total_video_length = 0
# #         id_ = []
# #         for p in users_posts:
# #             post_id = p.id
# #             id_.append(post_id)
# #             post_duration = total_video_length + float(p.video_length)

# #         min_id = min(id_)
# #         min_post = Post.objects.get(id=min_id)
# #         min_post.current_feed_play = True
# #         min_post.save()

# #         for post_id in id_:
# #             if post_id != min_id:
# #                 post_to_disable = Post.objects.get(id=post_id)
# #                 post_to_disable.current_feed_play = False
# #                 post_to_disable.save()
# #         print("lowest "+ str(min_id))
# #         print("total video length for "+ u.username+ " "+ str(post_duration)+" "+str(id_))
            




# sched.start()