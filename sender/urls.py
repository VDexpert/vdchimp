from django.urls import path
from sender.views import*
from sender.apps import SenderConfig

app_name = SenderConfig.name

urlpatterns = [
    path('blog', PostListView.as_view(), name='post_list'),
    path('blog/<str:slug>', PostDetailView.as_view(), name='post_detail'),
    path('update-blog', BlogUpdateView.as_view(), name='update_blog'),
    path('content-management-posts', PostListContentManagementListView.as_view(), name='content_management_posts'),
    path('create-post', PostCreateView.as_view(), name='create_post'),
    path('update-post', PostUpdateView.as_view(), name='update_post'),
    path('contacts', ContactsFormView.as_view(), name='contacts'),
    path('login', LoginUser.as_view(), name='login'),
    path('logout', logout_user, name='logout'),
    path('register', RegisterUser.as_view(), name='registration'),
    path('my-mailings', ListAndCreateConfigMailing.as_view(), name='profile'),
    path('verify-email/<uidb64>/<token>/', EmailVerifyView.as_view(), name='verify_email'),
    path('invalid-verify', InvalidVerifyTemplateView.as_view(), name='invalid_verify'),
    path('confirm-email', ConfirmEmailTemplateView.as_view(), name='confirm_email'),
    path('change-password/', CustomPasswordChangeView.as_view(), name='change_password'),
    path('reset-password/', CustomPasswordResetFormView.as_view(), name='reset_password'),
    path('success-reset-password/', ConfirmResetPasswordTemplateView.as_view(), name='confirm_reset'),
    path('my-mailings/mailing-<int:pk>', ConfigMailingDetailView.as_view(), name='mailing_detail'),
    path('my-mailings/update-mailing-<int:pk>', ConfigMailingUpdateView.as_view(), name='update_mailing'),
    path('my-mailings/delete-mailing-<int:pk>', ConfigMailingDeleteView.as_view(), name='delete_mailing'),
    path('my-mailings/mailing-<int:pk>/create-letter', LetterMailingCreateView.as_view(), name='create_letter'),
    path('my-mailings/mailing-<int:mailing_pk>/update-letter-<int:letter_pk>', LetterMailingUpdateView.as_view(), name='update_letter'),
    path('my-mailings/mailing-<int:mailing_pk>/delete-letter-<int:letter_pk>', LetterMailingDeleteView.as_view(), name='delete_letter'),
    path('my-mailings/update-mailing-<int:pk>/point-weekdays', WeekdayUpdateConfigMailingDetailView.as_view(), name='update_weekday'),
    path('my-mailings/update-mailing-<int:pk>/point-monthdates', MonthdateUpdateConfigMailingDetailView.as_view(), name='update_monthdate'),
    path('my-mailings/mailing-<int:pk>/success-restart', RestartConfigMailingDetailView.as_view(), name='restart_mailing'),
    path('my-mailings/create-mailing', ConfigMailingCreateViewMobile.as_view(), name='create_mailing_mobile'),
    path('all-mailings', ConfigMailingModeratingListView.as_view(), name='moderating_mailings'),
    path('all-mailings/mailing-<int:pk>', ConfigMailingModeratingDetailView.as_view(), name='mailing_detail_moderating'),
    path('all-mailings/mailing-<int:pk>/change-ban-status', MailingBannedUpdateView.as_view(), name='mailing_ban'),
    path('user-list', UserListModeratingListView.as_view(), name='moderating_users'),
    path('user-list/user-<int:pk>/change-ban-status', UserBannedUpdateView.as_view(), name='user_ban'),
    path('user-list/user-<int:pk>/change-comment', UserCommentModeratingUpdateView.as_view(), name='moderating_user_comment'),
    path('mail-server-responds', TryMailingListView.as_view(), name='trials'),
    path('thank-for-feedback', TemplateView.as_view(template_name='sender/service/after_feedback_page.html'), name='after_feedback'),
    path('access-error', TemplateView.as_view(template_name='sender/service/permission_error.html'), name='access_error'),
    path('some-error', TemplateView.as_view(template_name='sender/service/some_error.html'), name='some_error'),
    path('send-ban-status-error', TemplateView.as_view(template_name='sender/service/send_ban_status_error.html'), name='send_ban_status_errorr'),
    path('success-reset-password', TemplateView.as_view(template_name='sender/service/after_reset_password.html'), name='after_reset_password'),
]