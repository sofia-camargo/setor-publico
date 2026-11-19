import re
from rest_framework.exceptions import ValidationError


def validar_senha(senha):
    if not senha:
        raise ValidationError(
            "A senha é obrigatória."
        )

    if len(senha) < 6:
        raise ValidationError(
            "A senha deve ter no mínimo 6 caracteres."
        )

    if not re.search(r'[A-Z]', senha):
        raise ValidationError(
            "A senha deve conter pelo menos uma letra maiúscula."
        )

    if not re.search(r'[a-z]', senha):
        raise ValidationError(
            "A senha deve conter pelo menos uma letra minúscula."
        )

    if not re.search(r'\d', senha):
        raise ValidationError(
            "A senha deve conter pelo menos um número."
        )

    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=]', senha):
        raise ValidationError(
            "A senha deve conter pelo menos um caractere especial."
        )

    return senha