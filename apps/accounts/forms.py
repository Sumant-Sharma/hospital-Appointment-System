from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, PatientProfile

class PatientRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    gender = forms.ChoiceField(choices=CustomUser.GENDER_CHOICES, required=False)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    
    blood_group = forms.CharField(max_length=5, required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g. O+, A+'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
    emergency_contact = forms.CharField(max_length=20, required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'gender', 'date_of_birth')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.ROLE_PATIENT
        if commit:
            user.save()
            PatientProfile.objects.create(
                user=user,
                blood_group=self.cleaned_data.get('blood_group'),
                address=self.cleaned_data.get('address'),
                emergency_contact=self.cleaned_data.get('emergency_contact')
            )
        return user


class UserUpdateForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'gender', 'date_of_birth')


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ('blood_group', 'address', 'emergency_contact', 'medical_history_summary')
