from django.core.management import BaseCommand
from sender.models import LetterMailing, ConfigMailing, Post, User
from sender.utils import plugs, translit


class Command(BaseCommand):

    def handle(self, *args, **options):
        # configs_dump = [
        #     {'user': User.objects.get(id=1), 'title': 'Рассыка акции1'},
        #     {'user': User.objects.get(id=2), 'title': 'Рассыка акции2'},
        #     {'user': User.objects.get(id=3), 'title': 'Рассыка акции3'},
        #     {'user': User.objects.get(id=1), 'title': 'Рассыка акции4'},
        #     {'user': User.objects.get(id=2), 'title': 'Рассыка акции5'},
        #     {'user': User.objects.get(id=3), 'title': 'Рассыка акции6'},
        #     {'user': User.objects.get(id=1), 'title': 'Рассыка акции7'},
        #     {'user': User.objects.get(id=2), 'title': 'Рассыка акции8'},
        #     {'user': User.objects.get(id=3), 'title': 'Рассыка акции9'},
        # ]
        #
        # configs = []
        # for item in configs_dump:
        #     configs.append(ConfigMailing(user=item['user'], title=item['title']))
        #
        # ConfigMailing.objects.bulk_create(configs)
        #
        # letters_dump = [
        #     {'user': User.objects.get(id=1), 'title': 'Скидка 50%', 'position': 10,
        #      'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=1)},
        #     {'user': User.objects.get(id=2), 'title': 'Скидка 50%', 'position': 20,
        #      'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=1)},
        #     {'user': User.objects.get(id=3), 'title': 'Скидка 50%', 'position': 30,
        #      'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=1)},
        #     {'user': User.objects.get(id=1), 'title': 'Скидка 50%', 'position': 10,
        #      'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=2)},
        #     {'user': User.objects.get(id=2), 'title': 'Скидка 50%', 'position': 20,
        #      'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=2)},
        #     {'user': User.objects.get(id=3), 'title': 'Скидка 50%', 'position': 30,
        #      'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=2)},
        #     {'user': User.objects.get(id=1), 'title': 'Скидка 50%', 'position': 10,
        #      'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=3)},
        #     {'user': User.objects.get(id=2), 'title': 'Скидка 50%', 'position': 20,
        #      'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=3)},
        #     {'user': User.objects.get(id=3), 'title': 'Скидка 50%', 'position': 30,
        #      'content': plugs.text(), 'mailing': ConfigMailing.objects.get(id=3)},
        # ]
        #
        # letters = []
        # for item in letters_dump:
        #     letters.append(LetterMailing(user=item['user'], title=item['title'], position=item['position'],
        #                                  content=item['content'], mailing=item['mailing']))
        #
        # LetterMailing.objects.bulk_create(letters)

        posts = [
            {'title': 'Как выбрать день и время для рассылки',
             'slug': translit.do('Как выбрать день и время для рассылки'), 'content': plugs.text()},
            {'title': 'Что писать в теме email-рассылки: исчерпывающее руководство', 'content': plugs.text(),
             'slug': translit.do('Что писать в теме email-рассылки: исчерпывающее руководство')},
            {'title': 'Как персонализировать рассылки, чтобы продавать больше', 'content': plugs.text(),
             'slug': translit.do('Как персонализировать рассылки, чтобы продавать больше')},
            {'title': 'Главный после темы: как правильно настроить прехедер письма','content': plugs.text(),
             'slug': translit.do('Главный после темы: как правильно настроить прехедер письма')},
            {'title': 'Что написать в поле «От кого». Гид по имени отправителя в рассылках', 'content': plugs.text(),
             'slug': translit.do('Что написать в поле «От кого». Гид по имени отправителя в рассылках')},
            {'title': 'Как сегментировать базу: 6 критериев с примерами', 'content': plugs.text(),
             'slug': translit.do('Как сегментировать базу: 6 критериев с примерами')},
            {'title': 'Что такое RFM-анализ и как его использовать','content': plugs.text(),
             'slug': translit.do('Что такое RFM-анализ и как его использовать')},
            {'title': 'Триггерные email-рассылки: путеводитель для новичков', 'content': plugs.text(),
             'slug': translit.do('Триггерные email-рассылки: путеводитель для новичков')},
            {'title': 'Автоворонка продаж. Как все устроено','content': plugs.text(),
             'slug': translit.do('Автоворонка продаж. Как все устроено')}
        ]
        post_list = []
        for i in range(11):
            for item in posts:
                post_list.append(
                    Post(title=f'''{item['title']}-{i}''', content=item['content'], slug=f'''{item['slug']}-{i}'''))

        Post.objects.bulk_create(post_list)

