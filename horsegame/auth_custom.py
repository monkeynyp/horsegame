from django.contrib.auth.password_validation import BasePasswordValidator
from django.utils.translation import gettext as _

class CustomPasswordValidator(BasePasswordValidator):
    def validate(self, password, user=None):
        if len(password) < 6:
            raise ValidationError(
                _("The password must be at least 6 characters long."),
                code='password_too_short',
            )