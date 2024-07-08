from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def user_is_medical_staff(function):
    def wrap(request, *args, **kwargs):
        if request.user.user_type in ['doctor', 'nurse', 'admin']:
            return function(request, *args, **kwargs)
        else:
            return redirect('unauthorized_access')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap