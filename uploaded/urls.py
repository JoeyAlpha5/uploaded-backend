"""uploaded URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from authentication import views
from app import views as appviews
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register(r'groups',views.GroupViewSet)
router.register(r'posts',appviews.PostViewSet)
router.register(r'likes',appviews.LikeViewSet)
router.register(r'views',appviews.ViewViewSet)
# router.register(r'comments',appviews.CommentViewSet)
router.register(r'follows',appviews.FollowViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('authentication.urls')),
    path('', include('authentication.urls')),
    path('uploaded/', include('authentication.urls')),
    path('api-auth/',include('rest_framework.urls',namespace='rest_framework'))
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
