from django.contrib import admin
from .models import UserAccount
# Register your models here.

class userAccountAdmin(admin.ModelAdmin):
    list_display = ['user','mobile','oneSignalId']

admin.site.register(UserAccount, userAccountAdmin)

admin.site.site_header = "Uploaded Admin Panel"
admin.site.site_title = "Admin Panel"