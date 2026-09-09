from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import PatientRegistrationForm, UserUpdateForm, PatientProfileForm
from .models import CustomUser

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().username}!")
        return super().form_valid(form)


def register_patient(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard_redirect')

    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully! Welcome to the Hospital Portal.")
            return redirect('core:dashboard_redirect')
    else:
        form = PatientRegistrationForm()

    return render(request, 'accounts/register_patient.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('core:home')


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        patient_form = None
        if user.is_patient:
            patient_profile, _ = user.patient_profile.get_or_create(user=user)
            patient_form = PatientProfileForm(request.POST, instance=patient_profile)

        if user_form.is_valid() and (not patient_form or patient_form.is_valid()):
            user_form.save()
            if patient_form:
                patient_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=user)
        patient_form = PatientProfileForm(instance=user.patient_profile) if user.is_patient and hasattr(user, 'patient_profile') else None

    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'patient_form': patient_form
    })
