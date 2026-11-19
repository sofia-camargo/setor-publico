"""Dados sintéticos de setembro e outubro para testar o SIGDEI local."""

from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from projects.models import Project, Tarefa
from sector.models import Atividade, Indicador, Sector
from users.models import Users


INDICATORS = {
    "SEBRAE Aqui": [
        ("Atendimentos empresariais", 24, 30),
        ("Oficinas realizadas", 4, 5),
    ],
    "PAT": [
        ("Vagas captadas", 21, 23),
        ("Encaminhamentos realizados", 18, 20),
    ],
    "Banco do Povo": [
        ("Operações de crédito liberadas", 7, 9),
        ("Crédito liberado em reais", 42000, 51000),
    ],
    "PROCON": [
        ("Reclamações registradas", 10, 9),
        ("Casos resolvidos", 8, 8),
    ],
}


class Command(BaseCommand):
    help = "Insere dados fictícios identificados por [DEMO], sem alterar registros existentes."

    def handle(self, *args, **options):
        if Indicador.objects.filter(nome__startswith="[DEMO]").exists():
            self.stdout.write("Dados [DEMO] já existem; nenhuma duplicação foi feita.")
            return
        admin = Users.objects.filter(nivel_acesso="Administrador").order_by("id_usuario").first()
        if admin is None:
            raise CommandError("Crie o Administrador inicial antes de inserir dados de demonstração.")

        with transaction.atomic():
            sectors = {}
            indicator_count = 0
            activity_count = 0
            for sector_name, specs in INDICATORS.items():
                code = {'SEBRAE Aqui': 'SEBRAE', 'Banco do Povo': 'BP',
                        'PAT': 'PAT', 'PROCON': 'PROCON'}[sector_name]
                sector = Sector.objects.filter(nome=sector_name).first()
                if sector is None:
                    sector = Sector.objects.create(nome=sector_name, codigo=code)
                elif sector.codigo != code:
                    sector.codigo = code
                    sector.save(update_fields=['codigo'])
                sectors[sector_name] = sector
                for label, september, october in specs:
                    indicator = Indicador.objects.create(
                        id_setor=sector, nome=f"[DEMO] {label}", tipo_dado="Número"
                    )
                    indicator_count += 1
                    for month, total in ((9, september), (10, october)):
                        first = total // 2
                        for day, value in ((15, first), (24, total - first)):
                            Atividade.objects.create(
                                id_indicador=indicator,
                                id_usuario=admin,
                                valor=Decimal(value),
                                data_cadastro=date(2026, month, day),
                            )
                            activity_count += 1

            projects = [
                {
                    "nome": "[DEMO] Balcão digital de empregos",
                    "setor": sectors["PAT"],
                    "inicio": date(2026, 9, 1),
                    "fim": date(2026, 11, 30),
                    "prioridade": "Alta",
                    "status": "Em andamento",
                    "tarefas": [
                        ("[DEMO] Levantar requisitos", date(2026, 9, 2), date(2026, 9, 18), True, date(2026, 9, 16)),
                        ("[DEMO] Desenhar formulários", date(2026, 9, 19), date(2026, 10, 10), True, date(2026, 10, 9)),
                        ("[DEMO] Testar cadastro de vagas", date(2026, 10, 11), date(2026, 11, 10), False, None),
                    ],
                },
                {
                    "nome": "[DEMO] Painel de microcrédito",
                    "setor": sectors["Banco do Povo"],
                    "inicio": date(2026, 9, 5),
                    "fim": date(2026, 12, 15),
                    "prioridade": "Média",
                    "status": "Em andamento",
                    "tarefas": [
                        ("[DEMO] Organizar dados de crédito", date(2026, 9, 6), date(2026, 9, 25), True, date(2026, 9, 24)),
                        ("[DEMO] Conferir indicadores", date(2026, 9, 26), date(2026, 10, 20), False, None),
                        ("[DEMO] Revisar visualizações", date(2026, 10, 21), date(2026, 11, 20), False, None),
                    ],
                },
            ]
            task_count = 0
            for spec in projects:
                project = Project.objects.create(
                    nome=spec["nome"],
                    data_inicio=spec["inicio"],
                    data_fim=spec["fim"],
                    prioridade=spec["prioridade"],
                    status_tag=spec["status"],
                    id_responsavel=admin,
                    id_setor=spec["setor"],
                )
                for name, start, end, done, finished in spec["tarefas"]:
                    Tarefa.objects.create(
                        id_projeto=project,
                        nome_tarefa=name,
                        responsavel_nome="Equipe de demonstração",
                        data_inicio=start,
                        data_final=end,
                        concluida=done,
                        data_conclusao=finished,
                    )
                    task_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Criados {indicator_count} indicadores, {activity_count} lançamentos, "
            f"{len(projects)} projetos e {task_count} tarefas [DEMO]."
        ))
