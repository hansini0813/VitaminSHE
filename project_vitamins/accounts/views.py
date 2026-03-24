from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from .forms import OnboardingForm, ProfileUpdateForm, SignUpForm
from .models import UserProfile


def account_home(request):
    if request.user.is_authenticated:
        return redirect("dashboard:index")
    return redirect("accounts:login")


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:index")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account was created. Complete onboarding to continue.")
            return redirect("accounts:onboarding")
    else:
        form = SignUpForm()

    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:index")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            profile = getattr(user, "profile", None)
            if profile and profile.onboarding_status == UserProfile.OnboardingStatus.PENDING:
                messages.info(request, "Finish onboarding before using the dashboard.")
                return redirect("accounts:onboarding")
            return redirect("dashboard:index")
    else:
        form = AuthenticationForm(request)

    return render(request, "accounts/login.html", {"form": form})


@login_required
def onboarding_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = OnboardingForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Onboarding completed.")
            return redirect("dashboard:index")
    else:
        form = OnboardingForm(instance=profile, user=request.user)

    return render(request, "accounts/onboarding.html", {"form": form})


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, "accounts/profile.html", {"form": form, "profile": profile})


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect("accounts:login")
