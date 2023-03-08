import os
from datetime import timezone
from smtplib import SMTPException
from django.core.mail import send_mail
from django.core.management import BaseCommand
from sender.models import LetterMailing, TryMailing, ConfigMailing, User
from django.utils import timezone


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-u',
                            '--user',
                            type=int,
                            default=False,
                            help='ID user')
        parser.add_argument('-m',
                            '--mailing',
                            type=int,
                            default=False,
                            help='ID mailing')

    def handle(self, *args, **options):
        user = User.objects.all().get(id=options['user'])
        mailing = ConfigMailing.objects.all().get(id=options['mailing'])

        if mailing.banned != ConfigMailing.BANNED_TRUE and mailing.from_email and mailing.password_from_email:
            print('\nИнициализация крона')
            letters = sorted(LetterMailing.objects.all().filter(mailing=mailing, status=LetterMailing.STATUS_WAIT))

            if len(letters):
                sent_letter = letters[0]
                subject = sent_letter.title
                message = sent_letter.content
                current_try = TryMailing.objects.all().filter(mailing=mailing).first()

                if not current_try:
                    print(f'\n\nИнициализация попытки\nПользователь: {user.email}\nID рассылки: {mailing.pk}\nВремя сервера {timezone.now()}\nВремя рассылки: {mailing.hour}:{mailing.minute}')
                    current_try = TryMailing.objects.create(user=user, mailing=mailing, letter=sent_letter)
                    mailing.status = 'Запущена'
                    mailing.save()

                recipient_list = []
                with open(mailing.mail_dump.path, 'r') as clients:
                    for client in clients:
                        recipient_list.append(client.encode('utf-8'))
                try:
                    if len(recipient_list):
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=mailing.from_email,
                            auth_password=mailing.password_from_email,
                            recipient_list=recipient_list
                        )
                    else:
                        print('База рассылки пустая')

                except SMTPException as e:
                    current_try.mail_server_respond = e
                    current_try.count_try += 1
                    current_try.save()

                else:
                    if len(recipient_list):
                        print('Успешная попытка')
                        success_sent = 'Письмо успешно отправлено'
                        current_try.count_try += 1
                        current_try.mail_server_respond = success_sent
                        current_try.letter = sent_letter
                        current_try.save()

                        if len(letters) == 1:
                            print('''Последнее письмо. Смена статуса рассылки на "Завершена" и удаление крона''')
                            mailing.status = ConfigMailing.STATUS_DONE
                            mailing.save()
                            path_project = '/'.join(os.path.abspath('manage.py').split('/')[3:-1])
                            cmd = f'cd {path_project} && myvenv/bin/python3 manage.py send_by_cron -u {user.pk} -m {mailing.pk} >> log_cronjobs.txt'''
                            os.system(f'''crontab -l | grep -v -F "{cmd}" | crontab -''')
                            print(f'path-to-manage-py {path_project}')

                        sent_letter.status = LetterMailing.STATUS_SENT
                        sent_letter.save()
                        print('Успешное завершение крона')
        else:
            password_exist = 'Задан' if mailing.password_from_email else 'Не задан'
            print(f'\nОшибка инициализации крона: {timezone.now()}\nID рассылки: {mailing.pk}\nПользователь: {mailing.user.email}\nПочта рассылки: {mailing.from_email}\nПароль от почты: {password_exist}')