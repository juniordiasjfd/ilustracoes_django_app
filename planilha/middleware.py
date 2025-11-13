try:
    # asgiref.local.Local é seguro para async (se disponível)
    from asgiref.local import Local
    _user = Local()
except Exception:
    import threading
    _user = threading.local()

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _user.value = request.user if request.user.is_authenticated else None
        try:
            return self.get_response(request)
        finally:
            # Limpa para evitar vazamento entre requisições/threads
            try:
                _user.value = None
            except Exception:
                # Se não for possível limpar, ignore (precaução)
                pass

def get_current_user():
    return getattr(_user, 'value', None)