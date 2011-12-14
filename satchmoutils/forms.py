import logging, re, types
from django import forms
from django.utils.encoding import smart_unicode
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.forms.fields import CharField, BooleanField

from satchmo_store.contact.models import Contact
from captcha.fields import CaptchaField


class ContactForm(forms.Form):
    sender_fullname = forms.CharField(required=True, max_length=100)
    company = forms.CharField(required=False, max_length=100)
    city = forms.CharField(required=False, max_length=100)
    telephone = forms.CharField(required=False, max_length=100)
    sender_from_address = forms.EmailField(required=True, max_length=100)
    message = forms.CharField(required=True, widget=forms.widgets.Textarea(), max_length=1000)
    captcha = CaptchaField(required=True)