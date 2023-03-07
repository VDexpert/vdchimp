from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse_lazy
from django.contrib.auth.models import AbstractUser
from dotenv import load_dotenv
from config.settings import BASE_DIR
from tinymce import models as tinymce_models


NULLABLE = {'blank': True, 'null': True}

env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)


class User(AbstractUser):
    BANNED_TRUE = 'Заблокирован модератором'
    BANNED_FALSE = 'Не заблокирован'
    BANNED_STATUSES = (
        (BANNED_TRUE, 'ЗАБЛОКИРОВАТЬ'),
        (BANNED_FALSE, 'РАЗБЛОКИРОВАТЬ')
    )

    username = None
    email = models.EmailField(verbose_name='Почта', unique=True)
    phone = models.CharField(verbose_name='Телефон', max_length=20, **NULLABLE)
    country = models.CharField(verbose_name='Страна', max_length=30, **NULLABLE)
    email_verify = models.BooleanField(default=False)
    banned = models.CharField(choices=BANNED_STATUSES, default=BANNED_FALSE, max_length=30, verbose_name='Забанить пользователя?')
    comment = models.CharField(verbose_name='Комментарий пользователю', **NULLABLE, max_length=100)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta():
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        permissions = [
            ('view_and_ban_any_user', 'блокировать любого пользователя'),
        ]

    def get_absolute_url(self):
        return reverse_lazy('sender:mailing_detail', kwargs={'pk': self.pk})


class ConfigMailing(models.Model):
    count = 1

    STATUS_DONE = 'Завершена'
    STATUS_CREATED = 'Создана'
    STATUS_STARTED = 'Запущена'
    STATUS_MODERATING = 'Ожидает модерации'
    STATUSES = (
        (STATUS_DONE, 'Завершена'),
        (STATUS_CREATED, 'Создана'),
        (STATUS_STARTED, 'Запущена'),
        (STATUS_MODERATING, 'Ожидает модерации')
    )

    PERIOD_DAY = 'Каждый день'
    PERIOD_WEEK = 'Один или несколько дней в неделю'
    PERIOD_MONTH = 'Один или несколько дней в месяц'
    PERIODS = (
        (PERIOD_DAY, 'Каждый день'),
        (PERIOD_WEEK, 'Один или несколько дней в неделю'),
        (PERIOD_MONTH, 'Один или несколько дней в месяц')
    )
    PERIODS_TUPLE = ('Каждый день', 'Один или несколько дней в неделю', 'Один или несколько дней в месяц')

    BANNED_TRUE = 'ЗАБЛОКИРОВАНО МОДЕРАТОРОМ'
    BANNED_FALSE = 'одобрено модератором'
    BANNED_STATUSES = (
        (BANNED_TRUE, 'ЗАБАНИТЬ'),
        (BANNED_FALSE, 'РАЗБАНИТЬ')
    )

    user = models.ForeignKey('User', verbose_name='Клиент', on_delete=models.CASCADE, **NULLABLE)
    title = models.CharField(verbose_name='Название рассылки', max_length=100, help_text='максимальное количество символов - 100')
    hour = models.IntegerField(verbose_name='Час', default=12)
    minute = models.IntegerField(verbose_name='Минуты', default=0)
    periodicity = models.CharField(choices=PERIODS, default=PERIOD_DAY, max_length=40, verbose_name='График')
    mail_dump = models.FileField(verbose_name='База рассылки в формате .txt', upload_to=f'maildumps/{count}/', **NULLABLE)
    status = models.CharField(choices=STATUSES, default=STATUS_CREATED, max_length=20, verbose_name='Статус')
    weekdays = models.CharField(verbose_name='Дни недели cron-формат', max_length=20, **NULLABLE)
    weekdays_text = models.CharField(verbose_name='Дни недели текст', max_length=100, **NULLABLE)
    monthdates = models.CharField(verbose_name='Дни месяца cron-формат', max_length=100, **NULLABLE)
    monthdates_text = models.CharField(verbose_name='Дни месяца с пробелами', max_length=100, **NULLABLE)
    from_email = models.EmailField(verbose_name='Email рассылки', unique=False, **NULLABLE)
    password_from_email = models.CharField(max_length=150, verbose_name='Пароль от почты рассылки', **NULLABLE)
    banned = models.CharField(choices=BANNED_STATUSES, default=BANNED_FALSE, max_length=30, verbose_name='Забанить пост?')
    create_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True, **NULLABLE)


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
        permissions = [
            ('view_and_ban_any_mailing', 'блокировать любую рассылку'),
        ]


class LetterMailing(models.Model):
    STATUS_SENT = 'Отправлено'
    STATUS_WAIT = 'В ожидании'
    STATUSES = (
        (STATUS_SENT, 'Отправлено'),
        (STATUS_WAIT, 'Ожидает отправки')
    )

    user = models.ForeignKey('User', verbose_name='Логин клиента', on_delete=models.CASCADE, **NULLABLE)
    mailing = models.ForeignKey('ConfigMailing', verbose_name='Рассылка', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Тема письма', max_length=50, null=False, help_text='максимальное количество символов - 50')
    content = tinymce_models.HTMLField(verbose_name='Содержание', **NULLABLE)
    position = models.PositiveIntegerField(verbose_name='Очередь на отправку', **NULLABLE, validators=[MinValueValidator(10), MaxValueValidator(5000000)])
    status = models.CharField(verbose_name='Статус отправки', choices=STATUSES, default=STATUS_WAIT, max_length=20)

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


class Home(models.Model):
    home_h1 = models.CharField(max_length=100, verbose_name='Заголовок',  help_text='До 100 символов')
    home_annotation = models.CharField(max_length=150, verbose_name='Аннотация', help_text='До 150 символов')
    title = models.CharField(max_length=70, verbose_name='Метатэг Title', help_text='До 70 символов')
    description = tinymce_models.HTMLField(verbose_name='Содержание', **NULLABLE)
    annotation_advantages = models.CharField(max_length=100, verbose_name='Заголовок перед блоком преимуществ',
                                        **NULLABLE, help_text='До 100 символов')
    annotation_posts = models.CharField(max_length=100, verbose_name='Заголовок перед блоком случайных постов',
                                        **NULLABLE, help_text='До 100 символов')
    picture = models.ImageField(verbose_name='Картинка в шапке', upload_to='home/', **NULLABLE,
                                help_text='рекомендуемый размер - 2000*1000')
    count_all_mailings = models.IntegerField(verbose_name='Всего рассылок',
                                             help_text='Если поле пустое - берется автоматически из БД', **NULLABLE)
    count_active_mailings = models.IntegerField(verbose_name='Активных рассылок',
                                                help_text='Если поле пустое - берется автоматически из БД', **NULLABLE)
    count_users = models.IntegerField(verbose_name='Количество пользователей',
                                      help_text='Если поле пустое - берется автоматически из БД', **NULLABLE)
    meta_description = models.CharField(verbose_name='Метатэг description', max_length=300, **NULLABLE,
                                        help_text='До 300 символов')
    meta_keywords = models.CharField(max_length=150, verbose_name='Метатег Keywords', **NULLABLE,
                                     help_text='До 150 символов')

    class Meta():
        verbose_name = 'Главная страница'
        verbose_name_plural = 'Главная страница'


class AdvantagesHome(models.Model):
    STATUS_ACTIVE = 'опубликовано'
    STATUS_INACTIVE = 'не опубликовано'
    STATUSES = (
        (STATUS_ACTIVE, 'ДА'),
        (STATUS_INACTIVE, 'НЕТ')
    )

    title = models.CharField(max_length=50, verbose_name='Заголовок', help_text='До 50 символов')
    description = models.CharField(max_length=200, verbose_name='Содержание', help_text='До 200 символов')
    picture = models.ImageField(verbose_name='Картинка', upload_to='home/')
    status = models.CharField(choices=STATUSES, default=STATUS_ACTIVE, max_length=20, verbose_name='Публиковать?')

    class Meta():
        verbose_name = 'Преимущество на главной'
        verbose_name_plural = 'Преимущества на главной'


class Blog(models.Model):
    blog_h1 = models.CharField(max_length=100, verbose_name='Заголовок', **NULLABLE,  help_text='До 100 символов')
    blog_annotation = models.CharField(max_length=150, verbose_name='Аннотация', **NULLABLE, help_text='До 150 символов')
    title = models.CharField(max_length=70, verbose_name='Метатэг Title',  **NULLABLE,  help_text='До 70 символов')
    description = tinymce_models.HTMLField(verbose_name='Содержание',  **NULLABLE)
    meta_description = models.CharField(verbose_name='Метатэг Description', max_length=300, **NULLABLE, help_text='До 300 символов')
    meta_keywords = models.CharField(max_length=150, verbose_name='Метатег Keywords', **NULLABLE, help_text='До 150 символов')

    class Meta():
        verbose_name = 'Блог'
        verbose_name_plural = 'Блог'
        permissions = [
            ('content_management', 'Создавать статьи блога'),
        ]


class Contacts(models.Model):
    contacts_h1 = models.CharField(max_length=100, verbose_name='Заголовок', **NULLABLE,  help_text='До 100 символов')
    title = models.CharField(max_length=70, verbose_name='Метатэг Title', **NULLABLE,  help_text='До 70 символов')
    official_company_name = models.CharField(max_length=30, verbose_name='Юридическое название', **NULLABLE,  help_text='До 30 символов')
    country = models.CharField(max_length=20, verbose_name='Страна', **NULLABLE,  help_text='До 20 символов')
    itin = models.CharField(max_length=20, verbose_name='ИНН', **NULLABLE,  help_text='До 20 символов')
    address = models.CharField(max_length=50, verbose_name='Адрес', **NULLABLE,  help_text='До 50 символов')
    phone = models.CharField(max_length=30, verbose_name='Телефон', **NULLABLE,  help_text='До 30 символов')
    email = models.CharField(max_length=40, verbose_name='Email', **NULLABLE,  help_text='До 40 символов')
    meta_description = models.CharField(verbose_name='Метатэг Description', max_length=300, **NULLABLE, help_text='До 300 символов')
    meta_keywords = models.CharField(max_length=150, verbose_name='Метатег Keywords', **NULLABLE, help_text='До 150 символов')

    class Meta():
        verbose_name = 'Контакты'
        verbose_name_plural = 'Контакты'


class Post(models.Model):
    STATUS_ACTIVE = 'опубликовано'
    STATUS_INACTIVE = 'не опубликовано'
    STATUSES = (
        (STATUS_ACTIVE, 'ДА'),
        (STATUS_INACTIVE, 'НЕТ')
    )


    title = models.CharField(max_length=100, verbose_name='Заголовок', db_index=True, unique=True,  help_text='До 100 символов')
    slug = models.SlugField(max_length=100, verbose_name='URL',  db_index=True, unique=True, null=True)
    content = tinymce_models.HTMLField(verbose_name='Содержание', **NULLABLE)
    picture = models.ImageField(verbose_name='Фото', upload_to='posts/', **NULLABLE, help_text='рекомендуемый размер - 2000*1000')
    create_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    change_at = models.DateTimeField(verbose_name='Дата изменения', **NULLABLE)
    count_views = models.IntegerField(default=0, verbose_name='Количество просмотров')
    status = models.CharField(choices=STATUSES, default=STATUS_ACTIVE, max_length=20, verbose_name='Публиковать?')

    class Meta():
        verbose_name = 'публикация'
        verbose_name_plural = 'публикации'

    def __str__(self):
        return f'{self.title},{self.slug}, {self.create_at}, {self.change_at}, {self.count_views}, {self.status}'

    def get_absolute_url(self):
        return reverse_lazy('sender:post_list', kwargs={'slug': self.slug})


class Comment(models.Model):
    name_user = models.CharField(max_length=50, verbose_name='Если хотите, укажите Ваще имя или псевдоним', default='Гость')
    content = models.CharField(max_length=1000, verbose_name='Комментарий')
    post = models.ForeignKey('Post', on_delete=models.CASCADE)

    class Meta():
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
