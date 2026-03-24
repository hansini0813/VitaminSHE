from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm

def home(request):
    return render(request, 'VitaminSHE/home.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('home')  # Change 'home' to your home page route name
    else:
        form = SignUpForm()
    return render(request, 'VitaminSHE/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Change 'home' to your home page route name
    else:
        form = AuthenticationForm()
    return render(request, 'VitaminSHE/login.html', {'form': form})

def healthcheck(request):
    return render(request, 'VitaminSHE/healthcheck.html')

def food(request):
    return render(request, 'VitaminSHE/food.html')

def book(request):
    return render(request, 'VitaminSHE/book.html')

def why(request):
    return render(request, 'VitaminSHE/why.html')
