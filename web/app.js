// Frontend chat logic for QueryPilot.
// Keeps the conversation, sends past turns so follow-ups work, and draws
// each answer (text + chart + table + sql) as a chat bubble.

const $ = (id) => document.getElementById(id);
const messages = $("messages");

let turns = [];       // past turns: {q, sql} — sent back so the model has context
let chartCount = 0;   // gives each chart canvas a unique id

const CHART_COLORS = [
    "#2f6fed", "#f5a623", "#38b26b",
    "#e0567b", "#8a5cf6", "#22b8cf",
];


// wire up the composer and the example chips
$("composer").addEventListener("submit", (e) => {
    e.preventDefault();
    send($("question").value);
});
$("file").onchange = runUpload;
$("demo").onclick = runDemo;
messages.addEventListener("click", (e) => {
    if (e.target.classList.contains("chip")) send(e.target.textContent);
});


async function send(text) {
    const question = text.trim();
    if (!question) return;

    addUser(question);
    $("question").value = "";

    const typing = addTyping();

    const resp = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, history: turns }),
    });
    const data = await resp.json();

    typing.remove();

    if (data.error) {
        addError("Couldn't answer that: " + data.error);
        return;
    }

    addBotAnswer(data);
    turns.push({ q: question, sql: data.sql });  // remember this turn
}


// --- message builders ---

function addUser(text) {
    const el = bubble("user");
    el.querySelector(".bubble").textContent = text;
    scroll();
}


function addError(text) {
    const el = bubble("bot");
    const b = el.querySelector(".bubble");
    b.classList.add("error");
    b.textContent = text;
    scroll();
}


function addTyping() {
    const el = bubble("bot");
    el.querySelector(".bubble").innerHTML =
        '<div class="typing"><span></span><span></span><span></span></div>';
    scroll();
    return el;
}


function addBotAnswer(data) {
    const el = bubble("bot");
    const b = el.querySelector(".bubble");

    // plain-english answer
    const p = document.createElement("p");
    p.className = "answer";
    p.textContent = data.answer;
    b.appendChild(p);

    // one number -> big KPI; otherwise chart + table side by side
    if (data.chart === "kpi") {
        b.appendChild(kpiEl(data.columns, data.rows));
        b.appendChild(tableEl(data.columns, data.rows));
    } else if (data.chart !== "table") {
        const row = document.createElement("div");
        row.className = "result-row";
        row.appendChild(chartEl(data.chart, data.columns, data.rows));
        row.appendChild(tableEl(data.columns, data.rows));
        b.appendChild(row);
    } else {
        b.appendChild(tableEl(data.columns, data.rows));
    }

    // sql + trace, tucked away
    b.appendChild(detailsEl("Show SQL", preEl(data.sql)));
    b.appendChild(detailsEl("How it worked", traceEl(data.trace)));

    scroll();
}


// --- small element helpers ---

function bubble(who) {
    const wrap = document.createElement("div");
    wrap.className = "msg " + who;
    wrap.innerHTML = '<div class="bubble"></div>';
    messages.appendChild(wrap);
    return wrap;
}


function kpiEl(columns, rows) {
    const div = document.createElement("div");
    div.className = "kpi";
    div.innerHTML =
        `<div class="kpi-value">${rows[0][0]}</div>` +
        `<div class="kpi-label">${columns[0]}</div>`;
    return div;
}


function chartEl(type, columns, rows) {
    const box = document.createElement("div");
    box.className = "chart-box";
    const canvas = document.createElement("canvas");
    canvas.id = "chart-" + (++chartCount);
    box.appendChild(canvas);

    const labels = rows.map((r) => r[0]);
    const values = rows.map((r) => r[1]);

    // Chart.js needs the canvas in the DOM before it can size itself
    setTimeout(() => {
        new Chart(canvas, {
            type: type,
            data: {
                labels: labels,
                datasets: [{
                    label: columns[1],
                    data: values,
                    backgroundColor: CHART_COLORS,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: type === "pie" } },
            },
        });
    }, 0);

    return box;
}


function tableEl(columns, rows) {
    const scroll = document.createElement("div");
    scroll.className = "table-scroll";

    let html = "<table><thead><tr>";
    columns.forEach((c) => (html += `<th>${c}</th>`));
    html += "</tr></thead><tbody>";
    rows.forEach((row) => {
        html += "<tr>";
        row.forEach((cell) => (html += `<td>${cell}</td>`));
        html += "</tr>";
    });
    html += "</tbody></table>";

    scroll.innerHTML = html;
    return scroll;
}


function detailsEl(title, child) {
    const d = document.createElement("details");
    const s = document.createElement("summary");
    s.textContent = title;
    d.appendChild(s);
    d.appendChild(child);
    return d;
}


function preEl(text) {
    const pre = document.createElement("pre");
    pre.textContent = text;
    return pre;
}


function traceEl(steps) {
    const ul = document.createElement("ul");
    ul.className = "trace";
    steps.forEach((step) => {
        const li = document.createElement("li");
        li.textContent = step;
        ul.appendChild(li);
    });
    return ul;
}


function scroll() {
    messages.scrollTop = messages.scrollHeight;
}


// --- file upload ---

async function runUpload() {
    const file = $("file").files[0];
    if (!file) return;

    const typing = addTyping();

    const form = new FormData();
    form.append("file", file);

    const resp = await fetch("/upload", { method: "POST", body: form });
    const data = await resp.json();

    typing.remove();
    loadedMessage(`Loaded your file — ${data.table}. Ask me anything about it.`);
    $("file").value = "";   // so re-picking the same file fires onchange again
}


async function runDemo() {
    const typing = addTyping();
    await fetch("/demo", { method: "POST" });
    typing.remove();
    loadedMessage("Demo data loaded — a small sales database (customers, products, orders). Ask me anything about it.");
}


function loadedMessage(text) {
    const el = bubble("bot");
    el.querySelector(".bubble").textContent = text;
    scroll();
}
