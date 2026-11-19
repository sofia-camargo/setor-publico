"""Cria o primeiro administrador em uma instalação local vazia."""

from getpass import getpass

import bcrypt
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from rest_framework.exceptions import ValidationError

from users.models import Users
from users.validators import validar_senha


class Command(BaseCommand):
    help = "Cria o primeiro administrador do SIGDEI, sem gravar senha em arquivo ou comando."

    def add_arguments(self, parser):
        parser.add_argument("--matricula", help="Matrícula do administrador")
        parser.add_argument("--nome", help="Nome do administrador")

    def handle(self, *args, **options):
        if Users.objects.exists():
            raise CommandError("Já existem usuários. Use as rotas administrativas do SIGDEI.")

        matricula = (options["matricula"] or input("Matrícula: ")).strip()
        nome = (options["nome"] or input("Nome: ")).strip()
        if not matricula or not nome:
            raise CommandError("Matrícula e nome são obrigatórios.")

        password = getpass("Senha inicial: ")
        confirmation = getpass("Confirme a senha: ")
        if password != confirmation:
            raise CommandError("As senhas não coincidem.")
        try:
            validar_senha(password)
        except ValidationError as exc:
            raise CommandError(str(exc)) from exc

        with transaction.atomic():
            if Users.objects.exists():
                raise CommandError("Já existem usuários. Importação interrompida.")
            Users.objects.create(
                matricula=matricula,
                nome=nome,
                senha_hash=bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
                nivel_acesso="Administrador",
                primeiro_acesso=True,
            )

        self.stdout.write(self.style.SUCCESS("Administrador inicial criado. Altere a senha no primeiro acesso."))
