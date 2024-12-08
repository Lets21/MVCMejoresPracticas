from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from .models import TipoUsuario

def tipo_usuario_requerido(tipos):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('signin')
            try:
                tipo_usuario = request.user.tipousuario.tipo
                if tipo_usuario in tipos:
                    return view_func(request, *args, **kwargs)
                else:
                    raise PermissionDenied
            except TipoUsuario.DoesNotExist:
                raise PermissionDenied
        return _wrapped_view
    return decorator