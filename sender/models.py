import os
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse_lazy
from django.contrib.auth.models import AbstractUser
from dotenv import load_dotenv
from config.settings import BASE_DIR

NULLABLE = {'blank': True, 'null': True}

env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)


class User(AbstractUser):
    username = None
    email = models.EmailField(verbose_name='Почта', unique=True)
    phone = models.CharField(verbose_name='Телефон', max_length=20, **NULLABLE)
    country = models.CharField(verbose_name='Страна', max_length=30, **NULLABLE)
    email_verify = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class ConfigMailing(models.Model):
    count = 1

    DONE = 'Завершена'
    CREATED = 'Создана'
    STARTED = 'Запущена'
    MODERATING = 'Ожидает модерации'
    STATUSES = (
        (DONE, 'Завершена'),
        (CREATED, 'Создана'),
        (STARTED, 'Запущена'),
        (MODERATING, 'Ожидает модерации')
    )

    PERIOD_DAY = 'Каждый день'
    PERIOD_WEEK = 'Один/несколько дней в неделю'
    PERIOD_MONTH = 'Один/несколько дней в месяц'
    PERIODS = (
        (PERIOD_DAY, 'Каждый день'),
        (PERIOD_WEEK, 'Один/несколько дней в неделю'),
        (PERIOD_MONTH, 'Один/несколько дней в месяц')
    )
    PERIODS_TUPLE = ('Каждый день', 'Один/несколько дней в неделю', 'Один/несколько дней в месяц')

    user = models.ForeignKey('User', verbose_name='Клиент', on_delete=models.CASCADE, **NULLABLE)
    title = models.CharField(verbose_name='Название рассылки', max_length=100, help_text='максимальное количество символов - 100')
    hour = models.IntegerField(verbose_name='Час', default=12)
    minute = models.IntegerField(verbose_name='Минуты', default=0)
    periodicity = models.CharField(choices=PERIODS, default=PERIOD_DAY, max_length=40, verbose_name='График')
    mail_dump = models.FileField(verbose_name='База рассылки в формате .txt', upload_to=f'maildumps/{count}/', **NULLABLE)
    status = models.CharField(choices=STATUSES, default=CREATED, max_length=20, verbose_name='Статус')
    weekdays = models.CharField(verbose_name='Дни недели cron-формат', max_length=20, **NULLABLE)
    weekdays_text = models.CharField(verbose_name='Дни недели текст', max_length=100, **NULLABLE)
    monthdates = models.CharField(verbose_name='Дни месяца cron-формат', max_length=100, **NULLABLE)
    monthdates_text = models.CharField(verbose_name='Дни месяца с пробелами', max_length=100, **NULLABLE)
    from_email = models.EmailField(verbose_name='Email рассылки', unique=False, default=os.getenv('EMAIL_HOST_USER'), **NULLABLE)
    password_user_from_email = models.CharField(max_length=300, verbose_name='Пароль от почты пользвоателя', **NULLABLE)

    def __int__(self, *args, **kwargs):
        self.count += 1
        super().__init__(self, *args, **kwargs)

    def __str__(self):
        return f'{self.title}, {self.hour}, {self.minute}, {self.periodicity}, {self.mail_dump}, {self.status}'

    def get_absolute_url(self):
        return reverse_lazy('sender:mailing_detail', kwargs={'pk': self.pk})

    class Meta():
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'


class LetterMailing(models.Model):
    SENT = 'Отправлено'
    WAIT = 'В ожидании'
    STATUSES = (
        (SENT, 'Отправлено'),
        (WAIT, 'Ожидает отправки')
    )

    user = models.ForeignKey('User', verbose_name='Логин клиента', on_delete=models.CASCADE, **NULLABLE)
    mailing = models.ForeignKey('ConfigMailing', verbose_name='Рассылка', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Тема письма', max_length=50, null=False, help_text='максимальное количество символов - 50')
    content = models.TextField(verbose_name='Содержание письма', null=False)
    position = models.PositiveIntegerField(verbose_name='Очередь на отправку', **NULLABLE, validators=[MinValueValidator(10), MaxValueValidator(5000000)])
    status = models.CharField(verbose_name='Статус отправки', choices=STATUSES, default=WAIT, max_length=20)

    def __hash__(self):
        return hash(self.pk)

    def __lt__(self, other):
        return self.position < other

    def __gt__(self, other):
        return self.position > other

    def __eq__(self, other):
        return self.position == other

    def __ne__(self, other):
        return self.position != other

    def __str__(self):
        return f'{self.id}, {self.title}, {self.content}'

    def get_absolute_url(self):
        return reverse_lazy('sender:update_letter', kwargs={'mailing_pk': self.mailing.pk, 'letter_pk': self.pk, })

    class Meta():
        verbose_name = 'письмо'
        verbose_name_plural = 'письма'


class TryMailing(models.Model):
    user = models.ForeignKey('User', verbose_name='Логин клиента', on_delete=models.CASCADE, **NULLABLE)
    mailing = models.OneToOneField('ConfigMailing', verbose_name='Рассылка', **NULLABLE, on_delete=models.CASCADE)
    letter = models.ForeignKey('LetterMailing', verbose_name='Отправленное письмо', **NULLABLE, on_delete=models.CASCADE)
    date_time_try = models.DateTimeField(verbose_name='Дата и время последней попытки', auto_now=True)
    mail_server_respond = models.CharField(verbose_name='Ответ почтового сервера', **NULLABLE, max_length=500)
    count_try = models.SmallIntegerField(verbose_name='Количество попыток', default=0)

    def __str__(self):
        return f'{self.date_time_try}, {self.mail_server_respond}, {self.count_try}'

    class Meta():
        verbose_name = 'попытка'
        verbose_name_plural = 'попытки'