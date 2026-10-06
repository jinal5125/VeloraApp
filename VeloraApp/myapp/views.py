from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from .models import *
from django.contrib.auth.hashers import make_password,check_password
from django.db.models import Q
from django.utils import timezone
from .utils import customesendmail,get_or_create_chatroom
import random


def checklogin(view_function):
    def wrapper(request,*args,**kwargs):
        if "email" in request.session:
            try:
                uid = instrauser.objects.get(email = request.session['email'])
                request.uid = uid
                return view_function(request,*args,**kwargs)
            except instrauser.DoesNotExist:
                return redirect("login")
        return redirect("login")
    return wrapper

def login(request):
    if request.POST:
        email = request.POST['email']
        password =request.POST['password']

        try:
            uid = instrauser.objects.get(email = email)
            if not check_password(password,uid.password):
                context = {
                    'e_msg' : "Invalid Credentials !"
                }
                return render(request,"myapp/login.html",context)
            else:
                request.session['email'] = email 
                context = {
                     'uid' : uid 
                }
                return redirect("home")

        except: 
            context = {
                'e_msg' : "User Not Found !"
            }
            return render(request,"myapp/login.html",context)

    return render(request,'myapp/login.html')

def register(request):
    if request.POST:
        username = request.POST['username']
        email = request.POST['email']
        gender = request.POST['gender']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if instrauser.objects.filter(username=username).exists():
            context = {
                'e_msg' : "Username Already exists !"
            }
            return render(request,"myapp/register.html",context)

        elif instrauser.objects.filter(email = email).exists():
            context = {
                'e_msg' : "Email Already exists !"
            }
            return render(request,"myapp/register.html",context)

        elif password!= confirm_password:
            context = {
                'e_msg': "Password does not match !"
            }
            return render(request,"myapp/register.html",context)

        else:
            img = None

            gender_lower = gender.lower()
            if gender_lower == "male":
                img = "images/boy.png"
            elif gender_lower == "female":
                img = "images/girl.png"

            instrauser.objects.create(
                    username = username,
                    email = email,
                    password = make_password(password),
                    profile_pic = img,
                    gender = gender
                    )
                    
            return redirect("login")

    return render(request,"myapp/register.html")


def logout(request):
    if "email" in request.session:
        del request.session['email']
        return redirect("login")
    return redirect("login")

@checklogin   
def edit_profile(request):
    uid = request.uid   

    if request.POST:
        uid.fullname = request.POST['fullname']
        uid.username = request.POST['username']
        uid.bio = request.POST['bio']
        uid.description = request.POST['description']
        uid.link = request.POST['link']

        if 'profile_pic' in request.FILES:
            uid.profile_pic = request.FILES['profile_pic']

        uid.save()
        return redirect("profile")
    
    context = {
        'uid': uid,
    }
    return render(request, "myapp/edit_profile.html", context)

@checklogin 
# create post 
def create(request):
    uid = request.uid

    if request.POST:
        image = request.FILES['image']
        caption = request.POST['caption']
        location = request.POST['location']

        instrapost.objects.create(
            user=uid,
            image=image,
            caption=caption,
            location=location
        )

        return redirect("home")

    context = {
        'uid': uid,
    }
    return render(request, "myapp/create.html", context)

@checklogin 
def create_story(request):
    uid = request.uid

    if request.POST:
        image = request.FILES['image']
        caption = request.POST['caption']


        istory = instrastory.objects.create(
            user = uid,
            image = image,
            caption = caption
        )

        if "music" in request.FILES:
            istory.music = request.FILES['music']

        istory.save()

        #return redirect("home")

    context = {
        'uid': uid,
    }
    return render(request, "myapp/create_story.html", context)



@checklogin
def home(request):
    uid = request.uid   
    
    count_followers = followusers.objects.filter(following_person = uid).count()
    count_following  = followusers.objects.filter(following = uid).count()
    count_post = instrapost.objects.filter(user = uid).count()

    my_following_users = followusers.objects.filter(following = uid).values_list("following_person",flat=True)

    post_all = instrapost.objects.filter(user__in = list(my_following_users))

    liked_posts = like_unlike.objects.filter(user_fk=uid).values_list('post_fk_id', flat=True)

    my_following = followusers.objects.filter(following=uid).values_list("following_person_id", flat=True)
    suggested_users = instrauser.objects.exclude(id__in=list(my_following) + [uid.id])

    users = list(my_following_users)

    my_story = instrastory.objects.filter(
        user=uid,
        expired_at__gt=timezone.now()
    ).exists()

    # Get all active stories for followed users
    story_all_query = instrastory.objects.filter(
        user__in=users,
        expired_at__gt=timezone.now()
    ).order_by('-created_at')

    # Group stories by user to show only one circle per person
    unique_stories = []
    seen_users = set()
    for s in story_all_query:
        if s.user.id not in seen_users:
            unique_stories.append(s)
            seen_users.add(s.user.id)
    story_all = unique_stories

    # Ensure viewed_stories are integers for reliable comparison
    viewed_stories = [int(sid) for sid in request.session.get('viewed_stories', [])]

    context = {
        'uid': uid,
        'post_all': post_all,
        'my_following_users': my_following_users,
        'liked_posts': liked_posts,
        'suggested_users': suggested_users,
        'count_followers': count_followers,
        'count_following': count_following,
        'count_post': count_post,
        'story_all': story_all,
        'my_story': my_story,   
        'viewed_stories': viewed_stories,
    }
    return render(request, "myapp/home.html", context)

@checklogin
def view_story(request, pk):
    uid = request.uid
    target_user = instrauser.objects.get(id=pk)
    
    stories = instrastory.objects.filter(
        user=target_user,
        expired_at__gt=timezone.now()
    ).order_by('created_at')

    if not stories.exists():
        return redirect('home')

    viewed_stories = request.session.get('viewed_stories', [])
    if target_user.id not in viewed_stories:
        viewed_stories.append(target_user.id)
        request.session['viewed_stories'] = viewed_stories

    context = {
        'uid': uid,
        'target_user': target_user,
        'stories': stories,
    }
    return render(request, "myapp/view_story.html", context)


@checklogin
def user_profile(request,pk):
    uid = request.uid

    target_user = instrauser.objects.get(id=pk)

    posts = instrapost.objects.filter(user=target_user).order_by('-created_at')
    reels = instrareels.objects.filter(user=target_user).order_by('-created_at')

    count_followers = followusers.objects.filter(following_person=target_user).count()
    count_following = followusers.objects.filter(following=target_user).count()
    count_post = instrapost.objects.filter(user=target_user).count()

    # check follow or not
    is_following = followusers.objects.filter(
        following=uid,
        following_person=target_user
    ).exists()

    liked_posts = like_unlike.objects.filter(user_fk=uid).values_list('post_fk_id', flat=True)
    liked_reel = like_unlike.objects.filter(user_fk=uid).values_list('reel_fk_id', flat=True)

    context = {
        'uid': uid,
        'profile_user': target_user,
        'posts': posts,
        'reels': reels,
        'count_followers': count_followers,
        'count_following': count_following,
        'count_post': count_post,
        'is_following': is_following,
        'liked_posts': liked_posts,
        'liked_reel': liked_reel,
    }

    return render(request, "myapp/user_profile.html", context)



@checklogin
def notifications(request):
    uid = request.uid
    all_notifications = notification.objects.filter(reciver = uid).order_by("-created_at")
    my_following = followusers.objects.filter(following = uid).values_list("following_person_id", flat=True)
    
    context = {
        'uid': uid,
        'all_notifications':all_notifications,
        'my_following':my_following,
    }
    return render(request,"myapp/notifications.html", context)

@checklogin
def profile(request):
    uid = request.uid
    mypost = instrapost.objects.filter(user=uid).order_by('-created_at')

    myreel = instrareels.objects.filter(user = uid).order_by('-created_at')
    
    count_followers = followusers.objects.filter(following_person = uid).count()
    count_following = followusers.objects.filter(following = uid).count()
    count_post = instrapost.objects.filter(user = uid).count()

    liked_reel = like_unlike.objects.filter(user_fk=uid).values_list('reel_fk_id', flat=True)

    liked_posts = like_unlike.objects.filter(user_fk=uid).values_list('post_fk_id', flat=True)

    context = {
        'uid': uid,
        'mypost' : mypost,
        'count_followers': count_followers,
        'count_following':count_following,
        'count_post':count_post,
        'liked_posts':liked_posts,   
        'myreel':myreel,
        'liked_reel':liked_reel
    }
    return render(request, "myapp/profile.html", context)

@checklogin
def reels(request):
    uid = request.uid
    all_reels = instrareels.objects.all()

    liked_reels = like_unlike.objects.filter(
        user_fk=uid,
        reel_fk__isnull=False
    ).values_list('reel_fk_id', flat=True)

   

    context = {
        'uid': uid,
        'all_reels': all_reels,
        'liked_reels':liked_reels,
        
    }
    return render(request,"myapp/reels.html", context)

@checklogin
def create_reel(request):
    uid = request.uid
    if request.POST:
        video = request.FILES['video']
        caption = request.POST['caption']

        instrareels.objects.create(
            user = uid,
            video = video,
            caption = caption
        )
        return redirect("reels") 
      
    context = {
        'uid': uid,
    }
    return render(request,"myapp/create_reel.html", context)

@checklogin
def search(request):
    uid = request.uid
    users = instrauser.objects.exclude(username = uid.username)
    my_following = followusers.objects.filter(following = uid).values_list("following_person_id",flat=True)

    query = request.GET.get("q")
    if query:
        users = users.filter(
            Q(username__icontains = query)|
            Q(fullname__icontains = query)
        )
    else:
        users = instrauser.objects.none()

    context = {
        'uid': uid,
        'users': users,
        'my_following': my_following,
    }
    return render(request,"myapp/search.html", context)

@checklogin
def settings(request):
    uid = request.uid
    context = {
        'uid': uid,
    }
    return render(request,"myapp/settings.html", context)

@checklogin
def following(request):
    uid = request.uid
    users = instrauser.objects.exclude(username = uid.username)

    my_following = followusers.objects.filter(following = uid).values_list("following_person_id",flat=True)
 
    query = request.GET.get("q")

    if query:
        users = users.filter(
            Q(username__icontains = query)|
            Q(fullname__icontains = query)
            )


    context = {
        'uid': uid,
        'users' : users,
        'my_following' : my_following,
    }
    return render(request, "myapp/following.html", context)

@checklogin
def follow_unfollow(request,pk):
    uid = request.uid
    target_user = instrauser.objects.get(id = pk)

    if uid == target_user:
        return redirect(request.META.get('HTTP_REFERER', 'following'))

    following_persons = followusers.objects.filter(following = uid , following_person = target_user).first()

    if following_persons:
        # unfollow logic here
        following_persons.delete()  # delete entry from follow model
    else:
        # follow logic here
        followusers.objects.create(following = uid , following_person = target_user)

        notification.objects.create(
            sender = uid,
            reciver = target_user,
            message = "started following you",
            notification_type = "follow"
        )

    return redirect(request.META.get('HTTP_REFERER', 'following'))

@checklogin
def followers(request):
    uid = request.uid
    followers_list = followusers.objects.filter(following_person = uid)
    my_following = followusers.objects.filter(following = uid).values_list("following_person_id", flat=True)

    query = request.GET.get("q")
    if query:
        followers_list = followers_list.filter(
            Q(following__username__icontains = query)|
            Q(following__fullname__icontains = query)
        )

    context = {
        'uid': uid,
        'followers_list' : followers_list,
        'my_following':my_following
    }

    return render(request, "myapp/followers.html", context)


@checklogin
def remove_followers(request,pk):
    uid = request.uid
    
    target_user_followers = followusers.objects.filter(id=pk).delete()

    return redirect("followers")


@checklogin
def like_unlike_post(request, pk):
    if request.method == "POST":
        uid = request.uid

        type = request.POST.get("type")

        if type == "post":
            post = instrapost.objects.get(id=pk)

            like = like_unlike.objects.filter(user_fk=uid, post_fk=post).first()

            if like:
                like.delete()
                if uid != post.user:
                    notification.objects.filter(sender=uid, reciver=post.user, post_fk=post, notification_type="like").delete()
            else:
                like_unlike.objects.create(user_fk=uid, post_fk=post)
                if uid != post.user:
                    notification.objects.get_or_create(
                        sender = uid,
                        reciver = post.user,
                        post_fk = post,
                        notification_type = "like",
                        defaults = {'message': 'liked your post'}
                    )

        elif type == "reel":
            reel = instrareels.objects.get(id=pk)

            like = like_unlike.objects.filter(user_fk=uid, reel_fk=reel).first()

            if like:
                like.delete()
                if uid != reel.user:
                    notification.objects.filter(sender=uid, reciver=reel.user, notification_type="like").delete()
            else:
                like_unlike.objects.create(user_fk=uid, reel_fk=reel)
                if uid != reel.user:
                    notification.objects.get_or_create(
                        sender = uid,
                        reciver = reel.user,
                        reel_fk = reel,
                        notification_type = "like",
                        post_fk = None,
                        defaults = {'message': 'liked your reel'}
                    )

    return redirect(request.META.get('HTTP_REFERER'))

def forgot_password(request):
    if request.POST:
        email = request.POST['email']
        try:
            uid = instrauser.objects.get(email = email)
             
            if uid:
                otp = random.randint(1111,9999)
                uid.otp = otp
                uid.save()  
                customesendmail("forgot_password","mailtemplate",email,{'otp' : otp})

                context = {
                    'email' : email
                }
                return render(request,"myapp/otp.html",context)
        except Exception as e:
            # print("---->>excepion",e)
            
            context = {
                'e_msg' : "user does not exist!"
            }
            return render(request,"myapp/forgot_password.html",context)

        return render(request,"myapp/reset_password.html")
    else:
        return render(request,"myapp/forgot_password.html")

def otp_verification(request):
    if request.POST:
        email = request.POST['email']
        otp = request.POST['otp']

        uid = instrauser.objects.get(email=email)

        if str(uid.otp) == otp:
            return render(request,"myapp/reset_password.html",{'email':email})
        else:
            return redirect("forgot_password")

    return render(request,"myapp/reset_password.html")

def reset_password(request):
    if request.POST:
        email = request.POST['email']
        newpassword = request.POST['newpassword']
        repassword = request.POST['repassword']

        uid = instrauser.objects.get(email=email)

        if newpassword == repassword:
            uid.password = make_password(newpassword)
            uid.save()
            return redirect("login")
            
        else:
            return redirect("forgot_password")

    return render(request,"myapp/reset_password.html")


@checklogin
def user_following(request, pk):
    uid = request.uid

    target_user = instrauser.objects.get(id=pk)

    following = followusers.objects.filter(following=target_user)

    context = {
        'uid': uid,
        'target_user': target_user,
        'following': following,
    }

    return render(request, "myapp/user_following.html", context)

@checklogin
def user_followers(request, pk):
    uid = request.uid

    target_user = instrauser.objects.get(id=pk)

    followers = followusers.objects.filter(following_person=target_user)

    context = {
        'uid': uid,
        'target_user': target_user,
        'followers': followers,
    }

    return render(request, "myapp/user_followers.html", context)

@checklogin
def messages(request,pk=None):
    uid = request.uid
    sender = instrauser.objects.get(id = uid.id)
    receiver = None
    message = []

    following_list = followusers.objects.filter(following = sender)

    following_users = [f.following_person for f in following_list]

    #receiver id

    if pk:
        receiver = instrauser.objects.get(id = pk)

        conversation_room = get_or_create_chatroom(sender,receiver)
        
        message = all_messages.objects.filter(chat_room = conversation_room)

        for msg in message:
            print(f"--------->>>>>> sender_id :: {msg.sender_id} {sender}")

    context = {
        'uid': uid,
        'sender' : sender,
        'following_users' : following_users,
        'receiver' : receiver,
        'message':message
    }
    return render(request,"myapp/messages.html", context)

@checklogin
def send_message(request,pk):
    if request.POST:
        uid = request.uid
        sender = instrauser.objects.get(id = uid.id)
        receiver = instrauser.objects.get(id = pk)
        conversation_room = get_or_create_chatroom(sender,receiver)

        text_message = request.POST['message_text']
        
        msg_obj = all_messages.objects.create(
            chat_room = conversation_room,
            sender_id = sender,
            text_message = text_message
        )

        if "image" in request.FILES:
            msg_obj.image = request.FILES['image']
            msg_obj.save()
        if "video" in request.FILES:
            msg_obj.video = request.FILES['video']
            msg_obj.save()

        return redirect("messages",pk=receiver.id)

@checklogin
def comments(request, pk, media_type='post'):
    uid = request.uid
    
    if media_type == "post":
        obj = instrapost.objects.get(id=pk)
        type = "post"
        all_comments = add_comments.objects.filter(post_fk=obj).order_by('-created_at')
    else:
        obj = instrareels.objects.get(id=pk)
        type = "reel"
        all_comments = add_comments.objects.filter(reel_fk=obj).order_by('-created_at')

    # Naya comment save karne ke liye
    if request.method == "POST":
        msg = request.POST.get('comment_text')
        
        if type == "post":
            add_comments.objects.create(user_fk=uid, post_fk=obj, comment_text=msg)
            if uid != obj.user:
                notification.objects.create(sender=uid, reciver=obj.user, post_fk=obj, message="commented on your post", notification_type="comment")
        else:
            add_comments.objects.create(user_fk=uid, reel_fk=obj, comment_text=msg)
            if uid != obj.user:
                notification.objects.create(sender=uid, reciver=obj.user, reel_fk=obj, message="commented on your reel", notification_type="comment")
            
        return redirect(request.META.get('HTTP_REFERER', 'comments'))

    context = {
        'uid': uid,
        'obj': obj,
        'type': type,
        'all_comments': all_comments,
    }
    return render(request, "myapp/comments.html", context)
              