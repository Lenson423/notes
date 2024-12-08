from django.contrib import admin
from .models import Note

from django.utils.translation import gettext_lazy as _


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('note_title', 'created_at', 'updated_at', 'user')