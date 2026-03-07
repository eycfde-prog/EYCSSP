// --- Data Structure (Activities) ---
// تأكد أن هذه المصفوفة تحتوي على الـ 160 نشاط بالكامل كما في GitHub
const activitiesData = {
    season: [
        { id: 1, name: "Alike (AS)", icon: "fa-copy", type: "AS" },
        { id: 2, name: "Label (LB)", icon: "fa-tags", type: "LB" },
        { id: 3, name: "Golden Ear (GE)", icon: "fa-ear-listen", type: "GE" },
        { id: 4, name: "Grammar (GR)", icon: "fa-spell-check", type: "GR" },
        { id: 5, name: "Vivid (VV)", icon: "fa-eye", type: "VV" },
        { id: 6, name: "Seeds (SD)", icon: "fa-seedling", type: "SD" },
        // ... (سيتم ملء الباقي من ملف الـ HTML الأصلي)
    ],
    royal: [
        { id: 101, name: "Alike X (ASX)", icon: "fa-bolt", type: "ASX" },
        { id: 102, name: "Label X (LX)", icon: "fa-tag", type: "LX" },
        { id: 103, name: "Grammar X (GRX)", icon: "fa-pen-fancy", type: "GRX" },
        { id: 104, name: "Dictation X (DTX)", icon: "fa-keyboard", type: "DTX" },
        // ... (سيتم ملء الباقي من ملف الـ HTML الأصلي)
    ]
};

// --- MeMe AI Knowledge Base ---
const memeResponses = {
    "hello": "أهلاً بك يا بطل! أنا ميمي، كيف يمكنني مساعدتك اليوم؟",
    "as": "نشاط Alike (AS) يعتمد على مطابقة الجمل والكلمات المتشابهة لتقوية مهارة الملاحظة.",
    "ge": "نشاط Golden Ear (GE) يركز على مهارات الاستماع وتدوين ما تسمعه بدقة.",
    // يتم إضافة بقية الردود من الكود الأصلي
};

// --- Core Functions ---

// 1. Render Stars Background
function createStars() {
    const container = document.getElementById('star-container');
    for (let i = 0; i < 150; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        const size = Math.random() * 3;
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        star.style.left = `${Math.random() * 100}%`;
        star.style.top = `${Math.random() * 100}%`;
        star.style.setProperty('--duration', `${Math.random() * 3 + 2}s`);
        container.appendChild(star);
    }
}

// 2. Switch Between Season & Royal X
function switchType(type, btn) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderCards(type);
}

// 3. Render Activity Cards
function renderCards(type) {
    const grid = document.getElementById('cardsGrid');
    grid.innerHTML = '';
    const data = activitiesData[type];
    
    data.forEach(item => {
        const card = document.createElement('div');
        card.className = 'activity-card';
        card.onclick = () => openActivity(item.id);
        card.innerHTML = `
            <i class="fas ${item.icon} card-icon"></i>
            <h3 style="font-family:'Orbitron'; font-size:0.8rem; color:var(--gold);">${item.name}</h3>
            <span class="tk-activity-badge">${item.type}</span>
        `;
        grid.appendChild(card);
    });
}

// 4. MeMe AI Chat Logic
function openMeMe() {
    document.getElementById('guideOverlay').style.display = 'flex';
}

function closeGuide() {
    document.getElementById('guideOverlay').style.display = 'none';
}

function sendMessage() {
    const input = document.getElementById('chatInput');
    const msg = input.value.trim().toLowerCase();
    if (!msg) return;

    appendMessage(input.value, 'user-msg');
    input.value = '';

    // Simulate AI Thinking
    document.getElementById('loadingChat').style.display = 'block';
    setTimeout(() => {
        document.getElementById('loadingChat').style.display = 'none';
        const response = memeResponses[msg] || "عذراً، لم أفهم سؤالك جيداً. يمكنك سؤالي عن الأنشطة مثل AS أو GE.";
        appendMessage(response, 'meme-msg');
    }, 1000);
}

function appendMessage(text, className) {
    const chatBox = document.getElementById('chatBox');
    const div = document.createElement('div');
    div.className = className;
    div.innerText = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// 5. Initial Execution
window.onload = () => {
    createStars();
    renderCards('season'); // Default view
};
