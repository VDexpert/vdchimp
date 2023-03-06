from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from sender.forms_mixin import StyleFormMixin
from sender.models import User, LetterMailing, Blog, ConfigMailing
from sender.utils import custom_send_mail


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
    monday = forms.CharField(max_length=12, label='понедельник')
    tuesday = forms.CharField(max_length=12, label='вторник')
    wednesday = forms.CharField(max_length=12, label='среда')
    thursday = forms.CharField(max_length=12, label='четверг')
    friday = forms.CharField(max_length=12, label='пятница')
    saturday = forms.CharField(max_length=12, label='суббота')
    sunday = forms.CharField(max_length=12, label='воскресенье')


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


class FeedbackForm(StyleFormMixin, forms.Form):
    name = forms.CharField(max_length=50, label='Ваше имя', widget=forms.TextInput)
    email = forms.EmailField(max_length=50, label='Email для ответа', widget=forms.EmailInput)
    message = forms.CharField(widget=forms.Textarea(attrs={'cols': 60, 'rows': 3}), label="Ваше сообщение", required=True)


class CustomAuthenticationForm(AuthenticationForm):

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        try:
            User.objects.all().get(email=email)

        except ObjectDoesNotExist:
            self.add_error('username','У Вас нет аккаунта на портале. Перейдите по ссылке "Регистрация" внизу формы')

        else:

            if User.objects.all().get(email=email).banned == User.BANNED_TRUE:
                self.add_error('username','''Вам отказано в доступе, т.к. Вы были забанены за грубые нарушения правил сервиса''')
                return False

            if email is not None and password:
                self.user_cache = authenticate(self.request, email=email, password=password,)

                if self.user_cache is None:
                    self.add_error('username', '''Пароль введен неправильно''')
                    return False

                if not self.user_cache.email_verify:
                    custom_send_mail.verify(self.request, self.user_cache)
                    self.add_error('username', '''Ваша регистрация не была завершена, мы отправили Вам письмо с завершением регистрации - проверьте почту''')
                    return False

                else:
                    self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class CustomPasswordResetForm(StyleFormMixin, forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))

    def clean_email(self):
        email = self.cleaned_data['email']

        try:
            user = User.objects.all().get(email=email)

        except User.DoesNotExist:
            self.add_error('email', 'У Вас нет аккаунта на портале. Перейдите по ссылке "Регистрация" внизу формы')

        else:

            if not user.email_verify:
                self.add_error('email', '''Ваша регистрация не была завершена, мы отправили Вам письмо с завершением регистрации - проверьте почту''')
                return False

            return email


class UpdateBlogForm(StyleFormMixin, forms.ModelForm):

    class Meta:
        model = Blog
        fields = '__all__'

    def clean_blog_h1(self):
        blog_h1 = self.cleaned_data['blog_h1']

        if not blog_h1:
            raise ValidationError(f'''Поле '{self.fields['blog_h1'].label}' - обязательное''')

        return blog_h1

    def clean_blog_annotation(self):
        blog_annotation = self.cleaned_data['blog_annotation']

        if not blog_annotation:
            raise ValidationError(f'''Поле '{self.fields['blog_annotation'].label}' - обязательное''')

        return blog_annotation

    def clean_title(self):
        title = self.cleaned_data['title']

        if not title:
            raise ValidationError(f'''Поле '{self.fields['title'].label}' - обязательное''')

        return title


class ConfigMailingBannedForm(StyleFormMixin, forms.ModelForm):
    reason_ban = forms.CharField(label='Причина блокировки', max_length=500, help_text='поле обязательное - это будет отправлено разработчику', required=True)

    class Meta:
        model = ConfigMailing
        fields = ('banned',)


class UserBannedForm(StyleFormMixin, forms.ModelForm):
    reason_ban = forms.CharField(label='Причина блокировки', max_length=500, help_text='поле обязательное - это будет отправлено разработчику', required=True)

    class Meta:
        model = User
        fields = ('banned',)


class UserCommentForm(StyleFormMixin, forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs={'cols': 60, 'rows': 3}), required=False, label='Комментарий', max_length=100)
