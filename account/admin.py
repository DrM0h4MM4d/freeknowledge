from django.contrib import admin
from .models import (
    ChallengeEvent,
    ContactsUser,
    Message,
    NotificationAdminCenter,
    UserProfile,
)
from django.contrib.auth.admin import UserAdmin


# Register your models here.
UserAdmin.fieldsets[2][1]['fields'] += (
    'profile_pic',
    'phone',
    'about',
    'short_about',
    'is_author',
    'can_send_message',
)
UserAdmin.list_display += (
                'phone',
                'about',
                'short_about',
                'is_author',
                'can_send_message',
                'get_user_contacts',
                'image_tag',
)


@admin.register(ContactsUser)
class ContactUserAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'title',
        'url',
        'date_cr',
        'date_up',
    ]


@admin.register(NotificationAdminCenter)
class NotificationAdminCenterAdmin(admin.ModelAdmin):
    list_display = [
            'title',
            'text',
            'date',        
    ]


@admin.register(ChallengeEvent)
class AdminChallengeEvent(admin.ModelAdmin):
    list_display = [
            'title',
            'slug',
            'info',
            'date_c',
            'date_u',
            'image_tag',
            'get_category',
            'get_author',
    ]


admin.site.register(Message)
admin.site.register(UserProfile, UserAdmin)
