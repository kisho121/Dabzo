from django.urls import path, include
from .import views

urlpatterns = [
    path('accounts/', include('allauth.urls')),
     
    path('',views.home,name="home"),
    path('login', views.login_page,name="account_login"),
    path('logout', views.logout_page,name="account_logout"),
    path('register',views.registerpage, name="account_signup"),
    path('otp-verification/', views.otp_verification, name='otp_verification'),
    path('audio',views.musicView,name='audio'),
    path('audio/<str:name>',views.CategoryView,name='category'),
    path('audio/<str:ctname>/<str:aname>/<str:clname>',views.CollectionView,name='collection'),
    path('audio/<str:catname>/<str:aname>/<str:cltname>/<str:pname>',views.MusicPlayerView,name='player'),
    path('video',views.videoView,name='video'),
    path('video/<str:vname>',views.moviesView,name='movies'),
    path('video/<str:pname>/<str:sname>/<str:dname>',views.streamView,name='stream'),
    path('speed-test',views.SpeedTestView,name='speedtest'),
    # path('contact',views.contactView,name='contact'),
    path('about',views.AboutView, name='about'),
    path('privacy',views.PrivacyViews,name='privacy'),
    path('search',views.SearchViews,name='search'),
    path('support',views.supportview,name="support"),
    path('profile',views.profileView,name="profile"),
    path('toggle-favourite/', views.toggle_favourite, name='toggle_favourite'),
    path('myPlaylist', views.myPlaylistView, name='myPlaylist'),
    path('make-admin', views.make_admin, name ='make_admin'),
   
]
