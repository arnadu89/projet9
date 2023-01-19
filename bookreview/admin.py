from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Review, Ticket, User, UserFollows


admin.site.register(User, UserAdmin)
admin.site.register(UserFollows)
admin.site.register(Review)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "time_created")