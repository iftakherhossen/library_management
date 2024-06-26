from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .constants import GENDER, ACCOUNT_TYPE
from .models import UserAccount

class UserRegistrationForm(UserCreationForm):
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    birthday = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender = forms.ChoiceField(choices=GENDER)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'account_type', 'gender', 'birthday', 'password1', 'password2']
        
    def save(self, commit=True):
        user = super().save(commit=False)
        
        if commit == True:
            user.save()
            account_type = self.cleaned_data.get('account_type')
            birthday = self.cleaned_data.get('birthday')
            gender = self.cleaned_data.get('gender')              
            
            UserAccount.objects.create(
                user = user,
                account_type = account_type,
                birthday = birthday,                
                gender = gender,
                account_no = 10258000 + user.id
            )
            
        return user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500 mt-2 '
                )
            })
            
class UpdateUserProfileForm(forms.ModelForm):
    birthday = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender = forms.ChoiceField(choices=GENDER)
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500 mt-2 '
                )
            })
            
            if self.instance:
                try:
                    user_account = self.instance.account
                except UserAccount.DoesNotExist:
                    user_account = None
                    
                if user_account:
                    self.fields['account_type'].initial = user_account.account_type
                    self.fields['birthday'].initial = user_account.birthday
                    self.fields['gender'].initial = user_account.gender
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user_account, created = UserAccount.objects.get_or_create(user=user)    
            user_account.account_type = self.cleaned_data['account_type']              
            user_account.birthday = self.cleaned_data['birthday']
            user_account.gender = self.cleaned_data['gender']
            user_account.save()

        return user