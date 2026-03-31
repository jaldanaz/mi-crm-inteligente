import phonenumbers
from rapidfuzz import fuzz

def normalizar_telefono(numero, region="CL"):
    try:
        parsed = phonenumbers.parse(numero, region)
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except:
        return numero

def calcular_similitud(nombre1, nombre2):
    # Usa Jaro-Winkler para detectar si "Juan Perez" es igual a "Juan Perz"
    return fuzz.token_sort_ratio(nombre1, nombre2)
