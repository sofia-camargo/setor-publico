"""Jornadas fictícias por CNPJ para validar IC-01 a IC-04."""

from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from sector.cnpj import cnpj_check_digits
from sector.models import Atendimento, Empresa, Sector
from users.models import Users


def cnpj_demo(number):
    base = f'ZZZZZZZZ{number:04d}'
    return base + cnpj_check_digits(base)


class Command(BaseCommand):
    help = 'Insere empresas e atendimentos [DEMO] de setembro e outubro de 2026.'

    def handle(self, *args, **options):
        if Empresa.objects.filter(razao_social__startswith='[DEMO]').exists():
            self.stdout.write('Empresas [DEMO] já existem; nenhum atendimento duplicado.')
            return
        admin = Users.objects.filter(nivel_acesso='Administrador').first()
        if not admin:
            raise CommandError('Crie o Administrador inicial antes de inserir a demonstração.')
        sectors = {name: Sector.objects.filter(codigo=code).first()
                   for name, code in (('SEBRAE Aqui', 'SEBRAE'), ('Banco do Povo', 'BP'), ('PAT', 'PAT'))}
        if any(value is None for value in sectors.values()):
            raise CommandError('Execute seed_demo antes de seed_cross_demo para criar os setores.')

        journeys = [
            [('SEBRAE Aqui', 9, 10, Atendimento.SEBRAE, None, None),
             ('Banco do Povo', 9, 20, Atendimento.CREDITO, 100000, None),
             ('PAT', 10, 5, Atendimento.VAGA, None, 3)],
            [('SEBRAE Aqui', 9, 12, Atendimento.SEBRAE, None, None),
             ('Banco do Povo', 10, 10, Atendimento.CREDITO, 50000, None)],
            [('SEBRAE Aqui', 9, 20, Atendimento.SEBRAE, None, None),
             ('PAT', 10, 8, Atendimento.VAGA, None, 2)],
            [('Banco do Povo', 9, 22, Atendimento.CREDITO, 50000, None),
             ('PAT', 10, 6, Atendimento.VAGA, None, 2)],
            [('PAT', 10, 15, Atendimento.VAGA, None, 1)],
        ]
        with transaction.atomic():
            count = 0
            for number, journey in enumerate(journeys, 1):
                company = Empresa.objects.create(
                    cnpj=cnpj_demo(number), razao_social=f'[DEMO] Empresa {number}',
                    ramo_atividade='Serviços', bairro='Centro')
                for sector, month, day, kind, credit, vacancies in journey:
                    when = date(2026, month, day)
                    Atendimento.objects.create(
                        empresa=company, setor=sectors[sector], colaborador=admin,
                        data_atendimento=when, desfecho='Resolvido', tipo=kind,
                        valor_credito=Decimal(credit) if credit else None,
                        data_liberacao=when if credit else None,
                        vagas=vacancies, data_abertura_vaga=when if vacancies else None)
                    count += 1
        self.stdout.write(self.style.SUCCESS(f'Criadas 5 empresas e {count} atendimentos [DEMO].'))
