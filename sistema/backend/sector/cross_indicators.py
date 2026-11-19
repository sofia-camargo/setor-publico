"""IC-01 a IC-04 calculados por CNPJ a partir de atendimentos reais."""

from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Q

from .models import Atendimento


SECTOR_LABELS = {'SEBRAE': 'SEBRAE Aqui', 'BP': 'Banco do Povo', 'PAT': 'PAT'}


def _percent(numerator, denominator):
    if not denominator:
        return None
    return str((Decimal(numerator) * 100 / Decimal(denominator)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def cross_snapshot(start, end):
    # Apenas dados necessários ao cálculo; o retorno não contém CNPJ ou nome.
    rows = Atendimento.objects.select_related('setor').filter(
        Q(data_atendimento__range=(start, end)) |
        Q(data_liberacao__range=(start, end)) |
        Q(data_abertura_vaga__range=(start, end))
    ).values('empresa_id', 'setor__codigo', 'tipo', 'data_atendimento',
             'data_liberacao', 'valor_credito', 'data_abertura_vaga', 'vagas')
    companies = defaultdict(lambda: {'sebrae': [], 'creditos': [], 'pat': [], 'vagas': [], 'setores': set()})
    credit_total = Decimal('0')
    for row in rows:
        sector = SECTOR_LABELS.get(row['setor__codigo'])
        if not sector:
            continue
        company = companies[row['empresa_id']]
        attended = start <= row['data_atendimento'] <= end
        if attended:
            company['setores'].add(sector)
            if sector == 'SEBRAE Aqui':
                company['sebrae'].append(row['data_atendimento'])
            elif sector == 'PAT':
                company['pat'].append(row['data_atendimento'])
        if (sector == 'Banco do Povo' and row['tipo'] == Atendimento.CREDITO
                and row['data_liberacao'] and start <= row['data_liberacao'] <= end):
            company['creditos'].append(row['data_liberacao'])
            credit_total += row['valor_credito'] or 0
        if (sector == 'PAT' and row['tipo'] == Atendimento.VAGA
                and row['data_abertura_vaga'] and start <= row['data_abertura_vaga'] <= end):
            company['vagas'].append((row['data_abertura_vaga'], row['vagas'] or 0))

    sebrae_count = sum(bool(c['sebrae']) for c in companies.values())
    reached_credit = sum(bool(c['sebrae'] and c['creditos'] and
                              min(c['sebrae']) < max(c['creditos'])) for c in companies.values())
    vacancies_after_credit = sum(
        vacancies for c in companies.values() for opened, vacancies in c['vagas']
        if any(released < opened for released in c['creditos'])
    )
    full_journey = sum(
        bool(c['sebrae'] and c['creditos'] and c['pat'] and
             any(min(c['sebrae']) < bp < max(c['pat']) for bp in c['creditos']))
        for c in companies.values()
    )
    attended_companies = sum(bool(c['setores']) for c in companies.values())
    multisector = sum(len(c['setores']) >= 2 for c in companies.values())
    jobs_per_100k = None if credit_total == 0 else str(
        (Decimal(vacancies_after_credit) * 100000 / credit_total)
        .quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    )
    period = {'inicio': start.isoformat(), 'fim': end.isoformat()}
    return [
        {'id': 'IC-01', 'nome': 'Quantas empresas orientadas pelo SEBRAE chegaram ao crédito?',
         'pergunta': 'Quantas empresas orientadas pelo SEBRAE chegaram ao crédito?',
         'valor': _percent(reached_credit, sebrae_count),
         'unidade': '%', 'numerador': reached_credit, 'denominador': sebrae_count,
         'formula': 'CNPJ atendidos no SEBRAE com crédito liberado depois ÷ CNPJ atendidos no SEBRAE × 100',
         'setores': ['SEBRAE Aqui', 'Banco do Povo'], 'origem': 'atendimentos'},
        {'id': 'IC-02', 'nome': 'Retorno em emprego do crédito público',
         'pergunta': 'Cada R$ 100 mil emprestados viram quantas vagas?', 'valor': jobs_per_100k,
         'unidade': 'vagas por R$ 100 mil', 'vagas_apos_credito': vacancies_after_credit,
         'credito_liberado_reais': str(credit_total),
         'formula': 'Vagas abertas após crédito pela mesma empresa ÷ (crédito liberado ÷ 100000)',
         'setores': ['Banco do Povo', 'PAT'], 'origem': 'atendimentos'},
        {'id': 'IC-03', 'nome': 'Jornada completa (funil de 3 etapas)',
         'pergunta': 'Quantas empresas percorreram SEBRAE → Banco do Povo → PAT?', 'valor': full_journey,
         'unidade': 'empresas', 'formula': 'CNPJ com atendimento SEBRAE, liberação de crédito e atendimento PAT, nessa ordem',
         'setores': ['SEBRAE Aqui', 'Banco do Povo', 'PAT'], 'origem': 'atendimentos'},
        {'id': 'IC-04', 'nome': 'Empresas multissetoriais',
         'pergunta': 'Quantas empresas o departamento atende de forma integrada?',
         'valor': _percent(multisector, attended_companies), 'unidade': '%',
         'numerador': multisector, 'denominador': attended_companies,
         'formula': 'CNPJ em pelo menos 2 setores ÷ CNPJ atendidos nos setores de fomento × 100',
         'setores': ['SEBRAE Aqui', 'Banco do Povo', 'PAT'], 'origem': 'atendimentos'},
    ]
