# from django.contrib.auth import forms
# from django.contrib.auth import get_user_model
# from django.contrib.auth.forms import UserCreationForm


# User = get_user_model()


# # User Signup
# class UserCreateForm(UserCreationForm):
#     # password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
#     # password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'first_name', 'last_name']

#         widgets = {
#             'username': forms.TextInput(attrs={'class': 'form-control'}),
#             'first_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'last_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control'}),
#         }