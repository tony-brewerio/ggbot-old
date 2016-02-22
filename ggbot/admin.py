from __future__ import absolute_import, division, print_function, unicode_literals

from django import forms
from django.contrib import admin

from ggbot.models import Room, Account, League


class LeagueForm(forms.ModelForm):
    room = forms.ModelChoiceField(queryset=Room.objects.order_by('name'))


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        exclude = 'password_encrypted_iv',

    password = forms.CharField(
        label='Password',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'vTextField'})
    )

    def save(self, commit=True):
        if self.cleaned_data['password']:
            self.instance.set_password(self.cleaned_data['password'])
        return super(AccountForm, self).save(commit=commit)


class LeagueAccountInline(admin.TabularInline):
    model = Account
    form = AccountForm
    readonly_fields = 'password_encrypted',


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'ip',
    search_fields = 'name',


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    form = LeagueForm
    inlines = LeagueAccountInline,
    list_display = 'name', 'room', 'active', 'room_password',


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    form = AccountForm
    list_display = 'login', 'league', 'active',
    readonly_fields = 'password_encrypted',
