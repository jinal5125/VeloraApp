
from django.contrib import admin
from django.urls import path,include
from myapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('home/', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('reels/', views.reels, name='reels'),
    path('messages/', views.messages, name='messages'),
    path('messages/<int:pk>', views.messages, name='messages'),
    path('notifications/',  views.notifications, name='notifications'),
    path('create/', views.create, name='create'),
    path('create_story/', views.create_story, name='create_story'),
    path('view_story/<int:pk>/', views.view_story, name='view_story'),
    path('create_reel/', views.create_reel, name='create_reel'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('following/', views.following, name='following'),
    path('follow_unfollow/<int:pk>', views.follow_unfollow, name='follow_unfollow'),
    path('followers/', views.followers, name='followers'),
    path('remove_followers/<int:pk>', views.remove_followers, name='remove_followers'),
    path('like_unlike_post/<int:pk>',views.like_unlike_post,name='like_unlike_post'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('reset_password/',views.reset_password,name='reset_password'),
    path('otp_verification/',views.otp_verification,name='otp_verification'),
    path('user_profile/<int:pk>',views.user_profile,name='user_profile'),
    path('user_following/<int:pk>',views.user_following,name='user_following'),
    path('user_followers/<int:pk>',views.user_followers,name='user_followers'),
    path('send_message/<int:pk>',views.send_message,name='send_message'),
    path('comments/<int:pk>/',views.comments,name='comments'),
    path('reel_comments/<int:pk>/',views.comments, {'media_type': 'reel'}, name='reel_comments'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)