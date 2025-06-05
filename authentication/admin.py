from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('email',)
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_active')}),
    )
    search_fields = ('email',)
    ordering = ('email',)

    filter_horizontal = ()
    add_list_display = ('email', 'first_name', 'last_name', 'phone_number', 'is_staff', 'is_active')
    add_search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    add_ordering = ('email',)
    add_filter_horizontal = ()
    add_list_filter = ('is_staff', 'is_active')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SentEmail)
admin.site.register(ReportedEmail)
admin.site.register(LessonProgress)
admin.site.register(SentSMS)
admin.site.register(ReportedSMS)
from .models import LegitimateEmail

@admin.register(LegitimateEmail)
class LegitimateEmailAdmin(admin.ModelAdmin):
    list_display = ("subject", "sender_email", "receiver_email", "sent_at", "marked_by", "is_real")
    search_fields = ("subject", "sender_email", "receiver_email")
    list_filter = ("sent_at", "is_real")

from .models import AdminLesson
admin.site.register(AdminLesson)


