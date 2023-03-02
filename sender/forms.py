from django.contrib.auth.forms import UserCreationForm
from django import forms
from sender.forms_mixin import StyleFormMixin
from sender.models import User, LetterMailing


class RegisterUserForm(StyleFormMixin, UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')


class LetterCreateForm(StyleFormMixin, forms.ModelForm):

    class Meta:
        model = LetterMailing
        exclude = ('user', 'mailing', 'status', 'position')


class LetterUpdateForm(StyleFormMixin, forms.ModelForm):

    class Meta:
        model = LetterMailing
        fields = ('title', 'position', 'content')


class UpdateWeekdayForm(StyleFormMixin, forms.Form):
    sunday = forms.CharField(max_length=12, label='воскресенье')
    monday = forms.CharField(max_length=12, label='понедельник')
    tuesday = forms.CharField(max_length=12, label='вторник')
    wednesday = forms.CharField(max_length=12, label='среда')
    thursday = forms.CharField(max_length=12, label='четверг')
    friday = forms.CharField(max_length=12, label='пятница')
    saturday = forms.CharField(max_length=12, label='суббота')


class UpdateMonthdateForm(StyleFormMixin, forms.Form):
    num_1 = forms.CharField(max_length=5)
    num_2 = forms.CharField(max_length=5)
    num_3 = forms.CharField(max_length=5)
    num_4 = forms.CharField(max_length=5)
    num_5 = forms.CharField(max_length=5)
    num_6 = forms.CharField(max_length=5)
    num_7 = forms.CharField(max_length=5)
    num_8 = forms.CharField(max_length=5)
    num_9 = forms.CharField(max_length=5)
    num_10 = forms.CharField(max_length=5)
    num_12 = forms.CharField(max_length=5)
    num_13 = forms.CharField(max_length=5)
    num_14 = forms.CharField(max_length=5)
    num_15 = forms.CharField(max_length=5)
    num_16 = forms.CharField(max_length=5)
    num_17 = forms.CharField(max_length=5)
    num_18 = forms.CharField(max_length=5)
    num_19 = forms.CharField(max_length=5)
    num_20 = forms.CharField(max_length=5)
    num_21 = forms.CharField(max_length=5)
    num_22 = forms.CharField(max_length=5)
    num_23 = forms.CharField(max_length=5)
    num_24 = forms.CharField(max_length=5)
    num_25 = forms.CharField(max_length=5)
    num_26 = forms.CharField(max_length=5)
    num_27 = forms.CharField(max_length=5)
    num_28 = forms.CharField(max_length=5)
    num_29 = forms.CharField(max_length=5)
    num_30 = forms.CharField(max_length=5)
    num_31 = forms.CharField(max_length=5)


