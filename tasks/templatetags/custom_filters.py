from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Obtiene un valor de un diccionario usando una clave
    """
    if dictionary is None:
        return None
    return dictionary.get(str(key)) 

@register.filter
def tiene_tratamiento_activo(asignaciones):
    return any(asig.estado in ['pendiente', 'en_progreso'] for asig in asignaciones) 