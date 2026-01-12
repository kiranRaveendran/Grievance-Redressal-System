from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def officer_required(view_func):
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.groups.filter(name="Officer").exists():
            raise PermissionDenied("Officer access only")
        return view_func(request, *args, **kwargs)
    return _wrapped
