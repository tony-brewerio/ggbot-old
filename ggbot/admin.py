from __future__ import absolute_import, division, print_function, unicode_literals

from django import forms
from django.contrib import admin

from ggbot.models import Room, Account


class RoomAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'ip',
    search_fields = 'name',


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = '__all__'

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'vTextField'})
    )

    def save(self, commit=True):
        if self.cleaned_data['password']:
            self.instance.set_password(self.cleaned_data['password'])
        return super(AccountForm, self).save(commit=commit)


class AccountAdmin(admin.ModelAdmin):
    form = AccountForm
    list_display = 'login',
    search_fields = 'login',
    readonly_fields = 'password_encrypted',


admin.site.register(Room, RoomAdmin)
admin.site.register(Account, AccountAdmin)
