# users/admin.py
#
# This file configures how our models appear in the Django Admin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

# Define an inline admin descriptor for UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    
    # We add 'is_verified' to the list display
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_is_verified')

    def get_is_verified(self, instance):
        return instance.profile.is_verified
    get_is_verified.short_description = 'Verified'
    get_is_verified.boolean = True
    
    # This is where you would set up the admin verification action
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Note: After you create your Departments (Groups) in the admin,
# you can come here to verify users and assign them.