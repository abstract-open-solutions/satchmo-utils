from django.conf import settings
from django.utils.translation import check_for_language

import logging

logger = logging.getLogger("MIDDLEWARE LOG")


class ContentLengthWriter(object):
    """A simple middleware that writes content-length
    """

    def process_response(self, request, response):
        if not response.has_header('Content-Length'):
            response['Content-Length'] = str(len(response.content))
        return response

class LanguageManager(object):
    """A simple middleware that handle language cookies for both Plone and Satchmo
    """
    
    def process_request(self, request):
        """
            il middleware:
            leva  le " al cookie
            mette il contenuto del cookie in request.session['django_language']
            stop
        """
        old_cookie = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME, None)
        
        if not old_cookie:
            return None
        new_cookie = old_cookie.replace('"','')
        
        if request.method == 'POST':
            lang_code = request.POST.get('language', None)
            if lang_code and check_for_language(lang_code):
                request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = new_cookie
        return None
