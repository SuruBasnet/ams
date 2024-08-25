from typing import Any
from django import forms
from .models import User,Artist,Music


class YearInput(forms.DateInput):
    input_type = 'number'
    attrs = {'min': '1900', 'max': '2100'} 

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'password', 'email', 'phone', 'gender', 'address']

    


class ArtistForm(forms.ModelForm):   
    dob = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})  # HTML5 date input
    )
    class Meta:
        model = Artist
        fields = ['name','dob','gender','address','first_release_year','no_of_albums_released']
        widgets = {
            'first_release_year': YearInput(attrs={'placeholder': 'YYYY'}),
        }

class MusicForm(forms.ModelForm):
    class Meta:
        model = Music
        fields = ['artist_id','title','album_name','genre']


    
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(),required=False)    
    email = forms.EmailField(required=False)
    class Meta:
        model = User
        fields = ['first_name','last_name','password', 'email', 'phone', 'gender','address']
    
