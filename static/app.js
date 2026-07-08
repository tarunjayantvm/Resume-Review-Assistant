const form = document.getElementById('analyze-form');
const resultArea = document.getElementById('analysis-result');
const loading = document.getElementById('loading');
const chatForm = document.getElementById('chat-form');
const chatLog = document.getElementById('chat-log');
const chatInput = document.getElementById('chat-input');

let currentResumeText = '';
let currentAnalysis = null;
let currentJobRole = '';

function renderResult(analysis) {
  resultArea.innerHTML = '';
  resultArea.classList.remove('hidden');

  const cards = [
    { title: 'ATS compatibility', value: `${analysis.ats.score}/100`, detail: analysis.ats.summary },
    { title: 'Formatting', value: `${analysis.formatting.score}/100`, detail: analysis.formatting.summary },
    { title: 'Grammar', value: `${analysis.grammar.score}/100`, detail: analysis.grammar.summary },
  ];

  cards.forEach((card) => {
    const div = document.createElement('div');
    div.className = 'metric-card';
    div.innerHTML = `
      <strong>${card.title}</strong>
      <div class="metric-row"><span>Score</span><span>${card.value}</span></div>
      <div class="metric-row"><span>Note</span><span>${card.detail}</span></div>
    `;
    resultArea.appendChild(div);
  });

  const skillCard = document.createElement('div');
  skillCard.className = 'metric-card';
  skillCard.innerHTML = `
    <strong>Missing keywords</strong>
    <div class="metric-row"><span>${analysis.missing_skills.length ? analysis.missing_skills.join(', ') : 'No major gaps detected'}</span></div>
  `;
  resultArea.appendChild(skillCard);

  const summaryCard = document.createElement('div');
  summaryCard.className = 'metric-card';
  summaryCard.innerHTML = `
    <strong>Professional summary</strong>
    <p>${analysis.professional_summary}</p>
  `;
  resultArea.appendChild(summaryCard);

  const bulletCard = document.createElement('div');
  bulletCard.className = 'metric-card';
  bulletCard.innerHTML = `
    <strong>Achievement-oriented bullets</strong>
    <ul>${analysis.achievement_bullets.map((b) => `<li>${b.replace(/^[-•]\s*/, '')}</li>`).join('')}</ul>
  `;
  resultArea.appendChild(bulletCard);

  const suggestionsCard = document.createElement('div');
  suggestionsCard.className = 'metric-card';
  suggestionsCard.innerHTML = `
    <strong>Suggested improvements</strong>
    <ul>${analysis.suggestions.map((s) => `<li>${s}</li>`).join('')}</ul>
  `;
  resultArea.appendChild(suggestionsCard);
}

function appendMessage(text, role) {
  const bubble = document.createElement('div');
  bubble.className = `bubble ${role}`;
  bubble.textContent = text;
  chatLog.appendChild(bubble);
  chatLog.scrollTop = chatLog.scrollHeight;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  loading.classList.remove('hidden');
  resultArea.classList.add('hidden');

  const formData = new FormData(form);
  try {
    const response = await fetch('/api/analyze', { method: 'POST', body: formData });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Analysis failed');

    currentAnalysis = data.analysis;
    currentResumeText = data.resume_text;
    currentJobRole = formData.get('job_role');
    renderResult(currentAnalysis);
    appendMessage(`Resume analyzed for ${currentJobRole}. Ask me anything about improvements.`, 'bot');
  } catch (error) {
    resultArea.classList.remove('hidden');
    resultArea.innerHTML = `<div class="metric-card">${error.message}</div>`;
  } finally {
    loading.classList.add('hidden');
  }
});

chatForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!currentAnalysis) {
    appendMessage('Upload and analyze a resume first so I can tailor the advice.', 'bot');
    return;
  }

  const message = chatInput.value.trim();
  if (!message) return;

  appendMessage(message, 'user');
  chatInput.value = '';

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, job_role: currentJobRole, resume_text: currentResumeText, analysis: currentAnalysis }),
    });
    const data = await response.json();
    appendMessage(data.reply || 'No reply available.', 'bot');
  } catch (error) {
    appendMessage('Chat request failed. Please try again.', 'bot');
  }
});
