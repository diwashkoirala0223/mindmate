// ================= MindMate app.js (offline-first full features) =================

// Simple storage helpers
const storage = {
  get(k, def) { try { return JSON.parse(localStorage.getItem(k)) ?? def; } catch (e) { return def; } },
  set(k, v) { localStorage.setItem(k, JSON.stringify(v)); }
};

// Today helper
function todayStr() { return new Date().toISOString().slice(0, 10); }

// ---------- Data containers ----------
let foods = storage.get('foods', []); // {date,name,cal}
let water = storage.get('water', { date: todayStr(), today: 0 });
let steps = storage.get('steps', { date: todayStr(), today: 0 });
let weights = storage.get('weights', []); // {date,kg}
let bp = storage.get('bp', []); // {date,bpm}
let sleeps = storage.get('sleeps', []); // {date,hours}
let moods = storage.get('moods', []); // {date,emotion,type}
let journals = storage.get('journals', []); // {date,text}
let badges = storage.get('badges', []);
let chatHistory = storage.get('chats', []);

// ---------- Small local nutrition DB (sample) ----------
const foodDB = [
  { name: 'Apple', cal: 95 },
  { name: 'Banana', cal: 105 },
  { name: 'Egg (large)', cal: 78 },
  { name: 'Rice (1 cup)', cal: 205 },
  { name: 'Bread slice', cal: 80 },
  { name: 'Chicken breast (100g)', cal: 165 },
  { name: 'Salad (basic)', cal: 35 },
  { name: 'Milk (250ml)', cal: 122 },
  { name: 'Yogurt (100g)', cal: 59 },
  { name: 'Orange', cal: 62 },
  { name: 'Almonds (10)', cal: 70 },
  { name: 'Chocolate (30g)', cal: 160 }
];

// ---------- UI helpers ----------
function $(id) { return document.getElementById(id); }
function randomItem(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

// ---------- Greeting & encouragement ----------
const encouragements = [
  "You're doing better than you think.",
  "Small steps are still progress—well done for being here.",
  "Breathe — one thing at a time.",
  "You deserve rest and kindness today.",
  "You matter. Take one small step right now."
];
function greetUser() {
  if ($('welcomeTitle')) $('welcomeTitle').innerText = `Hello — ${new Date().toLocaleDateString()}`;
  if ($('welcomeMsg')) $('welcomeMsg').innerText = "Take a deep breath. MindMate is here to help.";
}
function generateEncouragement() {
  if ($('encourage')) $('encourage').innerText = randomItem(encouragements);
}

// ---------- PHYSICAL: Food & calories ----------
function suggestFoods() {
  if (!$('foodSuggestions')) return;
  $('foodSuggestions').innerHTML = '';
  foodDB.slice(0, 8).forEach(f => {
    const btn = document.createElement('button');
    btn.innerText = `${f.name} (${f.cal} kcal)`;
    btn.onclick = () => { $('foodSearch').value = f.name; $('foodCalInput').value = f.cal; };
    $('foodSuggestions').appendChild(btn);
  });
}
function addFoodFromUI() {
  const name = $('foodSearch').value.trim();
  let cal = parseInt($('foodCalInput').value);
  if (!name) return alert('Enter food name');
  if (!cal) {
    const db = foodDB.find(x => x.name.toLowerCase() === name.toLowerCase());
    cal = db ? db.cal : 0;
    if (!cal) cal = parseInt(prompt('Enter calories for ' + name) || 0);
  }
  foods.push({ date: todayStr(), name, cal });
  storage.set('foods', foods);
  $('foodSearch').value = ''; $('foodCalInput').value = '';
  renderFoodList();
  checkBadges();
}
function renderFoodList() {
  if (!$('foodList')) return;
  const todayFoods = foods.filter(f => f.date === todayStr());
  $('foodList').innerHTML = todayFoods.map(f => `<div>${f.name} — ${f.cal} kcal</div>`).join('');
  const total = todayFoods.reduce((s, f) => s + f.cal, 0);
  if ($('calTotal')) $('calTotal').innerText = total;
}
function clearFoods() { foods = foods.filter(f => f.date !== todayStr()); storage.set('foods', foods); renderFoodList(); }

// ---------- PHYSICAL: Water ----------
function ensureToday(obj) {
  if (!obj.date || obj.date !== todayStr()) { obj.date = todayStr(); if (obj.today !== undefined) obj.today = 0; }
}
function addWater(amount) {
  ensureToday(water);
  water.today = (water.today || 0) + amount;
  storage.set('water', water);
  renderWater();
  checkBadges();
}
function renderWater() {
  ensureToday(water);
  if ($('waterTotal')) $('waterTotal').innerText = water.today || 0;
  const pct = Math.min(100, Math.round((water.today / 2000) * 100));
  if ($('waterFill')) $('waterFill').style.width = pct + '%';
}
function resetWater() { water = { date: todayStr(), today: 0 }; storage.set('water', water); renderWater(); }

// ---------- PHYSICAL: Steps ----------
function addSteps(n) { ensureToday(steps); steps.today = (steps.today || 0) + n; storage.set('steps', steps); renderSteps(); checkBadges(); }
function addCustomSteps() { const v = parseInt($('stepInput')?.value || 0); if (v > 0) addSteps(v); if ($('stepInput')) $('stepInput').value = ''; }
function renderSteps() { if ($('stepsTotal')) $('stepsTotal').innerText = steps.today || 0; }

// ---------- PHYSICAL: Heartbeat ----------
function saveBpm() { const v = parseInt($('bpmInput')?.value || 0); if (!v) return alert('Enter BPM'); bp.push({ date: new Date().toISOString(), bpm: v }); storage.set('bp', bp); if ($('lastBpm')) $('lastBpm').innerText = v; $('bpmInput').value = ''; }
function simulateBpm() { const v = 55 + Math.round(Math.random() * 60); bp.push({ date: new Date().toISOString(), bpm: v }); storage.set('bp', bp); if ($('lastBpm')) $('lastBpm').innerText = v; }

// ---------- PHYSICAL: Weight & chart ----------
let weightChart = null;
function saveWeight() { const v = parseFloat($('weightInput')?.value || 0); if (!v) return alert('Enter weight'); weights.push({ date: todayStr(), kg: v }); storage.set('weights', weights); $('weightInput').value = ''; renderWeightChart(); }
function renderWeightChart() {
  if (!$('weightChart')) return;
  const ctx = $('weightChart').getContext('2d');
  const labels = weights.map(w => w.date);
  const data = weights.map(w => w.kg);
  if (weightChart) weightChart.destroy();
  weightChart = new Chart(ctx, { type: 'line', data: { labels, datasets: [{ label: 'Weight (kg)', data, borderColor: '#2f6fd6', fill: false }] }, options: { scales: { y: { beginAtZero: false } } } });
}

// ---------- PHYSICAL: Sleep ----------
function saveSleep() { const v = parseFloat($('sleepHours')?.value || 0); if (!v) return alert('Enter hours'); sleeps.push({ date: todayStr(), hours: v }); storage.set('sleeps', sleeps); if ($('lastSleep')) $('lastSleep').innerText = v; $('sleepHours').value = ''; checkBadges(); }

// ---------- BADGES & ACHIEVEMENTS ----------
function checkBadges() {
  // example badges
  ensureToday(water);
  ensureToday(steps);
  if ((water.today || 0) >= 2000 && !badges.includes('Hydration Champion')) badges.push('Hydration Champion');
  if ((steps.today || 0) >= 10000 && !badges.includes('Step Master')) badges.push('Step Master');
  storage.set('badges', badges);
  renderBadges();
}
function renderBadges() {
  if (!$('badges')) return;
  $('badges').innerHTML = '';
  if (badges.length === 0) $('badges').innerText = 'No badges yet — meet daily goals to earn them.';
  badges.forEach(b => { const d = document.createElement('div'); d.className = 'list'; d.innerText = `🏅 ${b}`; $('badges').appendChild(d); });
}

// ---------- MENTAL: Emotions & logging ----------
const positiveEmotions = ["Accepted", "Acknowledged", "Amused", "Appreciated", "Attracted", "Attractive", "Calm", "Capable", "Caring", "Competent", "Confident", "Connected", "Considered", "Content", "Creative", "Curious", "Delighted", "Empowered", "Encouraged", "Enthusiastic", "Excited", "Exhilarated", "Grateful", "Happy", "Hopeful", "Important", "Included", "Independent", "Inspired", "Interested", "Liberated", "Loved", "Nurtured", "Passionate", "Protected", "Proud", "Reassured", "Relaxed", "Relieved", "Respected", "Safe", "Satisfied", "Secure", "Stimulated", "Supported", "Surprised", "Trusted", "Trusting", "Understood", "Valued", "Welcome"];
const negativeEmotions = ["Abandoned", "Afraid", "Angry", "Anxious", "Belittled", "Betrayed", "Concerned", "Confused", "Controlled", "Deceived", "Defeated", "Defensive", "Devastated", "Disappointed", "Disconnected", "Discounted", "Discouraged", "Disrespected", "Embarrassed", "Excluded", "Foolish", "Frustrated", "Grief", "Guilty", "Humiliated", "Inadequate", "Inferior", "Insecure", "Jealous", "Lonely", "Manipulated", "Nervous", "Obligated", "Offended", "Overwhelmed", "Panic", "Powerless", "Pressured", "Regret", "Rejected", "Resentful", "Sad", "Shame", "Shocked", "Surprised", "Trapped", "Unappreciated", "Unattractive", "Violated", "Vulnerable", "Worried"];

function renderEmotionButtons() {
  if (!$('emotionContainer')) return;
  const container = $('emotionContainer'); container.innerHTML = '';
  positiveEmotions.forEach(e => {
    const b = document.createElement('button'); b.className = 'emotionBtn'; b.innerText = e;
    b.onclick = () => { logEmotion(e, 'positive'); };
    container.appendChild(b);
  });
  negativeEmotions.forEach(e => {
    const b = document.createElement('button'); b.className = 'emotionBtn'; b.innerText = e;
    b.onclick = () => { logEmotion(e, 'negative'); };
    container.appendChild(b);
  });
}
function logEmotion(emotion, type) {
  moods.push({ date: new Date().toISOString(), emotion, type });
  storage.set('moods', moods);
  if ($('emLogged')) $('emLogged').innerText = moods.filter(m => m.date.slice(0, 10) === todayStr()).length;
  alert('Logged: ' + emotion);
}

// ---------- MENTAL: Mood insights (hourly/daily/weekly/monthly) ----------
function showMoodInsights() {
  const now = Date.now();
  const last24 = moods.filter(m => new Date(m.date) > new Date(now - 24 * 3600 * 1000));
  const last7 = moods.filter(m => new Date(m.date) > new Date(now - 7 * 24 * 3600 * 1000));
  const last30 = moods.filter(m => new Date(m.date) > new Date(now - 30 * 24 * 3600 * 1000));
  function top(list) {
    if (list.length === 0) return 'No data';
    const counts = {}; list.forEach(i => counts[i.emotion] = (counts[i.emotion] || 0) + 1);
    return Object.entries(counts).sort((a, b) => b[1] - a[1])[0].join(' (') + ')';
  }
  if ($('insights')) $('insights').innerText = `Last 24h: ${last24.length} logs. Top: ${top(last24)}. Last 7d: ${last7.length} logs. Top: ${top(last7)}. Last 30d: ${last30.length} logs. Top: ${top(last30)}.`;
}

// ---------- JOURNAL ----------
function saveJournal() {
  const txt = $('journalText')?.value.trim();
  if (!txt) return alert('Write something first');
  journals.push({ date: new Date().toISOString(), text: txt });
  storage.set('journals', journals);
  $('journalText').value = '';
  alert('Journal saved');
}
function showJournal() {
  if (!$('journalList')) return;
  $('journalList').innerHTML = '';
  if (journals.length === 0) { $('journalList').innerText = 'No entries yet'; return; }
  journals.slice().reverse().forEach(j => {
    const d = document.createElement('div'); d.className = 'list'; d.innerText = `${new Date(j.date).toLocaleString()}: ${j.text}`; $('journalList').appendChild(d);
  });
}


// ---------- Standalone AI Assistant (Therapist Logic) ----------
const therapistPatterns = {
  greeting: {
    keywords: ["hello", "hi", "hey", "start"],
    responses: [
      "Hello. I'm here to listen. How are you feeling today?",
      "Hi there. This is a safe space. What's on your mind?",
      "Welcome. I'm ready to support you. Where would you like to start?"
    ]
  },
  anxiety: {
    keywords: ["anxious", "worry", "panic", "scared", "nervous", "future"],
    responses: [
      "It sounds like you're carrying a lot of anxiety. Can you tell me what specifically is triggering these feelings?",
      "I hear your worry. Let's focus on the present moment. Have you tried the 4-7-8 breathing exercise in the 'Breathing' tab?",
      "Anxiety can feel overwhelming, but it doesn't define you. What is one small thing you can control right now?"
    ]
  },
  depression: {
    keywords: ["sad", "depressed", "hopeless", "down", "cry", "lonely"],
    responses: [
      "I'm sorry you're going through this darkness. You don't have to face it alone. How long have you been feeling this way?",
      "It takes courage to admit you're struggling. Be gentle with yourself. What does your body need right now—rest, water, or maybe just a deep breath?",
      "I hear that you're in pain. Sometimes just naming the feeling can help. Would you say you're feeling more 'empty' or 'heavy'?"
    ]
  },
  crisis: {
    keywords: ["suicide", "kill myself", "die", "end it", "hurt myself"],
    responses: [
      "I'm very concerned about what you're saying. If you are in danger, please call emergency services (112 or 988) immediately. I am an AI and cannot physically help, but your life matters.",
      "Please reach out to a crisis hotline or a trusted person right now. You deserve support in this difficult moment."
    ]
  },
  sleep: {
    keywords: ["sleep", "insomnia", "tired", "awake"],
    responses: [
      "Sleep struggles are often linked to a busy mind. Have you tried a 'body scan' meditation before bed?",
      "It's frustrating when rest won't come. Try to lower the lights and avoid screens. Would you like a sleep hygiene tip?"
    ]
  },
  gratitude: {
    keywords: ["happy", "good", "great", "better", "thanks"],
    responses: [
      "I'm so glad to hear that! What do you think contributed to this positive feeling?",
      "That's wonderful. Holding onto these moments is key. Have you written this down in your journal yet?",
      "You're welcome. I'm proud of the steps you're taking."
    ]
  },
  admiration: {
    keywords: ["admiration", "respectful", "appreciative"],
    responses: [
      "I see you admire something or someone. Can you share what it is?",
      "Admiration is a powerful feeling. What inspires you the most right now?",
      "Feeling appreciation can uplift you. Who or what are you thinking about?",
      "It's wonderful to feel respect and admiration. How does it make you feel internally?",
      "Let's explore this feeling of admiration together. What stands out to you?"
    ]
  },
  // ... adding more from server.py (truncated for brevity in chunk but I'll include enough to match the user's expectations)
  calm: {
    keywords: ["calm", "peaceful", "relaxed"],
    responses: [
      "Feeling calm is wonderful. What helps you achieve this?",
      "Peace can be grounding. Can you describe this serene moment?",
      "Relaxation is a gift. How does your body feel in this calm state?"
    ]
  },
  confusion: {
    keywords: ["confusion", "uncertainty", "puzzled"],
    responses: [
      "Feeling confused is normal. Can you describe what’s unclear?",
      "Uncertainty can be stressful. What would help clarify things?"
    ]
  }
};

const fallbackResponses = [
  "I'm listening. Tell me more about that.",
  "How does that make you feel?",
  "I see. Go on.",
  "Can you help me understand what you mean by that?",
  "That sounds important. Why do you think that is?"
];

function getTherapistResponseLocal(userText) {
  const textLower = userText.toLowerCase();

  // 1. Check for specific patterns
  for (const category in therapistPatterns) {
    const data = therapistPatterns[category];
    for (const keyword of data.keywords) {
      if (textLower.includes(keyword)) {
        return randomItem(data.responses);
      }
    }
  }

  // 2. General empathy (Mirroring)
  if (userText.length > 10 && textLower.includes(" feel ")) {
    const parts = textLower.split(" feel ");
    if (parts.length > 1) {
      const feeling = parts[1].split(" ")[0];
      return `It sounds like those feelings are really strong. Why do you think you feel ${feeling}?`;
    }
  }

  // 3. Fallback
  return randomItem(fallbackResponses);
}

// ---------- AI Assistant (Bridge to Backend) ----------
// Connects to Python Flask server on port 5000

async function sendChat() {
  const input = $('chatInput');
  if (!input) return;

  const text = input.value.trim();
  if (!text) return;

  // User message
  chatHistory.push({ role: 'user', text, date: new Date().toISOString() });
  storage.set('chats', chatHistory);
  renderChat();
  input.value = '';

  // Try backend first
  try {
    const res = await fetch("https://mindmate-backend.onrender.com/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });

    if (!res.ok) throw new Error("Backend not reachable");

    const data = await res.json();
    const reply = data.reply;

    chatHistory.push({ role: 'bot', text: reply, date: new Date().toISOString() });
    storage.set('chats', chatHistory);
    renderChat();
    return;

  } catch (err) {
    console.warn("Backend failed, using offline mode");
  }

  // Fallback: offline therapist
  setTimeout(() => {
    const reply = getTherapistResponseLocal(text);
    chatHistory.push({ role: 'bot', text: reply, date: new Date().toISOString() });
    storage.set('chats', chatHistory);
    renderChat();
  }, 600);
}
function renderChat() {
  if (!$('chatBox')) return;
  $('chatBox').innerHTML = '';
  chatHistory.slice().reverse().forEach(m => {
    const el = document.createElement('div'); el.style.padding = '6px'; el.style.margin = '6px 0';
    if (m.role === 'user') { el.style.textAlign = 'right'; el.style.background = '#eef6ff'; el.innerText = 'You: ' + m.text; }
    else { el.style.textAlign = 'left'; el.style.background = '#f7fbff'; el.innerText = 'MindMate: ' + m.text; }
    $('chatBox').appendChild(el);
  });
}

// ---------- BREATHING ENGINE (20 presets) ----------
const breathingPresets = [
  { id: 'box', name: 'Box Breathing (4-4-4-4)', pattern: [{ label: 'Inhale', ms: 4000 }, { label: 'Hold', ms: 4000 }, { label: 'Exhale', ms: 4000 }, { label: 'Hold', ms: 4000 }], use: 'Calm + focus' },
  { id: '4-7-8', name: '4-7-8 (Sleep/Anxiety)', pattern: [{ label: 'Inhale', ms: 4000 }, { label: 'Hold', ms: 7000 }, { label: 'Exhale', ms: 8000 }], use: 'Sleep + anxiety' },
  { id: 'diaphragmatic', name: 'Diaphragmatic (Deep)', pattern: [{ label: 'Inhale', ms: 5000 }, { label: 'Exhale', ms: 5000 }], use: 'Relaxation' },
  { id: 'coherent', name: 'Coherent Breathing (5-5)', pattern: [{ label: 'Inhale', ms: 5000 }, { label: 'Exhale', ms: 5000 }], use: 'Balance' },
  { id: 'resonant', name: 'Resonant (6/min)', pattern: [{ label: 'Inhale', ms: 5000 }, { label: 'Exhale', ms: 5000 }], use: 'Nervousness' },
  { id: 'sama', name: 'Sama Vritti', pattern: [{ label: 'Inhale', ms: 4000 }, { label: 'Exhale', ms: 4000 }], use: 'Calm' },
  { id: 'relax1', name: 'Quick Calm (3-4-5)', pattern: [{ label: 'Inhale', ms: 3000 }, { label: 'Hold', ms: 4000 }, { label: 'Exhale', ms: 5000 }], use: 'Quick calming' },
  { id: 'energize', name: 'Energize Breath (fast)', pattern: [{ label: 'Inhale', ms: 500 }, { label: 'Exhale', ms: 500 }], use: 'Energy boost' },
  { id: 'alternate', name: 'Alternate Nostril (paced)', pattern: [{ label: 'Inhale', ms: 4000 }, { label: 'Exhale', ms: 4000 }], use: 'Balance' },
  { id: 'lion', name: 'Lion Breath (release)', pattern: [{ label: 'Inhale', ms: 2000 }, { label: 'Exhale', ms: 2000 }], use: 'Release tension' },
  { id: 'soothing', name: 'Soothing Breath', pattern: [{ label: 'Inhale', ms: 4000 }, { label: 'Exhale', ms: 6000 }], use: 'Soothing nervous system' },
  { id: 'mindful', name: 'Mindful Counting', pattern: [{ label: 'Inhale', ms: 4000 }, { label: 'Exhale', ms: 4000 }], use: 'Focus' },
  { id: 'box-short', name: 'Box Short (2-2-2-2)', pattern: [{ label: 'Inhale', ms: 2000 }, { label: 'Hold', ms: 2000 }, { label: 'Exhale', ms: 2000 }, { label: 'Hold', ms: 2000 }], use: 'Quick calm' },
  { id: 'bell', name: 'Bell Breath (sound-led)', pattern: [{ label: 'Inhale', ms: 4500 }, { label: 'Exhale', ms: 4500 }], use: 'Relaxation' },
  { id: 'humming', name: 'Humming Breath', pattern: [{ label: 'Inhale', ms: 4000 }, { label: 'Exhale', ms: 4000 }], use: 'Vagal tone' },
  { id: 'progressive', name: 'Progressive Longer Exhale', pattern: [{ label: 'Inhale', ms: 3000 }, { label: 'Exhale', ms: 6000 }], use: 'Anxiety' },
  { id: 'stabilize', name: 'Stabilizing Breath', pattern: [{ label: 'Inhale', ms: 4000 }, { label: 'Exhale', ms: 4000 }], use: 'Composure' },
  { id: 'focus', name: 'Focus Breath', pattern: [{ label: 'Inhale', ms: 3500 }, { label: 'Exhale', ms: 3500 }], use: 'Concentration' },
  { id: 'sleep', name: 'Sleep Prep (slow)', pattern: [{ label: 'Inhale', ms: 6000 }, { label: 'Hold', ms: 2000 }, { label: 'Exhale', ms: 8000 }], use: 'Sleep' },
  { id: 'calm-hold', name: 'Calm with Hold', pattern: [{ label: 'Inhale', ms: 4000 }, { label: 'Hold', ms: 4000 }, { label: 'Exhale', ms: 7000 }], use: 'Deep calm' }
];

let breathTimer = null, breathPhase = 0, breathPattern = [];
function renderBreathOptions() {
  if (!$('breathSelect')) return;
  const sel = $('breathSelect'); sel.innerHTML = '';
  breathingPresets.forEach(p => { const opt = document.createElement('option'); opt.value = p.id; opt.innerText = `${p.name} — ${p.use}`; sel.appendChild(opt); });
}
function startBreathing() {
  if (!$('breathSelect')) return;
  const id = $('breathSelect').value;
  const preset = breathingPresets.find(p => p.id === id) || breathingPresets[0];
  breathPattern = preset.pattern; breathPhase = 0;
  runBreathPhase();
}
function runBreathPhase() {
  if (!breathPattern.length) return;
  const step = breathPattern[breathPhase];
  if ($('breathText')) $('breathText').innerText = step.label;
  const circle = $('breathCircle');
  if (step.label.toLowerCase().includes('inhale')) circle.style.transform = 'scale(1.6)';
  else if (step.label.toLowerCase().includes('exhale')) circle.style.transform = 'scale(0.8)';
  else circle.style.transform = 'scale(1.1)';
  breathTimer = setTimeout(() => { breathPhase = (breathPhase + 1) % breathPattern.length; runBreathPhase(); }, step.ms);
}
function stopBreathing() { clearTimeout(breathTimer); if ($('breathText')) $('breathText').innerText = 'Stopped'; if ($('breathCircle')) $('breathCircle').style.transform = 'scale(1)'; }

// ---------- Notifications (demo) ----------
['notifBtn', 'notifBtn2', 'notifBtn3'].forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener('click', () => {
    if ("Notification" in window && Notification.permission !== 'granted') {
      Notification.requestPermission().then(p => { if (p === 'granted') alert('Notifications enabled'); else alert('Permission denied'); });
    } else if ("Notification" in window && Notification.permission === 'granted') {
      new Notification('MindMate — Reminder', { body: 'Time for a quick check-in or breathing exercise!' });
    } else alert('Notifications not supported.');
  });
});

// ---------- Export / Dashboard ----------
function renderSnapshot() {
  if (!$('snapshot')) return;
  const calToday = foods.filter(f => f.date === todayStr()).reduce((s, f) => s + f.cal, 0);
  const waterToday = (storage.get('water', { today: 0 }).today) || 0;
  const stepsToday = (storage.get('steps', { today: 0 }).today) || 0;
  const moodToday = moods.filter(m => m.date.slice(0, 10) === todayStr()).map(m => m.emotion).slice(-3);
  $('snapshot').innerHTML = `<li>Calories: ${calToday} kcal</li><li>Water: ${waterToday} ml</li><li>Steps: ${stepsToday}</li><li>Recent moods: ${moodToday.join(', ') || '—'}</li>`;
}
function exportData() {
  const data = { foods, water, steps, weights, bp, sleeps, moods, journals, chatHistory, badges };
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = $('downloadLink'); a.href = url; a.download = 'mindmate-data.json'; a.innerText = 'Download data';
}

// ---------- Init & render ----------

// ---------- Init & render ----------
function renderAll() {
  greetUser();
  generateEncouragement();
  suggestFoods();
  renderFoodList();
  renderWater();
  renderSteps();
  renderEmotionButtons();
  renderBreathOptions();
  renderChat();
  renderWeightChart();
  renderBadges();
  renderSnapshot();

  if ($('emLogged')) $('emLogged').innerText = moods.filter(m => m.date.slice(0, 10) === todayStr()).length;
}

// ---------- Visual Effects (Scroll Reveal) ----------
function initVisuals() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = 1;
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, { threshold: 0.1 });

  // Target all cards and major sections
  document.querySelectorAll('.card, .hero, .tile').forEach(el => {
    el.style.opacity = 0;
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
    observer.observe(el);
  });
}

window.addEventListener('load', () => {
  renderAll();
  initVisuals();
});

// ---------- Utility exposures for HTML buttons ----------
window.addFoodFromUI = addFoodFromUI;
window.addWater = addWater;
window.addSteps = addSteps;
window.addCustomSteps = addCustomSteps;
window.saveBpm = saveBpm;
window.simulateBpm = simulateBpm;
window.saveWeight = saveWeight;
window.saveSleep = saveSleep;
window.clearFoods = clearFoods;
window.saveJournal = saveJournal;
window.showJournal = showJournal;
window.sendChat = sendChat;
window.startBreathing = startBreathing;
window.stopBreathing = stopBreathing;
window.generateEncouragement = generateEncouragement;
window.showMoodInsights = showMoodInsights;
window.exportData = exportData;
window.renderWeightChart = renderWeightChart;
window.renderFoodList = renderFoodList;
window.renderBadges = renderBadges;


