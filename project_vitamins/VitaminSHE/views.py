from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, 'VitaminSHE/home.html')

def signup(request):
    return render(request, 'VitaminSHE/signup.html')

def login(request):
    return render(request, 'VitaminSHE/login.html')

def healthcheck(request):
    return render(request, 'VitaminSHE/healthcheck.html')

def food(request):
    return render(request, 'VitaminSHE/food.html')

def book(request):
    return render(request, 'VitaminSHE/book.html')

def why(request):
    return render(request, 'VitaminSHE/why.html')
