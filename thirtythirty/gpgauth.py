
from django.contrib.auth.models import User
from django.contrib.auth.views import redirect_to_login

# http://stackoverflow.com/questions/8869816/django-test-returning-wrapped-view-as-view-name-instead-of-proper-view-name
from functools import wraps
from django.utils.decorators import available_attrs

import addressbook.gpg
import thirtythirty.models
from settings import USERNAME

def set_up_single_user():
    """
    FIXME: when we go multiuser, this will need rethinking
    """
    try:
        single_user = User.objects.get(username=USERNAME)
    except User.DoesNotExist:
        single_user = User(username=USERNAME)
        single_user.save()
        prefs = thirtythirty.models.preferences(ooser=single_user)
        prefs.save()
    Preferences, create = thirtythirty.models.preferences.objects.get_or_create(ooser=single_user)
    return Preferences


class gpgAuth(object):
    def authenticate(self, username=USERNAME, password=None):
        if addressbook.gpg.verify_symmetric(password):
            Prefs = set_up_single_user()
            return User.objects.get(username=USERNAME)
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None



def session_pwd_wrapper(view_func=None):
    """
    decorator to take the place of @login_required
    (django.contrib.auth.decorators)

    @wraps makes sure error msgs are penetrable
    """
    @wraps(view_func, assigned=available_attrs(view_func))
    def inner(request, *args, **kwargs):
        prefs = thirtythirty.models.preferences.objects.first()            # FIXME: single user mode
        if not prefs:
            return view_func(request, *args, **kwargs)
        if not request.user.is_authenticated():
            return redirect_to_login(request.get_full_path(),
                                     login_url='/accounts/login')
        else:
            return view_func(request, *args, **kwargs)
    return inner
