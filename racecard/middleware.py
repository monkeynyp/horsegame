from django.utils.translation import activate

class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user has explicitly selected a language
        if 'lang_code' in request.GET:
            lang_code = request.GET['lang_code']
            if lang_code in ['en', 'tw']:
                request.session['django_language'] = lang_code
                activate(lang_code)
        else:
            # If no language is selected, set default to Traditional Chinese ('tw')
            if 'django_language' not in request.session:
                request.session['django_language'] = 'tw'
                activate('tw')
        
        response = self.get_response(request)

        return response