# Generated by Django 4.1.5 on 2023-03-01 00:35

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Почта')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Телефон')),
                ('country', models.CharField(blank=True, max_length=30, null=True, verbose_name='Страна')),
                ('email_verify', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ConfigMailing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название рассылки')),
                ('hour', models.IntegerField(default=12, verbose_name='Час')),
                ('minute', models.IntegerField(default=0, verbose_name='Минуты')),
                ('periodicity', models.CharField(choices=[('Каждый день', 'Каждый день'), ('Один/несколько дней в неделю', 'Один/несколько дней в неделю'), ('Один/несколько дней в месяц', 'Один/несколько дней в месяц')], default='Каждый день', max_length=40, verbose_name='График')),
                ('mail_dump', models.FileField(blank=True, null=True, upload_to='maildumps/1/', verbose_name='База рассылки в формате .txt')),
                ('status', models.CharField(choices=[('Завершена', 'Завершена'), ('Создана', 'Создана'), ('Запущена', 'Запущена')], default='Создана', max_length=20, verbose_name='Статус')),
                ('weekdays', models.CharField(blank=True, max_length=20, null=True, verbose_name='Дни недели cron-формат')),
                ('weekdays_text', models.CharField(blank=True, max_length=100, null=True, verbose_name='Дни недели текст')),
                ('monthdates', models.CharField(blank=True, max_length=100, null=True, verbose_name='Дни месяца')),
                ('from_email', models.EmailField(blank=True, default=None, max_length=254, null=True, verbose_name='Email рассылки')),
                ('password_user_from_email', models.CharField(blank=True, max_length=300, null=True, verbose_name='Пароль от почты пользвоателя')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Клиент')),
            ],
            options={
                'verbose_name': 'рассылка',
                'verbose_name_plural': 'рассылки',
            },
        ),
        migrations.CreateModel(
            name='LetterMailing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='Тема письма')),
                ('content', models.TextField(verbose_name='Содержание письма')),
                ('position', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(10), django.core.validators.MaxValueValidator(5000000)], verbose_name='Очередь на отправку')),
                ('status', models.CharField(choices=[('Отправлено', 'Отправлено'), ('Ожидает отправки', 'Ожидает отправки')], default='Ожидает отправки', max_length=20, verbose_name='Статус отправки')),
                ('mailing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sender.configmailing', verbose_name='Рассылка')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Логин клиента')),
            ],
            options={
                'verbose_name': 'письмо',
                'verbose_name_plural': 'письма',
            },
        ),
        migrations.CreateModel(
            name='TryMailing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time_try', models.DateTimeField(auto_now=True, verbose_name='Дата и время последней попытки')),
                ('mail_server_respond', models.CharField(blank=True, max_length=500, null=True, verbose_name='Ответ почтового сервера')),
                ('count_try', models.SmallIntegerField(default=0, verbose_name='Количество попыток')),
                ('letter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sender.lettermailing', verbose_name='Отправленное письмо')),
                ('mailing', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sender.configmailing', verbose_name='Рассылка')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Логин клиента')),
            ],
            options={
                'verbose_name': 'попытка',
                'verbose_name_plural': 'попытки',
            },
        ),
    ]
