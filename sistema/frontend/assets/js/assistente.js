(function () {
    const token = localStorage.getItem('jwt_token');
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    if (!token || !user) { window.top.location.replace('index.html'); return; }

    const apiBase = `http://${window.location.hostname}:8000/api/v1`;
    const status = document.getElementById('assistant-status');
    const messages = document.getElementById('assistant-messages');
    const form = document.getElementById('assistant-form');
    const question = document.getElementById('assistant-question');
    const button = document.getElementById('assistant-send');
    const start = document.getElementById('assistant-start');
    const end = document.getElementById('assistant-end');
    const headers = { Authorization: `Bearer ${token}` };

    const strategicBadge = document.getElementById('assistant-strategic-badge');
    if (strategicBadge && !user.visao_estrategica) strategicBadge.hidden = true;

    const today = new Date();
    const localDate = value => `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, '0')}-${String(value.getDate()).padStart(2, '0')}`;
    start.value = localDate(new Date(today.getFullYear(), 0, 1));
    end.value = localDate(today);

    async function refreshStatus() {
        try {
            const response = await fetch(`${apiBase}/assistente/status/`, { headers });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || data.erro || 'Acesso indisponível.');
            const documents = data.documentos_prontos
                ? `${data.arquivos} arquivo(s) indexado(s)`
                : 'documentos ainda não indexados';
            status.textContent = `${data.mensagem} Modelo: ${data.modelo}. Fontes: dados autorizados e ${documents}.`;
        } catch (error) {
            status.textContent = `RAG indisponível: ${error.message}`;
        }
    }

    function sourceLabel(item) {
        if (item.tipo === 'documento' || item.arquivo) {
            return `${item.arquivo || item.rotulo}${item.pagina ? `, página ${item.pagina}` : ''}`;
        }
        const period = item.periodo ? `, ${item.periodo.inicio} a ${item.periodo.fim}` : '';
        const sector = item.setor ? `, ${item.setor}` : '';
        return `${item.rotulo || item.indicador || item.referencia}${sector}${period}`;
    }

    function addMessage(role, content, sources) {
        const box = document.createElement('article');
        box.className = `assistant-message ${role}`;
        const label = document.createElement('strong');
        label.textContent = role === 'user' ? 'VOCÊ' : 'ASSISTENTE RAG';
        const text = document.createElement('div');
        text.textContent = content;
        box.append(label, text);
        if (sources && sources.length) {
            const footer = document.createElement('div');
            footer.className = 'assistant-sources';
            footer.textContent = `Fontes recuperadas: ${sources.map(sourceLabel).join(' · ')}`;
            box.append(footer);
        }
        messages.append(box);
        box.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }

    form.addEventListener('submit', async event => {
        event.preventDefault();
        const text = question.value.trim();
        if (!text) return;
        addMessage('user', text);
        question.value = '';
        button.disabled = true;
        status.textContent = 'Recuperando contexto autorizado e gerando a resposta…';
        try {
            const response = await fetch(`${apiBase}/assistente/perguntar/`, {
                method: 'POST',
                headers: { ...headers, 'Content-Type': 'application/json' },
                body: JSON.stringify({ pergunta: text, inicio: start.value, fim: end.value })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.erro || data.detail || 'Falha na consulta.');
            addMessage('assistant', data.resposta, data.fontes);
        } catch (error) {
            addMessage('assistant', `Não foi possível responder: ${error.message}`);
        } finally {
            button.disabled = false;
            refreshStatus();
            question.focus();
        }
    });

    refreshStatus();
})();
