const tokenInput = document.getElementById('token');
const statusText = document.getElementById('status');
const messages = document.getElementById('messages');
const form = document.getElementById('chat-form');
const questionInput = document.getElementById('question');
const sendButton = document.getElementById('send');

function headers() {
  const value = tokenInput.value.trim();
  return value ? { Authorization: `Bearer ${value}` } : {};
}

async function checkStatus() {
  try {
    const response = await fetch('/api/status', { headers: headers() });
    const data = await response.json();
    statusText.textContent = response.ok
      ? `${data.mensagem} Arquivos encontrados: ${data.arquivos}.`
      : data.erro;
    statusText.style.color = response.ok && data.pronto ? '#087b73' : '#9b392f';
  } catch {
    statusText.textContent = 'Não foi possível consultar o servidor local.';
  }
}

function addMessage(role, content, sources = []) {
  const box = document.createElement('article');
  box.className = `message ${role}`;
  const label = document.createElement('span');
  label.className = 'role';
  label.textContent = role === 'user' ? 'VOCÊ' : 'GAFIA';
  const text = document.createElement('div');
  text.textContent = content;
  box.append(label, text);
  if (sources.length) {
    const footer = document.createElement('div');
    footer.className = 'sources';
    footer.textContent = 'Trechos consultados: ' + sources.map(
      source => source.arquivo + (source.pagina ? `, página ${source.pagina}` : '')
    ).join(' · ');
    box.append(footer);
  }
  messages.append(box);
  box.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

tokenInput.addEventListener('change', checkStatus);
form.addEventListener('submit', async event => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;
  addMessage('user', question);
  questionInput.value = '';
  sendButton.disabled = true;
  statusText.textContent = 'Consultando os documentos…';
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...headers() },
      body: JSON.stringify({ pergunta: question })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.erro || 'Falha na consulta.');
    addMessage('assistant', data.resposta, data.fontes);
  } catch (error) {
    addMessage('assistant', `Não foi possível responder: ${error.message}`);
  } finally {
    sendButton.disabled = false;
    checkStatus();
    questionInput.focus();
  }
});

checkStatus();
