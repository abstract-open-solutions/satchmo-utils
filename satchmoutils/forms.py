from django import forms
from captcha.fields import CaptchaField


class ContactForm(forms.Form):
    """The *contact us* form.

    If a user wants to send an inquiry to the site owner, this form allows him
    to do so without making the reserved email address public, which should
    result in less spam.
    """

    sender_fullname = forms.CharField(max_length=100,
                                      required=True)
    company = forms.CharField(max_length=100,
                              required=True)
    city = forms.CharField(max_length=100,
                           required=False)
    telephone = forms.CharField(max_length=100,
                                required=False)
    sender_from_address = forms.EmailField(max_length=100,
                                           required=False)
    message = forms.CharField(widget=forms.widgets.Textarea(),
                              max_length=1000,
                              required=True)
    captcha = CaptchaField(required=True)
