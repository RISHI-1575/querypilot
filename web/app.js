// Frontend logic for QueryPilot.
// Sends the question to the backend and draws the answer, chart and table.

let chart = null;  // the current Chart.js instance, so we can replace it

const $ = (id) => document.getElementById(id);

// wire up the buttons
$("ask-btn").onclick = runAsk;
$("question").addEventListener("keydown", (e) => {
    if (e.key === "Enter") runAsk();
});
$("file").onchange = runUpload;
document.querySelectorAll(".chip").forEach((chip) => {
    chip.onclick = () => {
        $("question").value = chip.textContent;
        runAsk();
    };
});


async function runAsk() {
    const question = $("question").value.trim();
    if (!question) return;

    show("loading");
    hide("result");
    hide("error");

    const resp = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
    });
    const data = await resp.json();

    hide("loading");

    if (data.error) {
        $("error").textContent = "Could not answer: " + data.error;
        show("error");
        return;
    }

    render(data);
}


function render(data) {
    $("answer").textContent = data.answer;
    $("sql").textContent = data.sql;

    // trace list
    $("trace").innerHTML = "";
    data.trace.forEach((step) => {
        const li = document.createElement("li");
        li.textContent = step;
        $("trace").appendChild(li);
    });

    drawTable(data.columns, data.rows);
    drawChart(data.chart, data.columns, data.rows);

    show("result");
}


function drawTable(columns, rows) {
    let html = "<table><thead><tr>";
    columns.forEach((c) => (html += `<th>${c}</th>`));
    html += "</tr></thead><tbody>";
    rows.forEach((row) => {
        html += "<tr>";
        row.forEach((cell) => (html += `<td>${cell}</td>`));
        html += "</tr>";
    });
    html += "</tbody></table>";
    $("table-box").innerHTML = html;
}


function drawChart(type, columns, rows) {
    // reset the KPI and chart areas
    hide("kpi");
    hide("chart-box");
    if (chart) chart.destroy();

    // a single number -> show it big
    if (type === "kpi") {
        $("kpi").textContent = rows[0][0];
        show("kpi");
        return;
    }

    if (type === "table") return;  // table already shown

    // bar / line / pie
    const labels = rows.map((r) => r[0]);
    const values = rows.map((r) => r[1]);
    show("chart-box");

    chart = new Chart($("chart"), {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: columns[1],
                data: values,
                backgroundColor: [
                    "#2f6fed", "#f5a623", "#38b26b",
                    "#e0567b", "#8a5cf6", "#22b8cf",
                ],
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: type === "pie" } },
        },
    });
}


async function runUpload() {
    const file = $("file").files[0];
    if (!file) return;

    $("upload-status").textContent = "loading…";

    const form = new FormData();
    form.append("file", file);

    const resp = await fetch("/upload", { method: "POST", body: form });
    const data = await resp.json();

    $("upload-status").textContent = "loaded table: " + data.table;
}


// small helpers
function show(id) { $(id).classList.remove("hidden"); }
function hide(id) { $(id).classList.add("hidden"); }
