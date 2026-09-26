# apps/accounts/permissions.py
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def commander_required(view_func):
  def _wrapped_view(request, *args, **kwargs):
    if (
        request.user.is_authenticated
        and request.user.role in ["COMMANDER", "ADMIN"]
    ) or request.user.is_superuser:
      return view_func(request, *args, **kwargs)
    raise PermissionDenied("Access restricted to Station Commanders (OIC).")

  return _wrapped_view


def cid_or_commander_required(view_func):
  def _wrapped_view(request, *args, **kwargs):
    if request.user.is_authenticated and request.user.role in [
        "CID",
        "COMMANDER",
        "ADMIN",
    ]:
      return view_func(request, *args, **kwargs)
    raise PermissionDenied("Access restricted to CID Officers and Commanders.")

  return _wrapped_view
