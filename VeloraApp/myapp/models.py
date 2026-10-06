from django.db import models
import math
from django.utils import timezone
from datetime import timedelta


class instrauser(models.Model):
    gender_choices = (
        ('male','Male'),
        ('female','Female'),
    )
    username = models.CharField(max_length=100,unique=True)
    email = models.EmailField(unique=True,null=True,blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    profile_pic = models.FileField(upload_to='profile_pics/', blank=True, null=True,default='images/default_avatar.png')
    gender = models.CharField(max_length=10,choices=gender_choices,blank=True, null=True)
    fullname = models.CharField(max_length=100,blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    otp = models.PositiveBigIntegerField(default=456)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class instrapost(models.Model):
    user = models.ForeignKey(instrauser, on_delete=models.CASCADE)
    image = models.FileField(upload_to='posts/')
    caption = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    tagged_users = models.ManyToManyField(instrauser,related_name="tagged_users", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.caption
    
    def whenpublished(self):
        now = timezone.now()
        diff = now-self.created_at

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds

            if seconds == 1:
                return str(seconds) + "second ago"
            else:
                return str(seconds) + " seconds ago"
            
        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600 :
            minutes = math.floor(diff.seconds/60)
             
            if minutes == 1:
                return str(minutes) + " minute ago"
            
            else:
                return str(minutes) + " minutes ago"
            
        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400 :
            hours = math.floor(diff.seconds/3600)

            if hours == 1:
                return str(hours) + " hour ago"
            else:
                return str(hours) + " hours ago"
            
        if diff.days >= 1 and diff.days < 30:
            days = diff.days

            if days == 1:
                return str(days) + " day ago"
            else:
                return str(days) + " days ago"
            
        if diff.days >= 30 and diff.days < 365:
            months = math.floor(diff.days/30)

            if months == 1:
                return str(months) + " month ago" 
            else:
                return str(months) + " months ago"
            
        if diff.days >= 365:
            years = math.floor(diff.days/365)

            if years == 1:
                return str(years) + " year ago"
            
            else:
                return str(years) + " years ago"


class followusers(models.Model):
    following = models.ForeignKey(instrauser, on_delete=models.CASCADE,related_name="following")
    following_person = models.ForeignKey(instrauser,on_delete=models.CASCADE,related_name="following_person")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.following.fullname} - following {self.following_person.username}"
    

class notification(models.Model):
    notification_type = (
        ('follow','follow'),
        ('like','like'),
        ('comment','comment'),
    )

    sender = models.ForeignKey(instrauser, on_delete=models.CASCADE,related_name="sender_notification")
    reciver = models.ForeignKey(instrauser, on_delete=models.CASCADE,related_name="reciver_notification")
    post_fk = models.ForeignKey(instrapost, on_delete=models.CASCADE,null=True,blank=True)
    reel_fk = models.ForeignKey('instrareels', on_delete=models.CASCADE,null=True,blank=True)
    message = models.CharField(max_length=40)
    notification_type = models.CharField(max_length=20,choices=notification_type)
    read_status = models.CharField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} {self.message} {self.reciver.username}"

    def whenpublished(self):
        now = timezone.now()
        diff = now-self.created_at

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds

            if seconds == 1:
                return str(seconds) + "second ago"
            else:
                return str(seconds) + " seconds ago"
            
        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600 :
            minutes = math.floor(diff.seconds/60)
             
            if minutes == 1:
                return str(minutes) + " minute ago"
            
            else:
                return str(minutes) + " minutes ago"
            
        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400 :
            hours = math.floor(diff.seconds/3600)

            if hours == 1:
                return str(hours) + " hour ago"
            else:
                return str(hours) + " hours ago"
            
        if diff.days >= 1 and diff.days < 30:
            days = diff.days

            if days == 1:
                return str(days) + " day ago"
            else:
                return str(days) + " days ago"
            
        if diff.days >= 30 and diff.days < 365:
            months = math.floor(diff.days/30)

            if months == 1:
                return str(months) + " month ago" 
            else:
                return str(months) + " months ago"
            
        if diff.days >= 365:
            years = math.floor(diff.days/365)

            if years == 1:
                return str(years) + " year ago"
            
            else:
                return str(years) + " years ago"


class like_unlike(models.Model):
    user_fk = models.ForeignKey(instrauser, on_delete=models.CASCADE,related_name="liked_by")
    post_fk = models.ForeignKey(instrapost, on_delete=models.CASCADE,related_name="like_post",null=True, blank=True)
    reel_fk = models.ForeignKey("instrareels", on_delete=models.CASCADE, related_name="like_reel",null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user_fk','post_fk','reel_fk']

    def __str__(self):
        if self.post_fk:
            return f"{self.user_fk.username} liked post: {self.post_fk.caption}"
        elif self.reel_fk:
            return f"{self.user_fk.username} liked reel: {self.reel_fk.caption}"
    
class instrareels(models.Model):
    user = models.ForeignKey(instrauser, on_delete=models.CASCADE)
    video = models.FileField(upload_to='instrareels/')
    caption = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.caption
    
    def whenpublished(self):
        now = timezone.now()
        diff = now-self.created_at

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds

            if seconds == 1:
                return str(seconds) + "second ago"
            else:
                return str(seconds) + " seconds ago"
            
        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600 :
            minutes = math.floor(diff.seconds/60)
             
            if minutes == 1:
                return str(minutes) + " minute ago"
            
            else:
                return str(minutes) + " minutes ago"
            
        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400 :
            hours = math.floor(diff.seconds/3600)

            if hours == 1:
                return str(hours) + " hour ago"
            else:
                return str(hours) + " hours ago"
            
        if diff.days >= 1 and diff.days < 30:
            days = diff.days

            if days == 1:
                return str(days) + " day ago"
            else:
                return str(days) + " days ago"
            
        if diff.days >= 30 and diff.days < 365:
            months = math.floor(diff.days/30)

            if months == 1:
                return str(months) + " month ago" 
            else:
                return str(months) + " months ago"
            
        if diff.days >= 365:
            years = math.floor(diff.days/365)

            if years == 1:
                return str(years) + " year ago"
            
            else:
                return str(years) + " years ago"


class instrastory(models.Model):
    user = models.ForeignKey(instrauser,on_delete=models.CASCADE,related_name="story_by")
    image = models.FileField(upload_to="instrastory/")
    caption = models.CharField(blank=True,null=True)
    music = models.FileField(upload_to="instramusic/",blank=True,null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()

    is_expired = models.BooleanField(null=True,blank=True,default=False)

    def save(self, *args,**kwargs):
        if not self.expired_at:
            self.expired_at = timezone.now() + timedelta(hours=24)
        return super().save(*args,**kwargs)
    
    def is_expired(self):
        if self.expired_at > timezone.now():
            self.is_expired = True

class chatroom(models.Model):
    user1 = models.ForeignKey(instrauser,on_delete=models.CASCADE,related_name='user_1_chat')
    user2 = models.ForeignKey(instrauser,on_delete=models.CASCADE,related_name='user_2_chat')

    created_at = models.DateTimeField(auto_now_add=True)

    
class all_messages(models.Model):
    chat_room = models.ForeignKey(chatroom,on_delete=models.CASCADE,related_name='chatroom')
    sender_id = models.ForeignKey(instrauser,on_delete=models.CASCADE,related_name='senderby',blank=True,null=True)
    text_message = models.CharField(max_length=100)
    image = models.FileField(null=True,blank=True)
    video = models.FileField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class add_comments(models.Model):
    user_fk = models.ForeignKey(instrauser,on_delete=models.CASCADE)
    post_fk = models.ForeignKey(instrapost,on_delete=models.CASCADE,null=True,blank=True)
    reel_fk = models.ForeignKey(instrareels,on_delete=models.CASCADE,null=True,blank=True)

    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

