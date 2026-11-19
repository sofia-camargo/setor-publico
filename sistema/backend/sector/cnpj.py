"""Normalização e dígitos verificadores do CNPJ numérico ou alfanumérico."""

import re

from django.core.exceptions import ValidationError


def normalize_cnpj(value):
    return re.sub(r"[.\-/\s]", "", str(value or "")).upper()


def cnpj_check_digits(base):
    digits = base
    for weights in ((5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2),
                    (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)):
        total = sum((ord(char) - 48) * weight for char, weight in zip(digits, weights))
        remainder = total % 11
        digits += str(0 if remainder < 2 else 11 - remainder)
    return digits[-2:]


def validate_cnpj(value):
    cnpj = normalize_cnpj(value)
    if not re.fullmatch(r"[A-Z0-9]{12}[0-9]{2}", cnpj):
        raise ValidationError("Informe um CNPJ de 14 caracteres, com dois dígitos numéricos finais.")
    if len(set(cnpj)) == 1 or cnpj_check_digits(cnpj[:12]) != cnpj[-2:]:
        raise ValidationError("CNPJ com dígitos verificadores inválidos.")
    return cnpj
