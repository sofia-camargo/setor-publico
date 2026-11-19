from io import StringIO
from unittest.mock import patch

import bcrypt
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from users.models import Users


class BootstrapAdminTest(TestCase):
    @patch("users.management.commands.bootstrap_admin.getpass", side_effect=["SenhaForte1!", "SenhaForte1!"])
    def test_creates_first_admin_and_refuses_second(self, _getpass):
        call_command("bootstrap_admin", matricula="admin-local", nome="Admin Local", stdout=StringIO())
        admin = Users.objects.get(matricula="admin-local")
        self.assertEqual(admin.nivel_acesso, "Administrador")
        self.assertTrue(bcrypt.checkpw(b"SenhaForte1!", admin.senha_hash.encode("utf-8")))
        with self.assertRaises(CommandError):
            call_command("bootstrap_admin", matricula="outro", nome="Outro", stdout=StringIO())
