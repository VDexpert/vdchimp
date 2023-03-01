from django.contrib import admin
from sender.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'phone', 'country', 'first_name', 'last_name')
    search_fields = ('id', 'email')
    ordering = ('email',)

    def get_form(self, request, obj=None, **kwargs):

        form = super().get_form(request, obj, **kwargs)
        disabled_fields = set()
        disabled_fields |= {
            'user_permissions',
        }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True
        return form
