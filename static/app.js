const $ = (id) => document.getElementById(id);
const samples = {
  package: "[ERROR] [launch]: package 'robot_bringup' not found, searching: ['/opt/ros/humble']",
  tf: "[WARN] [tf2_ros]: Lookup would require extrapolation into the future. Requested time 12.4, latest data is 12.1",
  qos: "[WARN] [rclcpp]: New publisher discovered on topic '/camera/image_raw', offering incompatible QoS. No messages will be received."
};
const escapeHtml = (value) => String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const severityClass = (value) => ['high','medium','low'].includes(value) ? value : 'unknown';
const labels = {high:'HIGH PRIORITY',medium:'MEDIUM',low:'LOW',unknown:'UNCLASSIFIED'};
let selectedImage = null;
let previewUrl = null;

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
function clearSelectedImage() {
  selectedImage = null;
  $('screen-input').value = '';
  $('image-preview-wrap').hidden = true;
  $('image-result').hidden = true;
  if (previewUrl) URL.revokeObjectURL(previewUrl);
  previewUrl = null;
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
$('screen-input').addEventListener('change', () => {
  $('image-error').hidden = true;
  $('image-result').hidden = true;
  const file = $('screen-input').files?.[0];
  selectedImage = null;
  if (previewUrl) URL.revokeObjectURL(previewUrl);
  previewUrl = null;
  if (!file) { $('image-preview-wrap').hidden = true; return; }
  if (!['image/png','image/jpeg','image/webp'].includes(file.type)) {
    $('image-error').hidden = false;
    $('image-error').textContent = 'Choose a PNG, JPEG, or WebP screenshot.';
    $('screen-input').value = '';
    $('image-preview-wrap').hidden = true;
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    $('image-error').hidden = false;
    $('image-error').textContent = 'Image exceeds the 5 MiB limit.';
    $('screen-input').value = '';
    $('image-preview-wrap').hidden = true;
    return;
  }
  selectedImage = file;
  previewUrl = URL.createObjectURL(file);
  $('image-preview').src = previewUrl;
  $('image-preview-wrap').hidden = false;
});
$('clear-image').addEventListener('click', clearSelectedImage);
$('diagnose-image').addEventListener('click', async () => {
  $('image-error').hidden = true;
  $('image-result').hidden = true;
  if (!selectedImage) {
    $('image-error').hidden = false;
    $('image-error').textContent = 'Choose a screenshot first.';
    return;
  }
  const button = $('diagnose-image');
  button.disabled = true;
  button.textContent = 'Analyzing screenshot…';
  try {
    const form = new FormData();
    form.append('image', selectedImage, selectedImage.name);
    form.append('question', $('screen-question').value.trim());
    const response = await fetch('/api/diagnose-image', {method:'POST',body:form});
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Could not analyze screenshot.');
    $('image-explanation').textContent = data.ai_explanation || 'No explanation returned.';
    $('image-result').hidden = false;
  } catch (err) {
    $('image-error').hidden = false;
    $('image-error').textContent = err instanceof Error ? err.message : 'Unexpected screenshot-analysis error.';
  } finally {
    button.disabled = false;
    button.textContent = 'Analyze screenshot ↗';
  }
});
refreshHealth();
