from django.urls import path
from sender.views import*
from sender.apps import SenderConfig

app_name = SenderConfig.name

urlpatterns = [
    path('', LoginUser.as_view(), name='login'),
    path('register/', RegisterUser.as_view(), name='registration'),
    path('logout/', logout_user, name='logout'),
    path('profile/', ListAndCreateConfigMailing.as_view(), name='profile'),
    path('profile/mailing-<int:pk>', ConfigMailingDetailView.as_view(), name='mailing_detail'),
    path('profile/update-mailing-<int:pk>', ConfigMailingUpdateView.as_view(), name='update_mailing'),
    path('profile/delete-mailing-<int:pk>', ConfigMailingDeleteView.as_view(), name='delete_mailing'),
    path('profile/mailing-<int:pk>/create-letter', LetterMailingCreateView.as_view(), name='create_letter'),
    path('profile/mailing-<int:mailing_pk>/update-letter-<int:letter_pk>', LetterMailingUpdateView.as_view(), name='update_letter'),
    path('profile/mailing-<int:mailing_pk>/delete-letter-<int:letter_pk>', LetterMailingDeleteView.as_view(), name='delete_letter'),
    path('profile/update-mailing-<int:pk>/point-weekdays', WeekdayUpdateConfigMailingDetailView.as_view(), name='update_weekday'),
    path('profile/update-mailing-<int:pk>/point-monthdates', MonthdateUpdateConfigMailingDetailView.as_view(), name='update_monthdate'),
    path('profile/mailing-<int:pk>/success-restart', RestartConfigMailingDetailView.as_view(), name='restart_mailing'),
    path('trials/', TryMailingListView.as_view(), name='trials')
]