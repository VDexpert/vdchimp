import os
from smtplib import SMTPException
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import logout, login
from django.contrib.auth.models import Permission
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import redirect, render
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView, TemplateView
from config import settings
from sender.forms import *
from django.http import HttpResponseRedirect
from sender.models import*
from sender.utils import custom_send_mail, translit
from django.contrib.auth.tokens import default_token_generator as token_gen


weekdays_cron_dict = {
    'понедельник': '1', 'вторник': '2', 'среда': '3', 'четверг': '4',
    'пятница': '5', 'суббота': '6', 'воскресенье': '0'
}


def include_static_context():
    context = {}
    context['status_mailing_done'] = ConfigMailing.STATUS_DONE
    context['status_mailing_moderating'] = ConfigMailing.STATUS_MODERATING
    context['period_mailing_month'] = ConfigMailing.PERIOD_MONTH
    context['period_mailing_week'] = ConfigMailing.PERIOD_WEEK
    context['status_letter_sent'] = LetterMailing.STATUS_SENT
    context['status_letter_wait'] = LetterMailing.STATUS_WAIT
    context['periods'] = ConfigMailing.PERIODS_TUPLE
    context['hours'] = [x for x in range(0, 24)]
    context['minutes'] = [x for x in range(0, 60)]
    context['ban_mailing_true'] = ConfigMailing.BANNED_TRUE
    context['ban_mailing_false'] = ConfigMailing.BANNED_FALSE
    context['ban_user_true'] = User.BANNED_TRUE
    context['ban_user_false'] = User.BANNED_FALSE

    return context


class ConfigMailingDetailView(DetailView):
    '''
    Экземпляр данного класса служит прокси-объектом для передачи динамического контекста нескольким
    другим контроллерам, также основанным на модели ConfigMailing и контроллере DetailView
    '''
    model = ConfigMailing
    template_name = 'sender/mailing_detail_user.html'

    def include_user_and_static_context(self, obj, user):
        context = {}
        context['trials'] = TryMailing.objects.all().filter(user=user, mailing=obj)
        context['letters'] = LetterMailing.objects.all().filter(user=user, mailing=obj).order_by('position')
        context['sent_letters_count'] = LetterMailing.objects.all().filter(user=user, mailing=obj, status=LetterMailing.STATUS_SENT).count()
        context.update(include_static_context())

        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.include_user_and_static_context(self.get_object(), self.request.user))

        return context
'''прокси объект'''
proxy_mailing_detail = ConfigMailingDetailView()


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'sender/forms/registration.html'
    s = 'sender'
    get_perm = Permission.objects.get_by_natural_key

    user_permissions = [
        {'app': s, 'act': 'add_configmailing', 'mod': 'configmailing'}, {'app': s, 'act': 'change_configmailing', 'mod': 'configmailing'},
        {'app': s, 'act': 'view_configmailing', 'mod': 'configmailing'}, {'app': s, 'act': 'delete_configmailing', 'mod': 'configmailing'},
        {'app': s, 'act': 'add_lettermailing', 'mod': 'lettermailing'}, {'app': s, 'act': 'change_lettermailing', 'mod': 'lettermailing'},
        {'app': s, 'act': 'delete_lettermailing', 'mod': 'lettermailing'}, {'app': s, 'act': 'view_lettermailing', 'mod': 'lettermailing'},
    ]
    def get(self, request, *args, **kwargs):
        super().get(self, request, *args, **kwargs)

        if self.request.user.is_authenticated:
            return redirect('sender:profile')

        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=password)

            try:
                custom_send_mail.verify(request, user)

                for perm in self.user_permissions:
                    user.user_permissions.add(self.get_perm(codename=perm['act'], app_label=perm['app'], model=perm['mod']).pk)

            except SMTPException as e:
                os.system(f'echo {timezone.now()}, {e} >> register_errors.txt')

                return redirect('sender:some_error')

            else:
                return redirect('sender:confirm_email')

        context = {'form': form}

        return render(request, self.template_name, context)


class ConfirmEmailTemplateView(TemplateView):
    template_name = 'sender/service/confirm_email.html'

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            return redirect('sender:profile')

        return self.render_to_response(context)


class EmailVerifyView(View):

    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)

        if user is not None and token_gen.check_token(user, token):
            user.email_verify = True
            user.save()
            login(request, user)

            return redirect('sender:profile')

        return redirect('sender:invalid_verify')

    @staticmethod
    def get_user(uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None

        return user


class LoginUser(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'sender/forms/login.html'

    def get_success_url(self):
        user = self.request.user


        if user.has_perm('sender.view_and_ban_any_mailing'):
            return reverse_lazy('sender:moderating_mailings')

        if user.has_perm('sender.view_and_ban_any_user'):
            return reverse_lazy('sender:moderating_users')

        if user.has_perm('sender.management_category'):
            return reverse_lazy('sender:content_management_blog')

        return reverse_lazy('sender:profile')

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)

        if self.request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())

        return self.render_to_response(self.get_context_data())


def logout_user(request):
    logout(request)
    return redirect('sender:login')


class ListAndCreateConfigMailing(CreateView):
    model = ConfigMailing
    fields = ('title', 'hour', 'minute', 'periodicity', 'mail_dump')
    template_name = 'sender/mailing_list_user.html'
    success_url = reverse_lazy('sender:profile')

    def form_valid(self, form):
        self.object = form.save()
        user = self.request.user
        self.object.user = user
        self.object.save()

        if self.object.periodicity == self.model.PERIOD_DAY:
            path_project = '/'.join(os.path.abspath('manage.py').split('/')[3:-1])
            cmd = f'cd {path_project} && myvenv/bin/python3 manage.py send_by_cron -u {user.pk} -m {self.object.pk} >> log_cronjobs.txt'''
            start = 'crontab -l | { cat; echo '
            time = f'''"{self.object.minute} {self.object.hour} * * * '''
            cmd = f'{cmd}"; '
            end = '} | crontab -'
            os_cmd = start + time + cmd + end
            os.system(os_cmd)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_list"] = self.model.objects.all().filter(user=self.request.user.pk).order_by('-create_at')
        context['user'] = self.request.user
        context.update(include_static_context())

        return context


class ConfigMailingCreateViewMobile(CreateView):
    '''Для обработки операций создания рассылки со смартфонов и планшетов'''
    model = ConfigMailing
    template_name = 'sender/mailing_create_for_mobile.html'
    fields = ('title', 'from_email', 'hour', 'minute', 'periodicity', 'mail_dump')
    success_url = reverse_lazy('sender:profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(include_static_context())

        return context

    def form_valid(self, form):
        self.object = form.save()
        user = self.request.user
        self.object.user = user
        self.object.save()

        if self.object.periodicity == self.model.PERIOD_DAY:
            path_project = '/'.join(os.path.abspath('manage.py').split('/')[3:-1])
            cmd = f'cd {path_project} && myvenv/bin/python3 manage.py send_by_cron -u {user.pk} -m {self.object.pk} >> log_cronjobs.txt'''
            start = 'crontab -l | { cat; echo '
            time = f'''"{self.object.minute} {self.object.hour} * * * '''
            cmd = f'{cmd}"; '
            end = '} | crontab -'
            os_cmd = start + time + cmd + end
            os.system(os_cmd)

        return super().form_valid(form)


class ConfigMailingUpdateView(UpdateView):
    model = ConfigMailing
    fields = ('title', 'from_email', 'hour', 'minute', 'periodicity', 'mail_dump')
    template_name = 'sender/mailing_update.html'

    def form_valid(self, form):
        self.object = form.save()
        user = self.request.user
        path_project = '/'.join(os.path.abspath('manage.py').split('/')[3:-1])
        cmd = f'cd {path_project} && myvenv/bin/python3 manage.py send_by_cron -u {user.pk} -m {self.object.pk} >> log_cronjobs.txt'''
        os.system(f'''crontab -l | grep -v -F "{cmd}" | crontab -''')

        if self.object.periodicity == self.model.PERIOD_DAY:
            start = 'crontab -l | { cat; echo '
            time = f'''"{self.object.minute} {self.object.hour} * * * '''
            cmd = f'{cmd}"; '
            end = '} | crontab -'
            os_cmd = start + time + cmd + end
            os.system(os_cmd)

        super().form_valid(form)

        return self.get_success_url()

    def get_success_url(self):
        return HttpResponseRedirect(self.get_object().get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(proxy_mailing_detail.include_user_and_static_context(self.get_object(), self.request.user))

        return context


class ConfigMailingModeratingListView(ListView):
    model = ConfigMailing
    template_name = 'sender/mailing_list_moderating.html'
    ordering = '-create_at'

    def get(self, request, *args, **kwargs):
        user = self.request.user

        if not user.is_authenticated:
            redirect('sender:login')

        if not user.has_perm('sender.view_and_ban_any_mailing'):
            return redirect('sender:access_error')

        return super().get(request, *args, **kwargs)


    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_mailings'] = True
        context.update(include_static_context())

        return context

class ConfigMailingModeratingDetailView(DetailView):
    model = ConfigMailing
    template_name = 'sender/mailing_detail_moderating.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trials'] = TryMailing.objects.all().filter(mailing=self.get_object())
        context['letters'] = LetterMailing.objects.all().filter(mailing=self.get_object()).order_by('position')
        context['sent_letters_count'] = LetterMailing.objects.all().filter(mailing=self.get_object(), status=LetterMailing.STATUS_SENT).count()
        context.update(include_static_context())

        return context


class WeekdayUpdateConfigMailingDetailView(DetailView):
    model = ConfigMailing
    template_name = 'sender/mailing_update_weekday.html'
    form = UpdateWeekdayForm()

    def post(self, form, pk):
        mailing = ConfigMailing.objects.all().get(id=pk)

        weekdays = []
        weekdays_text = []
        for val in weekdays_cron_dict:
            try:
                form.POST[val]
            except Exception:
                continue
            else:
                weekdays.append(weekdays_cron_dict[val])
                weekdays_text.append(val)

        mailing.weekdays = ','.join(weekdays)
        mailing.weekdays_text = ', '.join(weekdays_text)
        mailing.save()

        user = self.request.user
        path_project = '/'.join(os.path.abspath('manage.py').split('/')[3:-1])
        cmd = f'cd {path_project} && myvenv/bin/python3 manage.py send_by_cron -u {user.pk} -m {mailing.pk} >> log_cronjobs.txt'''
        os.system(f'''crontab -l | grep -v -F "{cmd}" | crontab -''')
        start = 'crontab -l | { cat; echo '
        time = f'''"{mailing.minute} {mailing.hour} * * {mailing.weekdays} '''
        cmd = f'{cmd}"; '
        end = '} | crontab -'
        os_cmd = start + time + cmd + end
        os.system(os_cmd)

        return self.get_success_url()

    def get_success_url(self):
        return HttpResponseRedirect(self.get_object().get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context.update(proxy_mailing_detail.include_user_and_static_context(self.get_object(), self.request.user))

        return context


class MonthdateUpdateConfigMailingDetailView(DetailView):
    model = ConfigMailing
    template_name = 'sender/mailing_update_monthdate.html'
    form = UpdateMonthdateForm()

    def post(self, form, pk):
        mailing = ConfigMailing.objects.all().get(id=pk)

        monthdates = []
        for val in range(1, 32):
            try:
                form.POST[f'{val}']
            except Exception:
                continue
            else:
                monthdates.append(str(val))

        mailing.monthdates = ','.join(monthdates)
        mailing.monthdates_text = mailing.monthdates.replace(',', ', ')
        mailing.save()

        user = self.request.user
        path_project = '/'.join(os.path.abspath('manage.py').split('/')[3:-1])
        cmd = f'cd {path_project} && myvenv/bin/python3 manage.py send_by_cron -u {user.pk} -m {mailing.pk} >> log_cronjobs.txt'''
        os.system(f'''crontab -l | grep -v -F "{cmd}" | crontab -''')
        start = 'crontab -l | { cat; echo '
        time = f'''"{mailing.minute} {mailing.hour} {mailing.monthdates} * * '''
        cmd = f'{cmd}"; '
        end = '} | crontab -'
        os_cmd = start + time + cmd + end
        os.system(os_cmd)

        return self.get_success_url()

    def get_success_url(self):
        return HttpResponseRedirect(self.get_object().get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context.update(proxy_mailing_detail.include_user_and_static_context(self.get_object(), self.request.user))

        return context


class ConfigMailingDeleteView(DeleteView):
    model = ConfigMailing
    template_name = 'sender/forms/delete_mailing.html'
    success_url = reverse_lazy('sender:profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(proxy_mailing_detail.include_user_and_static_context(self.get_object(), self.request.user))

        return context

    def form_valid(self, form):
        user = self.request.user
        path_project = '/'.join(os.path.abspath('manage.py').split('/')[3:-1])
        cmd = f'cd {path_project} && myvenv/bin/python3 manage.py send_by_cron -u {user.pk} -m {self.object.pk} >> log_cronjobs.txt'''
        os.system(f'''crontab -l | grep -v -F "{cmd}" | crontab -''')

        return super().form_valid(form)


class RestartConfigMailingDetailView(DetailView):
    model = ConfigMailing
    template_name = 'sender/restart_mailing.html'

    def get(self, request, *args, **kwargs):
        obj = super().get_object()
        obj.status = ConfigMailing.STATUS_CREATED
        obj.save()
        context = super().get_context_data(object=obj)

        return super().render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(proxy_mailing_detail.include_user_and_static_context(self.get_object(), self.request.user))

        return context


class LetterMailingCreateView(DetailView):
    model = ConfigMailing
    form = LetterCreateForm()
    template_name = 'sender/forms/letter_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['mailing'] = self.object

        return context

    def post(self, form, pk):
        LetterMailing.objects.create(
            user=self.request.user,
            mailing=self.get_object(),
            title=form.POST['title'],
            content=form.POST['content'],
            position=form.POST['position']
        )
        return HttpResponseRedirect(self.get_object().get_absolute_url())


class LetterMailingUpdateView(UpdateView):
    model = LetterMailing
    form_class = LetterUpdateForm
    template_name = 'sender/forms/letter_form.html'
    pk_url_kwarg = 'letter_pk'

    def get_success_url(self):
        return reverse_lazy('sender:mailing_detail', kwargs={'pk': self.get_object().mailing.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailing'] = ConfigMailing.objects.all().get(id=self.get_object().mailing.pk)
        context['letter_exist'] = True

        return context


class LetterMailingDeleteView(DeleteView):
    model = LetterMailing
    template_name = 'sender/forms/delete_letter.html'
    pk_url_kwarg = 'letter_pk'

    def get_success_url(self):
        return reverse_lazy('sender:mailing_detail', kwargs={'pk': self.get_object().mailing.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailing'] = ConfigMailing.objects.all().get(id=self.get_object().mailing.pk)

        return context


class TryMailingListView(ListView):
    model = TryMailing
    template_name = 'sender/try_list.html'
    success_url = reverse_lazy('sender:trials')

    def get_queryset(self):
        user = self.request.user

        if user.has_perm('sender.view_and_ban_any_mailing'):
            return super().get_queryset().order_by('-date_time_try')

        return super().get_queryset().filter(user=self.request.user).order_by('-date_time_try')


class ContactsFormView(FormView):
    template_name = 'sender/contacts.html'
    form_class = FeedbackForm
    success_url = reverse_lazy('catalog:after_feedback')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contacts'] = Contacts.objects.all().get(id=1)

        return context

    def form_valid(self, form):
        recipients = [x.email for x in User.objects.all().filter(groups__name='Менеджеры')]
        custom_send_mail.feedback(form.data['name'], form.data['email'], form.data['message'], recipients)

        return super().form_valid(form)


class InvalidVerifyTemplateView(TemplateView):
    template_name = 'sender/service/invalid_verify.html'

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            return redirect('sender:profile')

        return self.render_to_response(context)


class UserListModeratingListView(ListView):
    model = User
    template_name = 'sender/user_list_moderating.html'
    ordering = '-register_at'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(include_static_context())

        return context


class UserCommentModeratingUpdateView(DetailView):
    model = User
    template_name = 'sender/forms/user_comment_form.html'
    form = UserCommentForm()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form

        return context

    def post(self, form, pk):
        obj = User.objects.all().get(id=pk)
        obj.comment = form.POST['comment']
        obj.save()

        return redirect('sender:moderating_users')


class MailingBannedUpdateView(UpdateView):
    model = ConfigMailing
    form_class = ConfigMailingBannedForm
    template_name = 'sender/change_ban_status_mailing.html'

    def get(self, request, *args, **kwargs):
        user = self.request.user

        if not user.is_authenticated:
            return redirect('sender:login')

        if not user.has_perm('sender.view_and_ban_any_mailing'):
            return redirect('sender:access_error')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(include_static_context())

        return context

    def form_valid(self, form):
        obj = super().get_object()

        if form.data['banned'] == ConfigMailing.BANNED_FALSE and obj.banned == ConfigMailing.BANNED_FALSE:
            form.add_error('banned', f'Выберите значение ЗАБЛОКИРОВАТЬ')

            return super().render_to_response(self.get_context_data(form=form))

        if form.data['banned'] == ConfigMailing.BANNED_TRUE and obj.banned == ConfigMailing.BANNED_TRUE:
            form.add_error('banned', f'Выберите значение РАЗБЛОКИРОВАТЬ')

            return super().render_to_response(self.get_context_data(form=form))

        if form.data['banned'] == ConfigMailing.BANNED_FALSE:
            obj = form.save()
            reason_ban = form.data['reason_ban']

            try:
                send_mail(
                    subject='''Ваша рассылка на сайте VDchimp разблокирована''',
                    message=f'''Рассылка: '{obj.title}' разблокирована. \n{reason_ban}. \nЕсли у Вас есть вопросы, Вы можете написать модератору на почту {self.request.user.email}''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[obj.user.email, ]
                )

            except SMTPException as e:
                os.system(f'echo {timezone.now()}, {e} >> send_reason_ban_mailing_errors.txt')

                return redirect('sender:send_ban_status_error')

            else:
                return redirect('sender:moderating_mailings')

        if form.data['banned'] == ConfigMailing.BANNED_TRUE:
            obj = form.save()
            reason_ban = form.data['reason_ban']

            try:
                send_mail(
                    subject='''Ваша рассылка на сайте VDchimp заблокирована''',
                    message=f'''Рассылка: '{obj.title}' заблокирована. \nПричины бана: {reason_ban}. \nЕсли у Вас есть вопросы, Вы можете написать модератору на почту {self.request.user.email}''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[obj.user.email, ]
                )

            except SMTPException as e:
                os.system(f'echo {timezone.now()}, {e} >> send_reason_ban_mailing_errors.txt')

                return redirect('sender:send_ban_status_error')

            else:
                return redirect('sender:moderating_mailings')


class UserBannedUpdateView(UpdateView):
    model = User
    form_class = UserBannedForm
    template_name = 'sender/change_ban_status_user.html'
    success_url = reverse_lazy('sender:moderating_users')

    def get(self, request, *args, **kwargs):
        user = self.request.user

        if not user.is_authenticated:
            return redirect('sender:login')

        if not user.has_perm('sender.view_and_ban_any_user'):
            return redirect('sender:access_error')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(include_static_context())

        return context

    def form_valid(self, form):
        obj = super().get_object()


        if form.data['banned'] == User.BANNED_FALSE and obj.banned == User.BANNED_FALSE:
            form.add_error('banned', f'Выберите значение ЗАБЛОКИРОВАТЬ')

            return super().render_to_response(self.get_context_data(form=form))

        if form.data['banned'] == User.BANNED_TRUE and obj.banned == User.BANNED_TRUE:
            form.add_error('banned', f'Выберите значение РАЗБЛОКИРОВАТЬ')

            return super().render_to_response(self.get_context_data(form=form))

        if form.data['banned'] == User.BANNED_FALSE:
            obj = form.save()
            reason_ban = form.data['reason_ban']

            try:
                send_mail(
                    subject='''Вы разблокированы на сайте VDchimp''',
                    message=f'''\n{reason_ban}. \nЕсли у Вас есть вопросы, Вы можете написать модератору на почту {self.request.user.email}''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[obj.email,]
                )

            except SMTPException as e:
                os.system(f'echo {timezone.now()}, {e} >> send_reason_ban_user_errors.txt')

                return redirect('sender:send_ban_status_error')

            else:
                return HttpResponseRedirect(self.get_success_url())

        if form.data['banned'] == User.BANNED_TRUE:
            obj = form.save()
            reason_ban = form.data['reason_ban']

            try:
                send_mail(
                    subject='''Вы заблокированы на сайте VDchimp''',
                    message=f'''\nПричины бана: {reason_ban}. \nЕсли у Вас есть вопросы, Вы можете написать модератору на почту {self.request.user.email}''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[obj.email, ]
                )

            except SMTPException as e:
                os.system(f'echo {timezone.now()}, {e} >> send_reason_ban_user_errors.txt')

                return redirect('sender:send_ban_status_error')

            else:
                return HttpResponseRedirect(self.get_success_url())


class PostListContentManagementListView(ListView):
    model = Post
    template_name = 'sender/post_list_content_management.html'
    paginate_by = 12
    ordering = ['-create_at']


class PostListView(ListView):
    model = Post
    template_name = 'sender/post_list.html'
    paginate_by = 12
    ordering = ['-create_at']
    paginate_orphans = 3

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count_posts'] = self.get_queryset().count()

        return context

    def get_queryset(self):
        return super().get_queryset().filter(status=Post.STATUS_ACTIVE).order_by('-create_at', '-id')


class PostDetailView(DetailView):
    model = Post
    template_name = 'sender/post_detail.html'

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)

        obj = self.get_object()
        context = super().get_context_data(object=obj)
        obj.count_views += 1
        obj.save()

        return super().render_to_response(context)


class PostCreateView(CreateView):
    model = Post
    template_name = 'sender/forms/post_form.html'

    def get(self, request, *args, **kwargs):
        user = self.request.user

        if not user.is_authenticated:
            return redirect('sender:login')

        if not user.has_perm('sender.content_management'):
            return redirect('sender:access_error')

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        self.object.slug = translit.do(self.object.title)
        self.object.change_at = timezone.now()
        self.object.save()

        return super().form_valid(form)


class PostUpdateView(UpdateView):
    model = Post
    template_name = 'sender/forms/post_form.html'

    def get(self, request, *args, **kwargs):
        user = self.request.user

        if not user.is_authenticated:
            return redirect('sender:login')

        if not user.has_perm('sender.content_management'):
            return redirect('sender:access_error')

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        self.object.slug = translit.do(self.object.title)
        self.object.change_at = timezone.now()
        self.object.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('sender:content_management_posts')


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'sender/forms/delete_post.html'
    success_url = reverse_lazy('users:user_posts')

    def get(self, request, *args, **kwargs):
        user = self.request.user

        if not user.is_authenticated:
            return redirect('sender:login')

        if not user.has_perm('sender.content_management'):
            return redirect('sender:access_error')

        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('sender:content_management_posts')


class BlogUpdateView(UpdateView):
    model = Blog
    template_name = 'sender/blog_form.html'
    form_class = UpdateBlogForm

    def get(self, request, *args, **kwargs):
        user = self.request.user

        if not user.is_authenticated:
            return redirect('sender:login')

        if not user.has_perm('sender.content_management'):
            return redirect('sender:access_error')

        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return Blog.objects.first()

    def get_success_url(self):
        return reverse_lazy('sender:content_management_posts')


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'sender/forms/change_password.html'
    model = User
    success_url = reverse_lazy('sender:profile')


class CustomPasswordResetFormView(FormView):
    template_name = 'sender/forms/reset_password_form.html'
    form_class = CustomPasswordResetForm

    def get(self, request, *args, **kwargs):

        if self.request.user.is_authenticated:
            return redirect('sender:profile')

        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('sender:confirm_reset')

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.all().get(email=email)
            new_password = User.objects.make_random_password(length=20)
            user.set_password(new_password)
            user.save()
            try:
                custom_send_mail.reset_password(request, email, new_password)

            except SMTPException as e:
                os.system(f'echo {timezone.now()}, {e} >> password_reset_errors.txt')

                return redirect('sender:some_error')

            else:
                return redirect('sender:confirm_reset')

        context = {'form': form}

        return render(request, self.template_name, context)


class ConfirmResetPasswordTemplateView(TemplateView):
    template_name = 'sender/service/after_reset_password.html'

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            return redirect('sender:profile')

        return self.render_to_response(context)






