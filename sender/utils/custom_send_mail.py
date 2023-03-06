from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator as token_gen
from django.conf import settings


def verify(request, user):
    current_site = request.get_host()
    context = {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token_gen.make_token(user),
    }
    message = render_to_string('sender/mails/verify_registration.html', context=context,)
    email = EmailMessage('Завершение регистрации на сайте VDchimp', message, to=[user.email],)

    email.send()


def reset_password(request, email, new_password):
    current_site = request.get_host()

    context = {
        'domain': current_site,
        'new_password': new_password
    }

    message = render_to_string('sender/mails/reset_password.html', context=context,)
    email = EmailMessage('Восстановление пароля на сайте VDchimp', message, to=[email])

    email.send()


def feedback(user_name, user_email, user_message, recipients):
    send_mail(
        subject='''Обратная связь от посетителя VDsolutions в форме Контакты''',
        message=f'''Имя посетителя: {user_name}
                \nEmail посетителя: {user_email}
                \nСообщение посетителя: {user_message}''',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=recipients
    )