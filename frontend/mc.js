// Data Arrays
const membersData = [
    { name: "أحمد علي", role: "مطور واجهات", status: "online" },
    { name: "سارة محمود", role: "مصممة UI/UX", status: "online" },
    { name: "محمد حسن", role: "مهندس بيانات", status: "offline" },
    { name: "ليلى خالد", role: "محللة أنظمة", status: "online" }
];

const activities = [
    { text: "قام أحمد بتحديث واجهة المستخدم", time: "منذ 5 دقائق" },
    { text: "تم إضافة مهمة جديدة لفرق التطوير", time: "منذ ساعة" },
    { text: "سجلت سارة دخولاً إلى النظام", time: "منذ ساعتين" }
];

// DOM Elements
const membersTable = document.querySelector("#members-table tbody");
const activityFeed = document.getElementById("activity-feed");
const totalMembersSpan = document.getElementById("total-members");
const activeTasksSpan = document.getElementById("active-tasks");
const modal = document.getElementById("member-modal");
const addBtn = document.getElementById("add-member-btn");
const closeBtn = document.querySelector(".close-modal");
const memberForm = document.getElementById("member-form");

// Initialize Data
function init() {
    renderMembers();
    renderActivity();
    updateStats();
}

// Render Members Table
function renderMembers() {
    membersTable.innerHTML = "";
    membersData.forEach((member, index) => {
        const row = `
            <tr>
                <td>${member.name}</td>
                <td>${member.role}</td>
                <td><span class="status-badge ${member.status === 'online' ? 'status-online' : 'status-offline'}">
                    ${member.status === 'online' ? 'نشط' : 'غير نشط'}
                </span></td>
                <td>
                    <button onclick="deleteMember(${index})" style="color: red; border:none; background:none; cursor:pointer">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
        membersTable.innerHTML += row;
    });
}

// Render Activity Feed
function renderActivity() {
    activityFeed.innerHTML = "";
    activities.forEach(act => {
        const li = `
            <li class="activity-item">
                <p>${act.text}</p>
                <span class="activity-time">${act.time}</span>
            </li>
        `;
        activityFeed.innerHTML += li;
    });
}

// Update Dashboard Stats
function updateStats() {
    totalMembersSpan.innerText = membersData.length;
    activeTasksSpan.innerText = Math.floor(Math.random() * 10) + 1; // Simulated count
}

// Modal Logic
addBtn.onclick = () => modal.style.display = "block";
closeBtn.onclick = () => modal.style.display = "none";
window.onclick = (event) => {
    if (event.target == modal) modal.style.display = "none";
};

// Form Submission
memberForm.onsubmit = (e) => {
    e.preventDefault();
    const newName = document.getElementById("member-name").value;
    const newRole = document.getElementById("member-role").value;

    membersData.push({
        name: newName,
        role: newRole,
        status: "online"
    });

    renderMembers();
    updateStats();
    modal.style.display = "none";
    memberForm.reset();
    
    // Add activity
    activities.unshift({ text: `تمت إضافة العضو ${newName} بنجاح`, time: "الآن" });
    renderActivity();
};

// Delete Member
function deleteMember(index) {
    if(confirm("هل أنت متأكد من حذف هذا العضو؟")) {
        membersData.splice(index, 1);
        renderMembers();
        updateStats();
    }
}

// Run app
init();
