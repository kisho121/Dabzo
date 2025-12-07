from django.shortcuts import get_object_or_404, render,redirect
from .models import *
from django.contrib import messages
from .forms import formCreation
from django.contrib.auth import authenticate,login,logout
from django.conf import settings
from django.core.mail import send_mail
import random
from django.urls import reverse
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Count  



def home(request):
     
     favourites=CollectionModel.objects.filter(favourite=1)
     likes=CategoryListModel.objects.filter(like=1)
     context={
         "favourites":favourites,  
         "likes":likes
     }
     return render(request,'starApp/home.html',context)

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,'Logged out Successfully')
    return redirect('/')
    
def login_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
     if request.method == "POST":
        name=request.POST.get('username')
        pwd=request.POST.get('password')
        user=authenticate(request,username=name,password=pwd)
        if user is not None:
            login(request,user)
            messages.success(request,"SuccessFully Logged in")
            return redirect('/')  
        else:
            messages.error(request,"Invalid User name Or Password")
            return redirect('account_login')
        
     return render(request,'starApp/account/login.html')
 
def sent_otp(email, otp):
    subject = 'Your OTP for Registration'
    message = f'Your OTP for Registration is {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)    

def registerpage(request):
    if request.method == 'POST':
        form = formCreation(request.POST, request.FILES)
        if form.is_valid():
            user=form.save(commit =False)
            user.is_active = False
            user.save()

            UserProfile.objects.create( 
                user=user, dateOfBirth=form.cleaned_data['dateOfBirth'], 
                profilePicture=form.cleaned_data.get('profilePicture'), )

            otp =random.randint(100000,999999)
            OTPVerification.objects.create(user=user, otp =otp)
            sent_otp(user.email, otp)
            return redirect(reverse('otp_verification') + f'?email={user.email}')
    else:
        form = formCreation()
    return render(request,'starApp/account/signup.html',{'form':form})


def otp_verification(request):
    email = request.GET.get('email')
    if request.method == 'POST':
        otp = request.POST.get('otp')
        try:
            user_otp = OTPVerification.objects.get(user__email=email, otp=otp)
            user = user_otp.user
            user.is_active = True
            user.save()
            user_otp.delete()  # OTP is used, so delete it
            messages.success(request, "Registration successfull> Login Now..")
            return redirect('account_login')
        except OTPVerification.DoesNotExist:
            messages.error(request, 'Invalid OTP. Please try again.')
    return render(request, 'starApp/otp_verification.html', {'email': email})

# ============ UPDATED musicView FUNCTION ============
from django.db.models import Count

def musicView(request):
    slides = carousel.objects.all()
    music = MusicModel.objects.all()
    favourites = CollectionModel.objects.filter(favourite=1)
    
    # Get top 10 globally most liked songs
    global_top_songs = CollectionModel.objects.annotate(
        like_count=Count('userfavourite')
    ).filter(
        like_count__gt=0
    ).order_by('-like_count')[:10]
    
    # Calculate percentages for progress bars
    if global_top_songs.exists():
        max_likes = global_top_songs[0].like_count
        for song in global_top_songs:
            song.like_percentage = (song.like_count / max_likes * 100) if max_likes > 0 else 0
    
    # ============ FIX: GET USER'S WISHLIST IDS (CONSISTENT NAMING) ============
    user_favourites = []  # For HOT TRACKS table compatibility
    user_wishlist_ids = []  # For Global Top 10 table
    
    if request.user.is_authenticated:
        # Get the list of song IDs the user has liked
        wishlist_ids = list(
            UserFavourite.objects.filter(user=request.user).values_list('song_id', flat=True)
        )
        user_favourites = wishlist_ids  # Same data, different variable name
        user_wishlist_ids = wishlist_ids  # Same data, different variable name
    # ============ END FIX ============
    
    context = {
        "slides": slides,
        "music": music,
        "favourites": favourites,
        "global_top_songs": global_top_songs,
        "user_wishlist_ids": user_wishlist_ids,  # For Global Top 10 section
        "user_favourites": user_favourites,  # For HOT TRACKS section
    }
    
    return render(request, 'starApp/webpage/audio.html', context)


# ============ UPDATED toggle_favourite FUNCTION ============
@login_required
@require_POST
def toggle_favourite(request):
    song_id = request.POST.get('song_id')
    
    try:
        song = CollectionModel.objects.get(id=song_id)
        
        # Check if user already liked this song
        favourite = UserFavourite.objects.filter(user=request.user, song=song).first()
        
        if favourite:
            # Unlike: delete the favourite
            favourite.delete()
            liked = False
            action = 'removed'
        else:
            # Like: create new favourite
            UserFavourite.objects.create(user=request.user, song=song)
            liked = True
            action = 'added'
        
        # Get updated like count for this song
        like_count = UserFavourite.objects.filter(song=song).count()
        
        return JsonResponse({
            'status': 'success',
            'liked': liked,
            'action': action,
            'like_count': like_count  # Return current like count
        })
    
    except CollectionModel.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Song not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def CategoryView(request,name):
    MusicModel_obj=get_object_or_404(MusicModel,musicName=name)
    categories=AudioTitleModel.objects.filter(musickey=MusicModel_obj)
    
    categories_with_audios={}
    for category in categories:
        audios=CategoryModel.objects.filter(musicModel=category)
        categories_with_audios[category]=audios
        
    context={
            'categories_with_audios':categories_with_audios,
            'musicName':name,
            'musicImage':MusicModel_obj.musicImage,
        }
    return render(request,'starApp/webpage/music_category.html',context)

    
def CollectionView(request, ctname, aname, clname):
    music_obj = get_object_or_404(MusicModel, musicName=ctname)
    audio_obj=get_object_or_404(AudioTitleModel,categorytitle=aname ,musickey=music_obj)
    category_obj = get_object_or_404(CategoryModel, artistName=clname, musicModel=audio_obj)
    collections = CollectionModel.objects.filter(categoryModel=category_obj)
    context = {
        "collections": collections,
        "musicName": ctname,
        "categorytitle":aname,
        "artistName": clname,
        "artistImage": category_obj.artistImage,
        "artistDescription": category_obj.artistDescription,
    }
    return render(request, 'starApp/webpage/collectionlist.html', context)

def MusicPlayerView(request, catname, aname, cltname, pname):
    music_obj = get_object_or_404(MusicModel, musicName=catname)
    audio_obj = get_object_or_404(AudioTitleModel, categorytitle=aname, musickey=music_obj)
    category_obj = get_object_or_404(CategoryModel, artistName=cltname, musicModel=audio_obj)
    collection_obj = get_object_or_404(CollectionModel, songname=pname, categoryModel=category_obj)
    
    musicPlayer = CollectionModel.objects.filter(categoryModel=category_obj)
    
    # Check if current song is liked by this user
    is_liked = UserFavourite.objects.filter(user=request.user, song=collection_obj).exists()
    
    # Get all user's favourite song IDs
    user_favourites = list(UserFavourite.objects.filter(user=request.user).values_list('song_id', flat=True))
    
    context = {
        "musicPlayer": musicPlayer,
        "musicName": catname,
        "categorytitle": aname,
        "artistName": cltname,
        "songname": pname,
        "cltnImage": collection_obj.cltnImage,
        "audio": collection_obj.audio,
        "movie": collection_obj.movie,
        "artist": collection_obj.artist,
        "duration": collection_obj.duration,
        "current_song": collection_obj,
        "is_liked": is_liked,
        "user_favourites": user_favourites,
    }
    return render(request, 'starApp/webpage/musicplayer.html', context)


 
def videoView(request):
    swap=Thumbnail.objects.all()
    videos=VideosModel.objects.all()
    likes=CategoryListModel.objects.filter(like=1)
    context={
        "swap":swap,
        "videos":videos,
        'likes':likes
    }
    return render(request,'starApp/webpage/video.html',context)

def moviesView(request,vname):
    video_obj=get_object_or_404(VideosModel, videoName=vname)
    categorys=VideoTitleModel.objects.filter(videomodel=video_obj)
    categorys_with_videos={}
    for category in categorys:
        videos=CategoryListModel.objects.filter(videotitle=category)
        categorys_with_videos[category]=videos
    context={
        'categorys_with_videos':categorys_with_videos,
        'videoName':vname,
        'bgvideo':video_obj.bgvideo,
        'videoImage':video_obj.videoImage,
        
    }
    
    return render(request,'starApp/webpage/movies.html',context)

def streamView(request,pname,sname,dname):
    video_obj=get_object_or_404(VideosModel,videoName=pname)
    category_obj=get_object_or_404(VideoTitleModel,categorytitle=sname, videomodel=video_obj)
    stream_obj=get_object_or_404(CategoryListModel, subtitle=dname, videotitle=category_obj )
    
    streaming=CategoryListModel.objects.filter(videotitle=category_obj)
    context={
        
        'streaming':streaming,
        'videoName':pname,
        'categorytitle':sname,
        'subtitle':dname,
        'videodescription':stream_obj.videodescription,
        'video':stream_obj.video,
        'like':stream_obj.like,
        
    }
    return render(request,'starApp/webpage/stream.html',context)

def SpeedTestView(request):
    return render(request,'starApp/webpage/speedtest.html')

def contactView(request):
    return render(request,'starApp/webpage/contact.html')

def AboutView(request):
    return render(request, 'starApp/webpage/about.html')

def PrivacyViews(request):
    return render(request,'starApp/webpage/privacy.html')

def SearchViews(request):
    query=request.GET.get('q')
    searched = False
    songs=[]
    videos=[]
    if query:
        searched=True
        
        songs=CollectionModel.objects.filter(songname__icontains=query)
       
        videos=CategoryListModel.objects.filter(subtitle__icontains=query)
       
    
    return render(request,'starApp/webpage/search.html', {'songs':songs,'videos':videos, 'searched' :searched})

def supportview (request):
    return render(request, 'starApp/webpage/support.html')

def profileView(request):
    return render(request, 'starApp/account/profile.html')
    
@login_required
def myPlaylistView(request):
    # Get all songs this user has liked
    user_favourite_ids = UserFavourite.objects.filter(user=request.user).values_list('song_id', flat=True)
    wishlist_songs = CollectionModel.objects.filter(id__in=user_favourite_ids).order_by('-id')
    
    context = {
        'wishlist_songs': wishlist_songs,
        'total_count': wishlist_songs.count()
    }
    return render(request, 'starApp/webpage/myPlaylist.html', context)