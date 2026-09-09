from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.accounts.models import CustomUser
from .models import DoctorProfile, DoctorAvailability, Department

class AdminCreateDoctorForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True)
    specialization = forms.CharField(max_length=150, required=True)
    qualification = forms.CharField(max_length=150, required=True)
    experience_years = forms.IntegerField(min_value=0, initial=1)
    consultation_fee = forms.DecimalField(max_digits=10, decimal_places=2, initial=50.00)
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.ROLE_DOCTOR
        if commit:
            user.save()
            DoctorProfile.objects.create(
                user=user,
                department=self.cleaned_data['department'],
                specialization=self.cleaned_data['specialization'],
                qualification=self.cleaned_data['qualification'],
                experience_years=self.cleaned_data['experience_years'],
                consultation_fee=self.cleaned_data['consultation_fee'],
                bio=self.cleaned_data.get('bio', ''),
                profile_picture=self.cleaned_data.get('profile_picture')
            )
        return user


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ('department', 'specialization', 'qualification', 'experience_years', 'consultation_fee', 'bio', 'profile_picture', 'is_active')


class DoctorAvailabilityForm(forms.ModelForm):
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = DoctorAvailability
        fields = ('day_of_week', 'start_time', 'end_time', 'slot_duration_minutes', 'is_available')

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")
        return cleaned_data


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ('name', 'description', 'icon_class')
