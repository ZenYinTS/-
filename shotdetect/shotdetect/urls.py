"""shotdetect URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from detect import views as dViews
from detect.video import videoViews as vViews
from detect.series import seriesViews as sViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dViews.index),
    path('search/',dViews.search),
    path('search/show/',dViews.showResult),
    path('login/',dViews.login),
    path('manage/', vViews.manage),
    path('videoManage/', vViews.videoManageList),
    path('videoManage/add', vViews.videoAdd),
    path('videoAdd/', vViews.addVideo),
    path('videoManage/uploadVideo/', vViews.uploadVideo),
    path('videoManage/list/', vViews.videoManageList),
    path('videoManage/edit/', vViews.videoEdit),
    path('videoEdit/', vViews.editVideo),
    path('videoManage/remove/', vViews.deleteVideo),
    path('videoManage/search/', vViews.searchVideo),
    path('seriesManage/', sViews.seriesManageList),
    path('seriesManage/add', sViews.seriesAdd),
    path('seriesAdd/', sViews.addSeries),
    path('seriesManage/list/', sViews.seriesManageList),
    path('seriesManage/edit/', sViews.seriesEdit),
    path('seriesEdit/', sViews.editSeries),
    path('seriesManage/remove/', sViews.deleteSeries),
    path('seriesManage/search/', sViews.searchSeries),

]
