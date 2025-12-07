from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
from django import forms

class formCreation(UserCreationForm):
    
    username= forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter your username'}))
    dateOfBirth=forms.DateField(widget=forms.TextInput(attrs={'type':'date'}))
    profilePicture=forms.ImageField(required=False)
    email= forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Enter your Email Id'}))
    password1= forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Enter your Password'}))
    password2= forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Enter your Confirm password'}))
    

    class Meta:
        model = User
        fields = ['username','email','password1','password2', 'dateOfBirth', 'profilePicture'] 
        
        
    def save(self, commit=True):
        user=super().save(commit=False)
        user.email=self.cleaned_data['email']
        if commit:
            user.save()
            print("User saved:", user.username)
            UserProfile.objects.create(
                    user=user,
                    dateOfBirth=self.cleaned_data['dateOfBirth'],
                    profilePicture=self.cleaned_data.get('profilePicture', None),
                )
            print("UserProfile created for:", user.username)
        return user