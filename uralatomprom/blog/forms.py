from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from captcha.fields import CaptchaField
from .models import Post, Comment

User = get_user_model()


class ParticipantCreationForm(UserCreationForm):
    captcha = CaptchaField(label='Введите капчу')

    class Meta:
        model = User
        fields = ('username', 'is_speaker',
                  'full_name', 'organisation',
                  'phone', 'email',
                  'abstract', 'give_personal_data',)

    def clean(self):
        clean_data = super().clean()
        if r'[а-яА-ЯёЁ]' in clean_data.get('username'):
            raise forms.ValidationError('Имя пользователя должно содержать '
                                        'только английские буквы и цифры')
        if not clean_data.get('give_personal_data'):
            raise forms.ValidationError('Необходимо дать согласие '
                                        'на обработку персональных данных!')


class ParticipantChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('is_speaker', 'full_name', 'organisation',
                  'phone', 'email', 'abstract',)


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'})
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
