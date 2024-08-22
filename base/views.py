from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from .models import User,Artist,Music
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .forms import UserForm,ArtistForm,MusicForm
from django.core.paginator import Paginator
from django.urls import reverse
from django.http import HttpResponse
from .resources import ArtistResource
from tablib import Dataset


def artist_csv_export(request):
    artist_resource = ArtistResource()
    dataset = artist_resource.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="artists.csv"'
    return response


def email_password_validate(email,password):
    # Validate email format
    try:
        validate_email(email)
    except ValidationError:
        return 'Invalid email format.'

    # Check if email already exists
    if User.objects.filter(email=email).exists():
        return 'Email is already registered.'
    # Validate password strength (example: length check)
    if len(password) < 8:
        return 'Password must be at least 8 characters long.'
    
    return True

# Create your views here.
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email,password=password)
        if user != None:
            login(request, user)
            messages.success(request,'Login Successfull!')
            return redirect('dashboard')
        else:
           messages.error(request,'Invalid username or password')
    return render(request,'login.html')

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        validation = email_password_validate(email,password)
        if validation == True:
            hash_password = make_password(password)
            user = User.objects.create(email=email,password=hash_password,is_active=True)
            messages.success(request,'Registeration Successfull!')
            return redirect('login')
        
        messages.error(request,validation)
        
    return render(request,'register.html')

def logout_view(request):
    logout(request)
    messages.success(request,f'Logged out successfully!')
    return redirect('login')   

def dashboard_view(request):
    paginate_data = request.GET.get('data')
    users = User.objects.filter(is_active=False)
    user_paginator = Paginator(users, 10)  # Show 10 users per page.
    artists = Artist.objects.all()
    artist_paginator = Paginator(artists, 10)  # Show 10 users per page.
    if paginate_data != None:
        if paginate_data == 'user':
            page_number = request.GET.get('page')
            user_page_obj = user_paginator.get_page(page_number)
            artist_page_obj = artist_paginator.get_page(1)
        else:
            page_number = request.GET.get('page')
            artist_page_obj = artist_paginator.get_page(page_number)
            user_page_obj = user_paginator.get_page(1)
    else:
        artist_page_obj = artist_paginator.get_page(1)
        user_page_obj = user_paginator.get_page(1)

    data = {'user_data':user_page_obj,'artist_data':artist_page_obj}
    return render(request,'index.html',context=data)

def user_create_view(request):
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'User data created!')
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    return render(request,'user_create.html',{'form': form})

def artist_create_view(request):
    form = ArtistForm()
    if request.method == 'POST':
        first_release_year = request.POST.get('first_release_year')
        data = request.POST.copy()
        data['first_release_year'] = f'{first_release_year}-01-01'
        form = ArtistForm(data)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    messages.success(request,'Artist data created!')
    return render(request,'artist_create.html',{'form': form})

def user_edit_view(request,pk):
    form = UserForm()
    try:
        instance = User.objects.get(id=pk)
    except:
        messages.error(request,'User data not found!')
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserForm(request.POST,instance=instance)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    form = UserForm(initial={'first_name': instance.first_name,'last_name':instance.last_name,'email':instance.email,'phone':instance.phone,'gender':instance.gender,'address':instance.address})
    messages.success(request,'User data edited!')
    return render(request,'user_edit.html',{'form': form})   

def user_delete_view(request,pk):
    try:
        instance = User.objects.get(id=pk)
    except:
        messages.error(request,'User data not found!')
        return redirect('dashboard')
    instance.delete()
    messages.success(request,'User data deleted!')
    return redirect('dashboard')

def artist_edit_view(request,pk):
    form = ArtistForm()
    try:
        instance = Artist.objects.get(id=pk)
    except:
        messages.error(request,'Artist data not found!')
        return redirect('dashboard')
    if request.method == 'POST':
        first_release_year = request.POST.get('first_release_year')
        data = request.POST.copy()
        data['first_release_year'] = f'{first_release_year}-01-01'
        form = ArtistForm(data,instance=instance)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    form = ArtistForm(initial={'name': instance.name,'dob':instance.dob,'gender':instance.gender,'address':instance.address,'first_release_year':instance.first_release_year.year,'no_of_albums_released':instance.no_of_albums_released})
    return render(request,'artist_edit.html',{'form': form})   

def artist_delete_view(request,pk):
    try:
        instance = Artist.objects.get(id=pk)
    except:
        messages.error(request,'Artist data not found!')
        return redirect('dashboard')
    instance.delete()
    return redirect('dashboard')

def artist_music_view(request,pk):
    music_objs = Music.objects.filter(artist_id=pk)
    user_paginator = Paginator(music_objs, 10) 
    page_number = request.GET.get('page')
    music_page_obj = user_paginator.get_page(page_number)
    data = {'musics':music_page_obj,'artist_id':pk}
    return render(request,'artist_music.html',context=data)

def artist_music_create_view(request,pk):
    form = MusicForm()
    try:
        instance = Artist.objects.get(id=pk)
    except:
        messages.error(request,'Artist data not found!')
        return redirect(reverse('artist-music', kwargs={'pk': pk}))
    if request.method == 'POST':
        data = request.POST.copy()
        data['artist_id'] = instance
        form = MusicForm(data)
        if form.is_valid():
            form.save()
            return redirect(reverse('artist-music', kwargs={'pk': pk}))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    return render(request,'artist_music_create.html',{'form': form})

def artist_music_edit_view(request,pk):
    form = MusicForm()
    try:
        instance = Music.objects.get(id=pk)
    except:
        messages.error(request,'Music data not found!')
        return redirect(reverse('artist-music', kwargs={'pk': pk}))
    if request.method == 'POST':
        artist_id = Artist.objects.get(id=instance.artist_id.id)
        data= request.POST.copy()
        data['artist_id'] = artist_id
        form = MusicForm(data,instance=instance)
        if form.is_valid():
            form.save()
            return redirect(reverse('artist-music', kwargs={'pk': artist_id.id}))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    form = MusicForm(initial={'title': instance.title,'album_name':instance.album_name,'genre':instance.genre})
    return render(request,'artist_music_edit.html',{'form': form})   

def artist_music_delete_view(request,pk):
    try:
        instance = Music.objects.get(id=pk)
    except:
        messages.error(request,'Music data not found!')
        return redirect('dashboard')
    instance.delete()
    return redirect(reverse('artist-music', kwargs={'pk': instance.artist_id.id}))

def artist_csv_import(request):
    if request.method == 'POST':
        dataset = Dataset()
        print(request.FILES)
        new_artists = request.FILES['csv_file']

        imported_data = dataset.load(new_artists.read().decode('utf-8'), format='csv')
        artist_resource = ArtistResource()
        result = artist_resource.import_data(dataset, dry_run=True)  # Test the data import

        if not result.has_errors():
            artist_resource.import_data(dataset, dry_run=False)  # Actually import now
        else:
            for error in result.error_rows:
                    messages.error(request, error)

    return render(request,'artist_import.html')