const $ = (id) => document.getElementById(id);
const samples = {
  package: "[ERROR] [launch]: package 'robot_bringup' not found, searching: ['/opt/ros/humble']",
  tf: "[WARN] [tf2_ros]: Lookup would require extrapolation into the future. Requested time 12.4, latest data is 12.1",
  qos: "[WARN] [rclcpp]: New publisher discovered on topic '/camera/image_raw', offering incompatible QoS. No messages will be received."
};
const escapeHtml = (value) => String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const severityClass = (value) => ['high','medium','low'].includes(value) ? value : 'unknown';
const labels = {high:'HIGH PRIORITY',medium:'MEDIUM',low:'LOW',unknown:'UNCLASSIFIED'};

async function refreshHealth() {
  try {
    const response = await fetch('/api/health');
    const data = await response.json();
    $('mode-label').textContent = data.ai_configured ? `AI ready · ${data.model}` : 'Heuristic mode';
  } catch (_) { $('mode-label').textContent = 'API status unavailable'; }
}
function setBusy(busy) {
  $('diagnose').disabled = busy;
  $('diagnose').innerHTML = busy ? '<span class="spinner"></span><span>Reading log…</span>' : '<span>Diagnose log</span><span aria-hidden="true">↗</span>';
}
function renderDiagnostics(items) {
  $('diagnostics').innerHTML = items.map(item => `
    <article class="diagnostic-card">
      <div class="diagnostic-head"><span class="severity ${severityClass(item.severity)}">${escapeHtml(labels[item.severity] || labels.unknown)}</span><span class="rule-id">${escapeHtml(item.id)}</span></div>
      <h3>${escapeHtml(item.title)}</h3><p class="why">${escapeHtml(item.why)}</p>
      ${item.evidence?.length ? `<div class="subhead">MATCHED EVIDENCE</div><ul class="evidence">${item.evidence.map(line=>`<li><code>${escapeHtml(line)}</code></li>`).join('')}</ul>` : ''}
      <div class="subhead">NEXT CHECKS</div><ul class="checks">${(item.checks||[]).map(s=>`<li>${escapeHtml(s)}</li>`).join('')}</ul>
      <div class="subhead">SUGGESTED COMMANDS · REVIEW FIRST</div><div class="commands">${(item.commands||[]).map(cmd=>`<code>${escapeHtml(cmd)}</code>`).join('')}</div>
    </article>`).join('');
}
function render(data) {
  $('empty-state').hidden = true; $('results').hidden = false;
  $('result-tag').textContent = `${data.input_lines} NON-EMPTY LINES`;
  $('summary').textContent = data.summary;
  renderDiagnostics(data.diagnostics || []);
  $('ai-block').hidden = !data.ai_explanation;
  if (data.ai_explanation) {
    $('ai-status').textContent = data.ai_used ? 'MODEL RESPONDED' : '';
    $('ai-explanation').textContent = data.ai_explanation;
  }
  $('ai-note').hidden = !data.ai_note;
  $('ai-note').textContent = data.ai_note || '';
}
$('log-input').addEventListener('input', () => $('char-count').textContent = `${$('log-input').value.length.toLocaleString()} / 20,000 characters`);
$('load-sample').addEventListener('click', () => {
  const key = $('sample-select').value;
  if (!key) { $('error').hidden = false; $('error').textContent = 'Choose a sample log first.'; return; }
  $('log-input').value = samples[key];
  $('log-input').dispatchEvent(new Event('input'));
  $('error').hidden = true;
});
$('diagnose').addEventListener('click', async () => {
  const log_text = $('log-input').value.trim();
  $('error').hidden = true;
  if (!log_text) { $('error').hidden = false; $('error').textContent = 'Paste a log or load a sample before diagnosing.'; return; }
  setBusy(true);
  try {
    const response = await fetch('/api/diagnose', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({log_text,use_ai:$('use-ai').checked})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Could not diagnose this log.');
    render(data);
  } catch (err) {
    $('error').hidden = false;
    $('error').textContent = err instanceof Error ? err.message : 'Unexpected error while diagnosing.';
  } finally { setBusy(false); }
});
refreshHealth();
