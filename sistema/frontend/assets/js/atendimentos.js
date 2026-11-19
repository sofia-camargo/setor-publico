(function () {
    const token = localStorage.getItem('jwt_token');
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    if (!token || !user) { window.top.location.replace('index.html'); return; }
    const api = `http://${window.location.hostname}:8000/api/v1`;
    const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
    const byId = id => document.getElementById(id);
    let company = null;
    const today = new Date();
    const todayText = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    byId('attendance-date').value = todayText;
    byId('attendance-date').max = todayText;
    byId('released').max = todayText;
    byId('opened').max = todayText;

    async function request(path, options = {}) {
        const response = await fetch(`${api}/${path}`, { ...options, headers });
        const data = await response.json();
        if (!response.ok) throw new Error(data.erro || data.detail || JSON.stringify(data));
        return data;
    }
    function chooseCompany(item) {
        company = item;
        const previous = item.setores_atendidos && item.setores_atendidos.length
            ? ` Já atendida em: ${item.setores_atendidos.join(', ')}.` : '';
        byId('company-found').textContent = `Empresa vinculada: ${item.razao_social} (${item.cnpj}).${previous}`;
        byId('attendance-company').textContent = `Empresa: ${item.razao_social}`;
        byId('company-new').hidden = true;
        byId('save-attendance').disabled = false;
    }
    byId('cnpj').addEventListener('input', () => {
        company = null;
        byId('save-attendance').disabled = true;
        byId('company-found').textContent = '';
        byId('company-new').hidden = true;
        byId('attendance-company').textContent = 'Busque ou cadastre a empresa antes de salvar.';
    });
    byId('company-search').addEventListener('click', async () => {
        try {
            const cnpj = byId('cnpj').value.trim();
            if (!cnpj) throw new Error('Informe o CNPJ.');
            const found = await request(`empresas/?cnpj=${encodeURIComponent(cnpj)}`);
            if (found.length) chooseCompany(found[0]);
            else { byId('company-new').hidden = false; byId('company-found').textContent = 'CNPJ não encontrado. Complete o cadastro.'; }
        } catch (error) { byId('company-found').textContent = error.message; }
    });
    byId('company-form').addEventListener('submit', async event => {
        event.preventDefault();
        try {
            const item = await request('empresas/', { method: 'POST', body: JSON.stringify({
                cnpj: byId('cnpj').value, razao_social: byId('razao-social').value,
                ramo_atividade: byId('ramo').value, bairro: byId('bairro').value,
            }) });
            chooseCompany(item);
        } catch (error) { byId('company-found').textContent = error.message; }
    });
    if (user.nivel_acesso === 'Administrador') {
        byId('sector-wrap').hidden = false;
        request('setores/').then(sectors => {
            byId('sector').replaceChildren(...sectors.map(item => {
                const option = document.createElement('option');
                option.value = item.id_setor; option.textContent = item.nome; return option;
            }));
        }).catch(error => { byId('attendance-status').textContent = error.message; });
    }
    function updateType() {
        const kind = byId('attendance-type').value;
        document.querySelectorAll('.credit-fields').forEach(field => { field.hidden = kind !== 'BP_LIBERACAO'; });
        document.querySelectorAll('.vacancy-fields').forEach(field => { field.hidden = kind !== 'PAT_VAGA'; });
        byId('credit').required = byId('released').required = kind === 'BP_LIBERACAO';
        byId('vacancies').required = byId('opened').required = kind === 'PAT_VAGA';
    }
    byId('attendance-type').addEventListener('change', updateType);
    updateType();
    byId('attendance-form').addEventListener('submit', async event => {
        event.preventDefault();
        if (!company) return;
        const kind = byId('attendance-type').value;
        const payload = { empresa: company.id, data_atendimento: byId('attendance-date').value,
            tipo: kind, desfecho: byId('outcome').value };
        if (user.nivel_acesso === 'Administrador') payload.setor = Number(byId('sector').value);
        if (kind === 'BP_LIBERACAO') { payload.valor_credito = byId('credit').value; payload.data_liberacao = byId('released').value; }
        if (kind === 'PAT_VAGA') { payload.vagas = Number(byId('vacancies').value); payload.data_abertura_vaga = byId('opened').value; }
        try {
            const saved = await request('atendimentos/', { method: 'POST', body: JSON.stringify(payload) });
            byId('attendance-status').textContent = `Atendimento ${saved.id} salvo. Os indicadores cruzados já consideram esse registro.`;
            byId('attendance-form').reset();
            byId('attendance-date').value = todayText;
            updateType();
        } catch (error) { byId('attendance-status').textContent = error.message; }
    });
})();
