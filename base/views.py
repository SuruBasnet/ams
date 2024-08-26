from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.http import HttpResponse
from django.db import connection
from .resources import ArtistResource
from tablib import Dataset
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from .forms import UserForm,ArtistForm,MusicForm
from django.core.paginator import Paginator
import datetime
from .models import *

def run_sql_query(query, params=()):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        # If the query is not a SELECT, return None or something appropriate
        if cursor.description is None:
            return None
        else:
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

def artist_csv_export(request):
    artist_resource = ArtistResource()
    dataset = artist_resource.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="artists.csv"'
    return response



def email_password_validate(email, password):
    # Validate email format
    try:
        validate_email(email)
    except ValidationError:
        return 'Invalid email format.'

    # Check if email already exists using raw SQL
    query = "SELECT * FROM base_user WHERE email = %s"
    user_exists = run_sql_query(query, [email])
    
    if user_exists:
        return 'Email is already registered.'

    # Validate password strength (example: length check)
    if len(password) < 8:
        return 'Password must be at least 8 characters long.'

    return True

def update_email_password_validate(email, password):
    # Validate email format
    try:
        validate_email(email)
    except ValidationError:
        return 'Invalid email format.'

    # Check if email already exists using raw SQL
    query = "SELECT * FROM base_user WHERE email = %s"
    user_exists = run_sql_query(query, [email])
    
    if len(user_exists) > 1:
        return 'Email is already registered.'

    # Validate password strength (example: length check)
    if len(password) < 8:
        return 'Password must be at least 8 characters long.'

    return True

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)
        if user != None:
            login(request, user)
            messages.success(request, 'Login Successful!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        validation = email_password_validate(email, password)
        if validation == True:
            hash_password = make_password(password)
            query = '''INSERT INTO base_user 
            (first_name, last_name, email, password, phone, gender, address, is_active, is_superuser,username,is_staff, date_joined,created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s,%s,%s,%s,%s)'''
            run_sql_query(query, ['first_name','last_name',email, hash_password,0,'male','address', True,False,'username',False,datetime.date.today(),datetime.datetime.now(),datetime.datetime.now()])
            messages.success(request, 'Registration Successful!')
            return redirect('login')

        messages.error(request, validation)

    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')

def dashboard_view(request):
    paginate_data = request.GET.get('data')

    # Fetch Users
    user_query = "SELECT * FROM base_user WHERE is_active = %s"
    users = run_sql_query(user_query, [False])

    # Fetch Artists
    artist_query = "SELECT * FROM base_artist"
    artists = run_sql_query(artist_query)

    # Pagination logic (using Django's Paginator)
    user_paginator = Paginator(users, 10)
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
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        form = UserForm(request.POST)
        if form.is_valid():
            query = '''INSERT INTO base_user 
            (first_name, last_name, email,  phone, gender, address, is_active, is_superuser,username,is_staff, date_joined,created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s,%s,%s,%s)'''
            run_sql_query(query, [first_name,last_name,email,phone,gender,address, False ,False,'username',False,datetime.date.today(),datetime.datetime.now(),datetime.datetime.now()])
            messages.success(request, 'User data created!')
            return redirect('dashboard')
        else:
            messages.error(request, form.errors)
    return render(request,'user_create.html',{'form': form})


def artist_create_view(request):
    form = ArtistForm()
    if request.method == 'POST':
        data = request.POST.copy()
        name = request.POST.get('name')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        first_release_year = f'{request.POST.get('first_release_year')}-01-01'
        data['first_release_year'] = first_release_year
        no_of_albums_released = request.POST.get('no_of_albums_released')
        form = ArtistForm(data)
        if form.is_valid():
            query = """
                INSERT INTO base_artist 
                (name, dob, gender, address, first_release_year, no_of_albums_released, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            run_sql_query(query, [name, dob, gender, address, first_release_year, no_of_albums_released,datetime.datetime.now(),datetime.datetime.now()])
            messages.success(request, 'Artist data created!')
            return redirect('dashboard')
        else:
            messages.error(request, form.errors)
    return render(request,'artist_create.html',{'form': form})


def user_edit_view(request, pk):
    form = UserForm()
    try:
        query = "SELECT * FROM base_user WHERE id = %s"
        instance = run_sql_query(query, [pk])[0]
    except:
        messages.error(request, 'User data not found!')
        return redirect('dashboard')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        data = request.POST.copy()
        data.pop('email')
        form = UserForm(data)
        validate = update_email_password_validate(email,'password1234')
        if validate == True:
            if form.is_valid():
                query = """
                    UPDATE base_user 
                    SET first_name = %s, last_name = %s, email = %s, phone = %s, gender = %s, address = %s, updated_at = %s 
                    WHERE id = %s
                """
                run_sql_query(query, [first_name, last_name, email, phone, gender, address,datetime.datetime.today(), pk])
                messages.success(request, 'User data edited!')
                return redirect('dashboard')
            else:
                messages.error(request, form.errors)
        else:
            messages.error(request, validate)

    
    form = {
        'first_name': instance['first_name'],
        'last_name': instance['last_name'],
        'email': instance['email'],
        'phone': instance['phone'],
        'gender': instance['gender'],
        'address': instance['address'],
    }
    form = UserForm(initial=form)
    return render(request, 'user_edit.html', {'form': form})

def user_delete_view(request, pk):
    query = "DELETE FROM base_user WHERE id = %s"
    run_sql_query(query, [pk])
    messages.success(request, 'User data deleted!')
    return redirect('dashboard')

def artist_edit_view(request, pk):
    try:
        query = "SELECT * FROM base_artist WHERE id = %s"
        artist = run_sql_query(query, [pk])[0]
    except:
        messages.error(request, 'Artist data not found!')
        return redirect('dashboard')
    if request.method == 'POST':
        data = request.POST.copy()
        name = request.POST.get('name')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        first_release_year = f'{request.POST.get('first_release_year')}-01-01'
        data['first_release_year'] = first_release_year
        no_of_albums_released = request.POST.get('no_of_albums_released')
        form = ArtistForm(data)
        if form.is_valid():
            query = """
                UPDATE base_artist 
                SET name = %s, dob = %s, gender = %s, address = %s, first_release_year = %s, no_of_albums_released = %s, updated_at = %s 
                WHERE id = %s
            """
            run_sql_query(query, [name, dob, gender, address, first_release_year, no_of_albums_released, datetime.datetime.today(), pk])
            messages.success(request, 'Artist data edited!')
            return redirect('dashboard')
        else:
                messages.error(request, form.errors)


    form = {
        'name': artist['name'],
        'dob': artist['dob'],
        'gender': artist['gender'],
        'address': artist['address'],
        'first_release_year': artist['first_release_year'].year,
        'no_of_albums_released': artist['no_of_albums_released'],
    }
    form = ArtistForm(initial=form)
    return render(request, 'artist_edit.html', {'form': form})

def artist_delete_view(request, pk):
    try:
        with connection.cursor() as cursor:
                cursor.execute("DELETE FROM base_music WHERE artist_id_id = %s", [pk])
                cursor.execute("DELETE FROM base_artist WHERE id = %s", [pk])
    except:
        messages.error(request, 'Artist data not found!')
        return redirect('dashboard')
    messages.success(request, 'Artist data deleted!')
    return redirect('dashboard')

def artist_music_view(request, pk):
    try:
        query = "SELECT * FROM base_artist WHERE id = %s"
        artists = run_sql_query(query, [pk])[0]
    except:
        messages.error(request,'Artists not found!')

    query = "SELECT * FROM base_music WHERE artist_id_id = %s"
    musics = run_sql_query(query, [pk])

    # Pagination logic (using Django's Paginator)
    user_paginator = Paginator(musics, 10) 
    page_number = request.GET.get('page')
    music_page_obj = user_paginator.get_page(page_number)
    data = {'musics':music_page_obj,'artist_id':pk,'artist_name':artists.get('name')}
    return render(request,'artist_music.html',context=data)


def artist_music_create_view(request, pk):
    form = MusicForm()
    if request.method == 'POST':
        data = request.POST.copy()
        title = request.POST.get('title')
        album_name = request.POST.get('album_name')
        genre = request.POST.get('genre')
        data['artist_id'] = pk
        form = MusicForm(data)
        if form.is_valid():
            query = """
                INSERT INTO base_music 
                (artist_id_id, title, album_name, genre, created_at, updated_at) 
                VALUES (%s, %s, %s, %s,%s, %s)
            """
            run_sql_query(query, [pk, title, album_name, genre,datetime.datetime.today(),datetime.datetime.today()])
            messages.success(request, 'Music data created!')
            return redirect(reverse('artist-music', kwargs={'pk': pk}))
        else:
             messages.error(request, form.errors)
    return render(request,'artist_music_create.html',{'form': form})


def artist_music_edit_view(request, pk):
    try:
        query = "SELECT * FROM base_music WHERE id = %s"
        music = run_sql_query(query, [pk])[0]
    except:
        messages.error('Music not found!')
        return redirect('dashboard')
    if request.method == 'POST':
        data = request.POST.copy()
        title = request.POST.get('title')
        album_name = request.POST.get('album_name')
        genre = request.POST.get('genre')
        artist_id = music.get('artist_id_id')
        data['artist_id'] = artist_id
        form = MusicForm(data)
        if form.is_valid():

            query = """
                UPDATE base_music 
                SET artist_id_id = %s, title = %s, album_name = %s, genre = %s, updated_at = %s
                WHERE id = %s
            """
            run_sql_query(query, [artist_id,title, album_name, genre, datetime.datetime.now(),pk])
            messages.success(request, 'Music data edited!')
            return redirect(reverse('artist-music', kwargs={'pk': artist_id}))
        else:
            messages.error(request,form.errors)


    form = {
        'title': music['title'],
        'album_name': music['album_name'],
        'genre': music['genre'],
    }
    form = MusicForm(initial=form)
    return render(request, 'artist_music_edit.html', {'form': form})

def artist_music_delete_view(request, pk):
    query = "DELETE FROM base_music WHERE id = %s"
    run_sql_query(query, [pk])
    messages.success(request, 'Music data deleted!')
    return redirect('dashboard')

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