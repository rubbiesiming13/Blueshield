from functools import wraps

from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect


def role_required(*allowed_roles):
    """
    Allow access only to users with one of the specified roles.
    """

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                return redirect("accounts:login")

            # Account must be active
            if not request.user.is_active:
                messages.error(
                    request,
                    "Your account is inactive."
                )

                logout(request)

                return redirect("accounts:login")

            # SevisPass must be verified
            if not request.user.sevispass_verified:
                messages.error(
                    request,
                    "Verified SevisPass access is required."
                )

                logout(request)

                return redirect("accounts:login")

            # Check role
            if request.user.role not in allowed_roles:

                messages.error(
                    request,
                    "You do not have permission to access this page."
                )

                return redirect("accounts:dashboard")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator