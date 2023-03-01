from django.contrib.auth.models import User
from django.core.management import BaseCommand
from sender.models import TryMailing, LetterMailing, ConfigMailing
from sender.utils import plugs


class Command(BaseCommand):
    ConfigMailing.objects.all().delete()
    LetterMailing.objects.all().delete()
    TryMailing.objects.all().delete()

    def handle(self, *args, **options):
        configs_dump = [
            {'username': User.objects.get(username='v'), 'title': 'Рассыка акции1', 'mail_dump': 'txt/mail_dump.txt'},
            {'username': User.objects.get(username='v'), 'title': 'Рассыка акции2', 'mail_dump': 'txt/mail_dump.txt'},
            {'username': User.objects.get(username='v'), 'title': 'Рассыка акции3', 'mail_dump': 'txt/mail_dump.txt'},
            {'username': User.objects.get(username='vd'), 'title': 'Рассыка акции4', 'mail_dump': 'txt/mail_dump.txt'},
            {'username': User.objects.get(username='vd'), 'title': 'Рассыка акции5', 'mail_dump': 'txt/mail_dump.txt'},
            {'username': User.objects.get(username='vd'), 'title': 'Рассыка акции6', 'mail_dump': 'txt/mail_dump.txt'},
            {'username': User.objects.get(username='vdn'), 'title': 'Рассыка акции7', 'mail_dump': 'txt/mail_dump.txt'},
            {'username': User.objects.get(username='vdn'), 'title': 'Рассыка акции8', 'mail_dump': 'txt/mail_dump.txt'},
            {'username': User.objects.get(username='vdn'), 'title': 'Рассыка акции9', 'mail_dump': 'txt/mail_dump.txt'},
        ]

        configs = []
        for item in configs_dump:
            configs.append(ConfigMailing(username=item['username'], title=item['title'], mail_dump=item['mail_dump']))

        ConfigMailing.objects.bulk_create(configs)

        letters_dump = [
            {'username': User.objects.get(username='v'), 'title': 'Скидка 50%', 'position': 10,
             'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=1)},
            {'username': User.objects.get(username='v'), 'title': 'Скидка 50%', 'position': 20,
             'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=1)},
            {'username': User.objects.get(username='v'), 'title': 'Скидка 50%', 'position': 30,
             'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=1)},
            {'username': User.objects.get(username='vd'), 'title': 'Скидка 50%', 'position': 10,
             'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=2)},
            {'username': User.objects.get(username='vd'), 'title': 'Скидка 50%', 'position': 20,
             'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=2)},
            {'username': User.objects.get(username='vd'), 'title': 'Скидка 50%', 'position': 30,
             'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=2)},
            {'username': User.objects.get(username='vdn'), 'title': 'Скидка 50%', 'position': 10,
             'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=3)},
            {'username': User.objects.get(username='vdn'), 'title': 'Скидка 50%', 'position': 20,
             'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=3)},
            {'username': User.objects.get(username='vdn'), 'title': 'Скидка 50%', 'position': 30,
             'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=3)},
        ]

        letters = []
        for item in letters_dump:
            letters.append(LetterMailing(username=item['username'], title=item['title'], position=item['position'],
                                         content=item['content'], mailing=item['mailing']))

        LetterMailing.objects.bulk_create(letters)

        try_dump = [
            {'username': User.objects.get(username='v'), 'mailing': ConfigMailing.objects.all().get(id=1),
             'letter': LetterMailing.objects.all().get(id=1),'respond': 'Письмо успешно отправлено'},
            {'username': User.objects.get(username='v'), 'mailing': ConfigMailing.objects.all().get(id=2),
             'letter': LetterMailing.objects.all().get(id=2), 'respond': 'Письмо успешно отправлено'},
            {'username': User.objects.get(username='v'), 'mailing': ConfigMailing.objects.all().get(id=3),
             'letter': LetterMailing.objects.all().get(id=3), 'respond': 'Ошибка'}
        ]

        trials = []
        for item in try_dump:
            trials.append(TryMailing(username=item['username'], mailing=item['mailing'],
                       letter=item['letter'], mail_server_respond=item['respond']))

        TryMailing.objects.bulk_create(trials)
