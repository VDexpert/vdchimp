import os
from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from sender.forms import *
from django.http import HttpResponseRedirect
from sender.models import*


weekdays_cron_dict = {
    'понедельник': '1', 'вторник': '2', 'среда': '3', 'четверг': '4',
    'пятница': '5', 'суббота': '6', 'воскресенье': '0'
}
monthdate_input_list = [str(x) for x in range(1, 32)]
hours_list = [x for x in range(0, 24)]
minutes_list = [x for x in range(0, 60)]


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'sender/registration.html'
    success_url = reverse_lazy('sender:login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('sender:profile')


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'sender/login.html'
    success_url = reverse_lazy('sender:profile')

def logout_user(request):
    logout(request)
    return redirect('sender:login')


class ConfigMailingListView(ListView):
    model = ConfigMailing
    fields = '__all__'
    template_name = 'sender/profile.html'
    success_url = reverse_lazy('sender:profile')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(username=self.request.user)


class ListAndCreateConfigMailing(CreateView):
    model = ConfigMailing
    fields = ('title', 'hour', 'minute', 'periodicity', 'mail_dump')
    template_name = 'sender/profile.html'
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
        context["object_list"] = self.model.objects.all().filter(user=self.request.user.pk)
        context['user'] = self.request.user
        context['periods'] = ConfigMailing.PERIODS_TUPLE

        return context


class ConfigMailingUpdateView(UpdateView):
    model = ConfigMailing
    fields = ('title', 'from_email', 'hour', 'minute', 'periodicity', 'mail_dump')
    template_name = 'sender/mailing_form.html'

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

        return self.get_success_url()

    def get_success_url(self):
        return HttpResponseRedirect(self.get_object().get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['letters'] = LetterMailing.objects.all().filter(user=self.request.user.pk, mailing=self.get_object().pk)
        context['sent_letters_count'] = LetterMailing.objects.all().filter(user=self.request.user.pk, mailing=self.get_object().pk, status=LetterMailing.SENT).count()
        context['periods'] = ConfigMailing.PERIODS_TUPLE

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
        context['letters'] = LetterMailing.objects.all().filter(user=self.request.user.pk, mailing=self.get_object().pk)
        context['sent_letters_count'] = LetterMailing.objects.all().filter(user=self.request.user.pk, mailing=self.get_object().pk, status=LetterMailing.SENT).count()

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

        return context


class ConfigMailingDeleteView(DeleteView):
    model = ConfigMailing
    template_name = 'sender/delete_mailing.html'
    success_url = reverse_lazy('sender:profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def form_valid(self, form):
        user = self.request.user
        path_project = '/'.join(os.path.abspath('manage.py').split('/')[3:-1])
        cmd = f'cd {path_project} && myvenv/bin/python3 manage.py send_by_cron -u {user.pk} -m {self.object.pk} >> log_cronjobs.txt'''
        os.system(f'''crontab -l | grep -v -F "{cmd}" | crontab -''')

        return super().form_valid(form)


class ConfigMailingDetailView(DetailView):
    model = ConfigMailing
    template_name = 'sender/mailing_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trials'] = TryMailing.objects.all().filter(user=self.request.user.pk)
        context['letters'] = LetterMailing.objects.all().filter(user=self.request.user.pk, mailing=self.get_object().pk).order_by('position')
        context['sent_letters_count'] = LetterMailing.objects.all().filter(user=self.request.user.pk, mailing=self.get_object().pk, status=LetterMailing.SENT).count()
        context['status_mailing_done'] = ConfigMailing.DONE
        context['status_mailing_moderating'] = ConfigMailing.MODERATING
        context['period_mailing_month'] = ConfigMailing.PERIOD_MONTH
        context['period_mailing_week'] = ConfigMailing.PERIOD_WEEK
        context['status_letter_sent'] = LetterMailing.SENT
        context['status_letter_wait'] = LetterMailing.WAIT
        context['periods'] = ConfigMailing.PERIODS_TUPLE
        context['hours'] = hours_list
        context['minutes'] = minutes_list

        return context


class RestartConfigMailingDetailView(DetailView):
    model = ConfigMailing
    template_name = 'sender/restart_mailing.html'

    def get(self, request, *args, **kwargs):
        obj = super().get_object()
        obj.status = 'Создана'
        obj.save()
        context = super().get_context_data(object=obj)

        return super().render_to_response(context)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['trials'] = TryMailing.objects.all().filter(user=self.request.user.pk)
    #     context['letters'] = LetterMailing.objects.all().filter(user=self.request.user.pk, mailing=self.get_object().pk).order_by('position')
    #     context['sent_letters_count'] = LetterMailing.objects.all().filter(user=self.request.user.pk, mailing=self.get_object().pk, status=LetterMailing.SENT).count()
    #     context.update(get_static_context())
    #
    #     return context


class LetterMailingCreateView(CreateView):
    model = ConfigMailing
    form = LetterCreateForm()
    template_name = 'sender/letter_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['mailing'] = self.object
        # context['sent_letters_count'] = LetterMailing.objects.all().filter(user=self.request.user.pk, mailing=self.get_object().pk, status=LetterMailing.SENT).count()
        # context['letters'] = LetterMailing.objects.all().filter(user=self.request.user, mailing=self.get_object()).order_by('position')
        # context.update(get_static_context())

        return context

    # def post(self, form, pk):
    #     LetterMailing.objects.create(
    #         user=self.request.user,
    #         mailing=self.get_object(),
    #         title=form.POST['title'],
    #         content=form.POST['content'],
    #         position=form.POST['position']
    #     )
    #     return HttpResponseRedirect(self.get_object().get_absolute_url())


class LetterMailingUpdateView(UpdateView):
    model = LetterMailing
    form_class = LetterUpdateForm
    template_name = 'sender/letter_form.html'
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
    template_name = 'sender/delete_letter.html'
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
       return super().get_queryset().filter(user=self.request.user)



