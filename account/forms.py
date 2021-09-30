from django.core.exceptions import ValidationError
from blog.models import Article
from .models import (
    ContactsUser,
    Message,
    NotificationAdminCenter,
    UserProfile
    )
from django import forms


class UserLoginForm(forms.Form):
    username = forms.CharField(required=True, max_length=50, label="نام کاربری")
    email = forms.EmailField(required=True, max_length=70, label="آدرس ایمیل")
    password = forms.CharField(widget=forms.PasswordInput(),required=True, label="کلمه عبور")
    remember_me = forms.CheckboxInput()


class UserSetPassword(forms.Form):
    raw_password = forms.CharField(widget=forms.PasswordInput(), label="رمزعبور")
    password_confirm = forms.CharField(widget=forms.PasswordInput(), label="تکرار رمزعبور")

    def clean(self):
        cd = self.cleaned_data
        password1 = cd.get("raw_password")
        password2 = cd.get("password_confirm")
        if password1 != password2:
            raise ValidationError("پسورد ها متفاوت اند.")
        return cd


class UserRegistrationForm(forms.Form):
    email = forms.EmailField(required=True, max_length=100, label="آدرس ایمیل")
    username = forms.CharField(max_length=50, label="نام کاربری")


class UpdateUserAccountForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
    
        super(UpdateUserAccountForm, self).__init__(*args, **kwargs)

        if not self.user.is_superuser:

            self.fields['is_author'].disabled = True
            self.fields['can_send_message'].disabled = True
            self.fields['email'].disabled = True
            self.fields['username'].disabled = True

    class Meta:
        model = UserProfile
        fields = [
            'profile_pic',
            'first_name',
            'last_name',
            'email',
            'username',
            'phone',
            'short_about',
            'about',
            'is_author',
            'can_send_message',
        ]


class CreateUserContactsForm(forms.ModelForm):
    class Meta:
        model = ContactsUser
        fields = [
            'title',
            'url'
        ]


class UpdateUserContactsForm(forms.ModelForm):
    class Meta:
        model = ContactsUser
        fields = [
            'title',
            'url'
        ]


class CreateArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            'title',
            'slug',
            'image',
            'video',
            'text',
            'category',
            'login_required',
        ]


class UpdateUserArticleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')

        super(UpdateUserArticleForm, self).__init__(*args, **kwargs)

        if not self.user.is_superuser:
            self.fields['published'].disabled = True
            self.fields['hits'].disabled = True
            self.fields['back_description'].disabled = True

    class Meta:
        model = Article
        fields = [
            'title',
            'slug',
            'image',
            'video',
            'text',
            'category',
            'login_required',
            'hits',
            'back_description',
            'published',        
        ]


class AgainEmailConfirmationForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput)


class NotificationCreatorForm(forms.ModelForm):
    expr_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'date'}))

    class Meta:
        model = NotificationAdminCenter
        fields = [
            'title',
            'text',
            'read',
            'expr_date'
        ]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = [
            'title',
            'text',
            'to_user',
        ]
