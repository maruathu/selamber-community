const apiBase = "http://127.0.0.1:8000";

function escapeHtml(value) {
  const entities = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  };
  return String(value).replace(/[&<>"']/g, (character) => entities[character]);
}

async function fetchJson(url, options = {}) {
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (options.admin) {
    const token = document.getElementById("admin-token").value.trim();
    if (token) {
      headers.Authorization = "Bearer " + token;
    }
  }
  const { admin, ...requestOptions } = options;
  const response = await fetch(`${apiBase}${url}`, {
    ...requestOptions,
    headers,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Request failed");
  }

  return response.json();
}

async function loadStats() {
  const stats = await fetchJson("/stats");
  document.getElementById("stat-communities").textContent = stats.communities;
  document.getElementById("stat-confessions").textContent = stats.confessions;
  document.getElementById("stat-comments").textContent = stats.comments;
  document.getElementById("stat-reports").textContent = stats.reports;
}

async function loadCommunities() {
  const communities = await fetchJson("/communities");
  const list = document.getElementById("communities");
  list.innerHTML = communities.length
    ? communities.map((item) => `<li><strong>${escapeHtml(item.name)}</strong><div>${escapeHtml(item.description || "No description")}</div></li>`).join("")
    : "<li>No communities yet.</li>";
}

async function loadConfessions() {
  const confessions = await fetchJson("/confessions");
  const list = document.getElementById("confessions");
  list.innerHTML = confessions.length
    ? confessions.map((item) => `<li><strong>${escapeHtml(item.title || "Untitled")}</strong><div>${escapeHtml(item.body)}</div><button type="button" class="moderate-content" data-content-id="${item.id}" data-status="hidden">Hide</button></li>`).join("")
    : "<li>No confessions yet.</li>";
}

async function loadReports() {
  const reports = await fetchJson("/reports", { admin: true });
  const list = document.getElementById("reports");
  list.innerHTML = reports.length
    ? reports.map((item) => `<li><strong>Report #${item.id}</strong><div>${escapeHtml(item.category)}: ${escapeHtml(item.reason || "No reason provided")}</div><button type="button" class="review-report" data-report-id="${item.id}" data-status="resolved">Resolve</button><button type="button" class="review-report secondary-action" data-report-id="${item.id}" data-status="dismissed">Dismiss</button></li>`).join("")
    : "<li>No pending reports.</li>";
}

async function loadHiddenConfessions() {
  const hidden = await fetchJson("/moderation/hidden-confessions", { admin: true });
  const list = document.getElementById("hidden-confessions");
  list.innerHTML = hidden.length
    ? hidden.map((item) => `<li><strong>${escapeHtml(item.title || "Untitled")}</strong><div>${escapeHtml(item.body)}</div><button type="button" class="moderate-content" data-content-id="${item.id}" data-status="published">Restore</button></li>`).join("")
    : "<li>No hidden confessions.</li>";
}

async function refreshDashboard() {
  try {
    await Promise.all([loadStats(), loadCommunities(), loadConfessions()]);
  } catch (error) {
    console.error(error);
    alert("Could not load data from the API.");
  }
  const adminMessage = "Enter a valid admin token to view moderation tools.";
  try {
    await Promise.all([loadReports(), loadHiddenConfessions()]);
  } catch (error) {
    console.error(error);
    document.getElementById("reports").innerHTML = `<li>${adminMessage}</li>`;
    document.getElementById("hidden-confessions").innerHTML = `<li>${adminMessage}</li>`;
  }
}

document.getElementById("community-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const form = new FormData(event.target);
    const payload = Object.fromEntries(form.entries());
    payload.description = payload.description?.trim() || null;

    await fetchJson("/communities", {
      method: "POST",
      admin: true,
      body: JSON.stringify(payload),
    });

    event.target.reset();
    await refreshDashboard();
  } catch (error) {
    console.error(error);
    alert("Could not create community. Check the form and admin token.");
  }
});

document.getElementById("confession-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const form = new FormData(event.target);
    const payload = Object.fromEntries(form.entries());
    payload.community_id = Number(payload.community_id);
    payload.telegram_id = Number(payload.telegram_id);

    await fetchJson("/confessions", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    event.target.reset();
    await refreshDashboard();
  } catch (error) {
    console.error(error);
    alert("Could not create confession. Check the form and API connection.");
  }
});

document.getElementById("admin-token").value = sessionStorage.getItem("selamber-admin-token") || "";
document.getElementById("admin-token").addEventListener("change", (event) => {
  sessionStorage.setItem("selamber-admin-token", event.target.value.trim());
  refreshDashboard();
});

document.getElementById("reports").addEventListener("click", async (event) => {
  const button = event.target.closest(".review-report");
  if (!button) return;
  try {
    await fetchJson(`/reports/${button.dataset.reportId}`, {
      method: "PATCH",
      admin: true,
      body: JSON.stringify({ status: button.dataset.status }),
    });
    await refreshDashboard();
  } catch (error) {
    console.error(error);
    alert("Could not review report. Check the admin token and try again.");
  }
});

async function moderateContentClick(event) {
  const button = event.target.closest(".moderate-content");
  if (!button) return;
  try {
    await fetchJson(`/confessions/${button.dataset.contentId}/moderation`, {
      method: "PATCH",
      admin: true,
      body: JSON.stringify({ status: button.dataset.status }),
    });
    await refreshDashboard();
  } catch (error) {
    console.error(error);
    alert("Could not moderate confession. Check the admin token and try again.");
  }
}

document.getElementById("confessions").addEventListener("click", moderateContentClick);
document.getElementById("hidden-confessions").addEventListener("click", moderateContentClick);

document.getElementById("refresh-btn").addEventListener("click", refreshDashboard);

refreshDashboard();
