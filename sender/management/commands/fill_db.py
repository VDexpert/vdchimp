from django.core.management import BaseCommand
from sender.models import LetterMailing, ConfigMailing, Post, User
from sender.utils import plugs, translit


class Command(BaseCommand):

    def handle(self, *args, **options):
        configs_dump = [
            {'user': User.objects.get(id=1), 'title': 'Рассыка акции1', 'mail_dump': 'txt/mail_dump.txt'},
            {'user': User.objects.get(id=2), 'title': 'Рассыка акции2', 'mail_dump': 'txt/mail_dump.txt'},
            {'user': User.objects.get(id=3), 'title': 'Рассыка акции3', 'mail_dump': 'txt/mail_dump.txt'},
            {'user': User.objects.get(id=1), 'title': 'Рассыка акции4', 'mail_dump': 'txt/mail_dump.txt'},
            {'user': User.objects.get(id=2), 'title': 'Рассыка акции5', 'mail_dump': 'txt/mail_dump.txt'},
            {'user': User.objects.get(id=3), 'title': 'Рассыка акции6', 'mail_dump': 'txt/mail_dump.txt'},
            {'user': User.objects.get(id=1), 'title': 'Рассыка акции7', 'mail_dump': 'txt/mail_dump.txt'},
            {'user': User.objects.get(id=2), 'title': 'Рассыка акции8', 'mail_dump': 'txt/mail_dump.txt'},
            {'user': User.objects.get(id=3), 'title': 'Рассыка акции9', 'mail_dump': 'txt/mail_dump.txt'},
        ]

        configs = []
        for item in configs_dump:
            configs.append(ConfigMailing(user=item['user'], title=item['title']))

        ConfigMailing.objects.bulk_create(configs)

        letters_dump = [
            {'user': User.objects.get(id=1), 'title': 'Скидка 50%', 'position': 10,
             'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=1)},
            {'user': User.objects.get(id=2), 'title': 'Скидка 50%', 'position': 20,
             'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=1)},
            {'user': User.objects.get(id=3), 'title': 'Скидка 50%', 'position': 30,
             'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=1)},
            {'user': User.objects.get(id=1), 'title': 'Скидка 50%', 'position': 10,
             'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=2)},
            {'user': User.objects.get(id=2), 'title': 'Скидка 50%', 'position': 20,
             'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=2)},
            {'user': User.objects.get(id=3), 'title': 'Скидка 50%', 'position': 30,
             'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=2)},
            {'user': User.objects.get(id=1), 'title': 'Скидка 50%', 'position': 10,
             'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=3)},
            {'user': User.objects.get(id=2), 'title': 'Скидка 50%', 'position': 20,
             'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=3)},
            {'user': User.objects.get(id=3), 'title': 'Скидка 50%', 'position': 30,
             'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=3)},
        ]

        letters = []
        for item in letters_dump:
            letters.append(LetterMailing(user=item['user'], title=item['title'], position=item['position'],
                                         content=item['content'], mailing=item['mailing']))

        LetterMailing.objects.bulk_create(letters)

        posts = [
            {'title': 'Сколько средств вы должны выделить на ERP?',
             'slug': translit.do('Сколько средств вы должны выделить на ERP?'), 'content': plugs.text()},
            {'title': '5 лучших программ для управления бухгалтерскими документами', 'content': plugs.text(),
             'slug': translit.do('5 лучших программ для управления бухгалтерскими документами')},
            {'title': 'Топ-5 программных продуктов ERP с открытым исходным кодом', 'content': plugs.text(),
             'slug': translit.do('Топ-5 программных продуктов ERP с открытым исходным кодом')},
            {'title': 'Электронный документооборот (ЭДО): какие бывают виды, как работает, особенности, функции','content': plugs.text(),
             'slug': translit.do('Электронный документооборот (ЭДО): какие бывают виды, как работает, особенности, функции')},
            {'title': 'CRM-системы для малого бизнеса: какую выбрать, обзор лучших', 'content': plugs.text(),
             'slug': translit.do('CRM-системы для малого бизнеса: какую выбрать, обзор лучших')},
            {'title': 'Как перейти на электронный документооборот (ЭДО)', 'content': plugs.text(),
             'slug': translit.do('Как перейти на электронный документооборот (ЭДО)')},
            {'title': 'CRM-системы для агентства недвижимости: лучшие программы для риэлторов','content': plugs.text(),
             'slug': translit.do('CRM-системы для агентства недвижимости: лучшие программы для риэлторов')},
            {'title': 'Система электронного документооборота EDI: платформа для обмена данными', 'content': plugs.text(),
             'slug': translit.do('Система электронного документооборота EDI: платформа для обмена данными')},
            {'title': 'Бухгалтерские программы: список программного обеспечения для ведения бухгалтерии','content': plugs.text(),
             'slug': translit.do('Бухгалтерские программы: список программного обеспечения для ведения бухгалтерии')}
        ]
        post_list = []
        for i in range(11):
            for item in posts:
                post_list.append(
                    Post(title=f'''{item['title']}-{i}''', content=item['content'], slug=f'''{item['slug']}-{i}'''))

        Post.objects.bulk_create(post_list)

