from django import template
from django.utils.safestring import mark_safe

# adicionando ícones na interface HTML
register = template.Library()
@register.filter
def boolean_to_icon(value):
    """
    Converte um valor booleano em um ícone Font Awesome:
    True -> <i class="fa fa-check-circle text-success"></i>
    False -> <i class="fa fa-times-circle text-danger"></i>
    """
    if value:
        # Ícone de check verde (sucesso)
        # icon_html = '<span class="fa fa-check-circle text-success" title="Ativo">✅</span>'
        icon_html = '<span class="fa fa-check-circle text-success" title="Ativo"></span>'
    else:
        # Ícone de X vermelho (perigo/erro)
        # icon_html = '<span class="fa fa-times-circle text-danger" title="Inativo">❌</span>'
        icon_html = '<span class="fa fa-times-circle text-danger" title="Inativo"></span>'
    # mark_safe é essencial para que o Django renderize o HTML e não o escape como texto puro
    return mark_safe(icon_html)