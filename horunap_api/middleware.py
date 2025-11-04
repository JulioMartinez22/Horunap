from django.shortcuts import redirect
from django.urls import reverse

class RedireccionAutenticacionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Si el usuario está autenticado y accede a /users/, redirigir según rol
        if request.user.is_authenticated and request.path == '/users/':
            if request.user.is_superuser or request.user.rol == 'ADMIN':
                return redirect('admin:index')
            elif request.user.rol == 'DOCENTE':
                return redirect('dashboard_docente')
        
        return response