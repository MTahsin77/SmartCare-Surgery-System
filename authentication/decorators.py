from django.shortcuts import redirect
from functools import wraps
from django.contrib.auth.decorators import login_required

def user_is_patient(function):
    @wraps(function)
    @login_required
    def wrap(request, *args, **kwargs):
        if request.user.user_type == 'patient':
            return function(request, *args, **kwargs)
        else:
            return redirect('unauthorized_access')
    return wrap

def user_is_doctor(function):
    @wraps(function)
    @login_required
    def wrap(request, *args, **kwargs):
        if request.user.user_type == 'doctor':
            return function(request, *args, **kwargs)
        else:
            return redirect('unauthorized_access')
    return wrap

def user_is_nurse(function):
    @wraps(function)
    @login_required
    def wrap(request, *args, **kwargs):
        if request.user.user_type == 'nurse':
            return function(request, *args, **kwargs)
        else:
            return redirect('unauthorized_access')
    return wrap

def user_is_admin(function):
    @wraps(function)
    @login_required
    def wrap(request, *args, **kwargs):
        if request.user.user_type == 'admin':
            return function(request, *args, **kwargs)
        else:
            return redirect('unauthorized_access')
    return wrap