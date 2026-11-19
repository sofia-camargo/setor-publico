(function () {
  const token = localStorage.getItem('jwt_token');
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  if (!token || !user) { window.top.location.replace('index.html'); return; }

  const apiBase = `http://${window.location.hostname}:8000/api/v1`;
  const start = document.getElementById('cross-start');
  const end = document.getElementById('cross-end');
  const status = document.getElementById('cross-status');
  const cards = document.getElementById('cross-cards');
  const charts = document.getElementById('cross-charts');
  const table = document.getElementById('cross-table-body');
  const periodLabel = document.getElementById('cross-period-label');
  const denied = document.getElementById('cross-denied');
  const colors = ['#087eae', '#1a9b7a', '#d99318', '#6e67b8'];
  const icons = ['fa-route', 'fa-briefcase', 'fa-filter-circle-dollar', 'fa-people-group'];

  function iso(date) {
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
  }
  function br(value) { return value ? value.split('-').reverse().join('/') : ''; }
  const today = new Date();
  start.value = iso(new Date(today.getFullYear(), 0, 1));
  end.value = iso(today);

  function displayValue(item) {
    if (item.valor === null || item.valor === undefined) return 'Não calculável';
    if (item.unidade === '%') return `${Number(item.valor).toLocaleString('pt-BR', { maximumFractionDigits: 2 })}%`;
    if (item.unidade === 'empresas') return `${Number(item.valor).toLocaleString('pt-BR')} empresas`;
    return `${Number(item.valor).toLocaleString('pt-BR', { maximumFractionDigits: 2 })} vagas / R$ 100 mil`;
  }
  function detail(item) {
    if (item.id === 'IC-01' || item.id === 'IC-04') return `${item.numerador} de ${item.denominador} empresas`;
    if (item.id === 'IC-02') return `${item.vagas_apos_credito} vagas após R$ ${Number(item.credito_liberado_reais).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
    return 'CNPJ presentes nos três setores, em ordem cronológica';
  }
  function chartValue(item) {
    if (item.valor === null) return 0;
    return item.unidade === '%' ? Math.min(Number(item.valor), 100) : Number(item.valor);
  }

  function render(indicators, period) {
    periodLabel.textContent = `${br(period.inicio)} a ${br(period.fim)}`;
    cards.replaceChildren(); charts.replaceChildren(); table.replaceChildren();
    const numericMax = Math.max(1, ...indicators.filter(item => item.unidade !== '%').map(item => chartValue(item)));
    indicators.forEach((item, index) => {
      const color = colors[index % colors.length];
      const card = document.createElement('article');
      card.className = 'cross-card'; card.style.setProperty('--card-color', color);
      card.innerHTML = `<div class="cross-card-head"><span class="cross-card-id">${item.id}</span><span class="cross-card-icon"><i class="fa-solid ${icons[index]}"></i></span></div><h3>${item.nome}</h3><div class="cross-card-value">${displayValue(item)}</div><div class="cross-card-detail">${detail(item)}</div>`;
      cards.append(card);

      const chart = document.createElement('div'); chart.className = 'cross-chart';
      if (item.unidade === '%') {
        const value = chartValue(item);
        chart.innerHTML = `<h3>${item.id} · ${item.nome}</h3><div class="cross-donut" style="--chart-color:${color};--chart-value:${value}" data-label="${item.valor === null ? '—' : `${Number(item.valor).toLocaleString('pt-BR',{maximumFractionDigits:1})}%`}"></div><div class="cross-chart-output">${detail(item)}</div>`;
      } else {
        const height = Math.max(5, chartValue(item) / numericMax * 100);
        chart.innerHTML = `<h3>${item.id} · ${item.nome}</h3><div class="cross-bar-track"><div class="cross-bar" style="--chart-color:${color};height:${height}%"></div></div><div class="cross-chart-output">${displayValue(item)}</div>`;
      }
      charts.append(chart);

      const row = document.createElement('tr');
      row.innerHTML = `<td>${item.id}</td><td><strong>${item.nome}</strong><small class="cross-question">${item.pergunta || ''}</small></td><td class="cross-result">${displayValue(item)}</td><td class="cross-formula">${item.formula}</td><td>${item.setores.map(sector => `<span class="cross-pill">${sector}</span>`).join('')}</td>`;
      table.append(row);
    });
  }

  async function load() {
    if (!start.value || !end.value || start.value > end.value) { status.textContent = 'Informe um período válido.'; return; }
    status.textContent = 'Atualizando indicadores…';
    document.getElementById('cross-apply').disabled = true;
    try {
      const params = new URLSearchParams({ inicio: start.value, fim: end.value });
      const response = await fetch(`${apiBase}/dashboard/cruzados/?${params}`, { headers: { Authorization: `Bearer ${token}` } });
      const data = await response.json();
      if (response.status === 401) { localStorage.clear(); window.top.location.replace('index.html'); return; }
      if (response.status === 403) {
        document.querySelectorAll('.cross-hero,.cross-filters,.cross-cards,.cross-grid,.cross-table-panel').forEach(element => element.hidden = true);
        denied.hidden = false; return;
      }
      if (!response.ok) throw new Error(data.erro || data.detail || 'Não foi possível carregar os indicadores.');
      render(data.indicadores, data.periodo);
      status.textContent = `Atualizado para ${br(data.periodo.inicio)} a ${br(data.periodo.fim)}.`;
    } catch (error) { status.textContent = error.message; }
    finally { document.getElementById('cross-apply').disabled = false; }
  }

  document.getElementById('cross-apply').addEventListener('click', load);
  document.getElementById('cross-export').addEventListener('click', () => window.print());
  load();
})();
