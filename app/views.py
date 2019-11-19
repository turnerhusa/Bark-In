"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render,redirect
from django.http import HttpRequest, HttpResponse
from django.template import loader
from .models import *
from .models import UserProfile
from app.forms import (EditProfileForm, ProfileForm,SignUpForm,AddDogForm,AddReviewForm)
from django.contrib.auth import update_session_auth_hash,authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


def index(request):
    parks = Park.objects.all()
    park_string_array = ""
    className = "'mapboxgl'"
    for park in parks:
        park_string_array += '{"type": "Feature", "properties": { "description": "<div class='+className+'>'+park.name+'</div>",},"geometry": {"type": "Point","coordinates": ['+str(park.lon)+', '+str(park.lat)+']}}'
        park_string_array += ","
        park_string_array += "\n"
    park_string_array = park_string_array[:-2]
    context = {
        'park_string_array' : park_string_array,
        'title':'Home Page',
        'year':datetime.now().year,
        }
    return render(request, 'app/index.html', context)


def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'year':datetime.now().year,
        }
    )
    
def login(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/login.html',
        {
            'title':'Login',
            'year':datetime.now().year
        }
    )

def logout_view(request):
    logout(request)
    return render(
        request,
        'app/layout.html',
        {
            'title':'Home',
            'year':datetime.now().year
        }
    )
    
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.userprofile.bio = form.cleaned_data.get('bio')
            user.save()
            raw_password = form.cleaned_data.get('password')
            auth_login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'app/signup.html', {'form': form})
    
def about(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About the Team',
            'year':datetime.now().year
        }
    )

def view_profile(request, uid):
    userProfile = UserProfile.objects.get(pk=uid)
    #need to add a way to fetch scheduled visits from just this user
    # for some reason passing just the userprofile doesn't work so I seperated the data
    editAllowed = False
    if (request.user.id == uid):
        editAllowed = True

    context = {
    'year' : datetime.now().year,
    'uid' : uid,
    'userBio' : userProfile.bio,
    'userDogs' : userProfile.dogs.all(),
    'userProfile' : userProfile.user,
    'editAllowed' : editAllowed, 
    }
    return render(request, 'app/view_profile.html', context)

def view_dog(request, uid,dogid):
    dog = Dog.objects.get(pk=dogid)
    context = {
    'name' : dog.name,
    'dogpfp' : dog.dog_pfp,
    'breed' : dog.breed,
    'dog_size' : dog.dog_size,
    'temperament' : dog.temperament,
    'activity_level' : dog.activity_level,
    'volume' : dog.volume,
    'notes' : dog.notes,
    }
    return render(request, 'app/view_dog.html', context)

def add_dog(request, uid):
    userProfile = UserProfile.objects.get(pk=uid)
    if request.method == 'POST':
        form = AddDogForm(request.POST)
        if form.is_valid():
            Dog = form.save()
            Dog.refresh_from_db()
            Dog.name = form.cleaned_data.get('name')
            Dog.breed = form.cleaned_data.get('breed')
            Dog.dog_size = form.cleaned_data.get('dog_size')
            Dog.temperament = form.cleaned_data.get('temperament')
            Dog.activity_level = form.cleaned_data.get('activity_level')
            Dog.volume = form.cleaned_data.get('volume')
            Dog.notes = form.cleaned_data.get('notes')
            Dog.save()
            userProfile.dogs.add(Dog) #add dog to user here
            userProfile.save()
            return redirect('index')
    else:
        form = AddDogForm()
    return render(request, 'app/add_dog.html', {'form': form})

def edit_dog_profile(request, uid, dogid):
    return HttpResponse("Edit dog"+str(dogid)+"'s profile' on User"+str(uid)+"'s page here")


def view_park(request, parkid):
    park = Park.objects.get(pk=parkid)

    editAllowed = False
    context = {
    'parkID' : parkid,
    'name' : park.name,
    'info' : park.info,
    'address' : park.address,
    'star_rating' : park.star_rating,
    'num_ratings' : park.num_ratings,
    'fenced_in' : park.fenced_in,
    'off_leash' : park.off_leash,
    'parkreviews' : park.reviews.all(),
    'parkschedules': park.schedules.all()
    }
    return render(request, 'app/view_park.html', context)


def review_park(request, parkid):
    park = Park.objects.get(pk=parkid)
    uid = request.user.id
    userProfile = UserProfile.objects.get(pk=uid)
    if request.method == 'POST':
        form = AddReviewForm(request.POST)
        if form.is_valid():
            ParkReview = form.save()
            ParkReview.refresh_from_db()
            ParkReview.user = request.user
            ParkReview.review = form.cleaned_data.get('review')
            ParkReview.star_rating = form.cleaned_data.get('star_rating')
            ParkReview.save()
            park.reviews.add(ParkReview)
            return redirect('index')
    else:
        form = AddReviewForm()
    return render(request, 'app/review.html', {'form': form})

def schedule(request, parkid):
    return HttpResponse("Schedule for Park ID: "+str(parkid)+" Here")


@login_required(login_url='login')
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.userprofile)  # request.FILES is show the selected image or file

        if form.is_valid() and profile_form.is_valid():
            user_form = form.save()
            custom_form = profile_form.save(False)
            custom_form.user = user_form
            custom_form.save()
            return redirect('index')
    else:
        form = EditProfileForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.userprofile)
        args = {}
        # args.update(csrf(request))
        args['form'] = form 
        args['profile_form'] = profile_form
        return render(request, 'app/edit_profile.html', args)