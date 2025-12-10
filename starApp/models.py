from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dateOfBirth = models.DateField(null=True)
    profilePicture = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return self.user.username


class OTPVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)


class carousel(models.Model):
    carousel_image = CloudinaryField('image')
    alt_text = models.CharField(max_length=150, default="slide_image")
    created_at = models.DateTimeField(auto_now_add=True)


class MusicModel(models.Model):
    musicName = models.CharField(max_length=150)
    musicImage = CloudinaryField('image', blank=True)
    status = models.BooleanField(default=False, help_text='0-show,1-Hidden')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.musicName


class AudioTitleModel(models.Model):
    musickey = models.ForeignKey(MusicModel, on_delete=models.CASCADE)
    categorytitle = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.categorytitle


class CategoryModel(models.Model):
    musicModel = models.ForeignKey(AudioTitleModel, on_delete=models.CASCADE)
    artistName = models.CharField(max_length=150)
    artistImage = CloudinaryField('image')
    artistDescription = models.CharField(max_length=1500)
    status = models.BooleanField(default=False, help_text='show-0,Hidden=1')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.artistName


class CollectionModel(models.Model):
    categoryModel = models.ForeignKey(CategoryModel, on_delete=models.CASCADE)
    cltnImage = CloudinaryField('image')
    audio = models.URLField(max_length=500, blank=True, null=True)
    songname = models.CharField(max_length=150)
    movie = models.CharField(max_length=150)
    artist = models.CharField(max_length=150)
    duration = models.FloatField()
    favourite = models.BooleanField(default=False, help_text='show-0,Trending-1')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.songname


class Thumbnail(models.Model):
    thumb_image = CloudinaryField('image')
    thumb_text = models.CharField(max_length=150, default="slide_image")
    created_at = models.DateTimeField(auto_now_add=True)


class VideosModel(models.Model):
    videoName = models.CharField(max_length=150)
    videoImage = CloudinaryField('image')
    bgvideo = CloudinaryField(resource_type='video')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.videoName


class VideoTitleModel(models.Model):
    videomodel = models.ForeignKey(VideosModel, on_delete=models.CASCADE)
    categorytitle = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.categorytitle


class CategoryListModel(models.Model):
    VIDEOTYPE_CHOICES = [
        ('standard', 'Standard'),
        ('youtube', 'YouTube'),
    ]

    videotitle = models.ForeignKey(VideoTitleModel, on_delete=models.CASCADE)
    subtitle = models.CharField(max_length=150)
    videodescription = models.CharField(max_length=1500)
    videothumbnail = CloudinaryField('image')
    video = models.URLField(max_length=500, blank=True, null=True)
    video_type = models.CharField(max_length=10, choices=VIDEOTYPE_CHOICES, default='standard')
    like = models.BooleanField(default=False, help_text='default-0,like-1')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subtitle


class UserFavourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(CollectionModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'song')
        verbose_name = 'User Favourite'
        verbose_name_plural = 'User Favourites'

    def __str__(self):
        return f"{self.user.username} - {self.song.songname}"
