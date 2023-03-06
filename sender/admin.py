from django.contrib import admin
from sender.models import User, Contacts, Blog, Home


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



@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    list_display = ('home_h1', 'home_annotation', 'title')

    def has_add_permission(self, request):
        if Home.objects.all().filter(id=1).exists():
            return False

        return True

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Blog)
class ContactsAdmin(admin.ModelAdmin):
    list_display = ('blog_h1', 'blog_annotation', 'title')

    def has_add_permission(self, request):
        if Blog.objects.all().filter(id=1).exists():
            return False

        return True

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Contacts)
class ContactsAdmin(admin.ModelAdmin):
    list_display = ('official_company_name', 'itin', 'phone', 'email', 'address')

    def has_add_permission(self, request):
        if Contacts.objects.all().filter(id=1).exists():
            return False

        return True

    def has_delete_permission(self, request, obj=None):
        return False
