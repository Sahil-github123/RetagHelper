#!/usr/bin/env python3
"""
RetagHelper v2 — IIT Bombay CPI/SPI Retag Calculator
======================================================
Run:   python retag_helper.py
Open:  http://localhost:5000

New in v2:
  • Save state  → downloads a .json file you can reload later
  • Load state  → upload a previously saved .json to restore everything
  • Retag Summary panel  → CPI impact, tag-wise credit breakdown, retagged course list
  • Total CPI credits shown in topbar
  • Tag-wise credit strip under topbar (with deltas)
"""

import json, webbrowser, threading, time
from http.server import HTTPServer, BaseHTTPRequestHandler

# ── Initial course data (from history.xlsx) ───────────────────────────────────
INITIAL_DATA = {
    "semesters": [
        {
            "id": "s1", "name": "Semester 1",
            "courses": [
                {"id":"c1",  "code":"AE 103",  "name":"Historical Perspective of Aerospace Engg.",     "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c2",  "code":"BB 101",  "name":"Biology",                                        "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c3",  "code":"CH 117",  "name":"Chemistry Lab",                                  "tag":"C", "newTag":"C", "credits":3, "grade":"AA"},
                {"id":"c4",  "code":"GC 101",  "name":"Gender in the Workplace",                        "tag":"N", "newTag":"N", "credits":0, "grade":"PP"},
                {"id":"c5",  "code":"MA 105",  "name":"Calculus",                                       "tag":"C", "newTag":"C", "credits":8, "grade":"AA"},
                {"id":"c6",  "code":"MS 101",  "name":"Makerspace",                                     "tag":"C", "newTag":"C", "credits":8, "grade":"AA"},
                {"id":"c7",  "code":"NOCS01",  "name":"NCC/NSS/NSO",                                    "tag":"N", "newTag":"N", "credits":0, "grade":"PP"},
            ]
        },
        {
            "id": "s2", "name": "Semester 2",
            "courses": [
                {"id":"c8",  "code":"AE 152",  "name":"Introduction to Aerospace Engg.",                "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c9",  "code":"CS 101",  "name":"Computer Programming and Utilization",           "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c10", "code":"ENT101",  "name":"Introduction to Innovation & Entrepreneurship",  "tag":"C", "newTag":"C", "credits":4, "grade":"AA"},
                {"id":"c11", "code":"HS 110",  "name":"Introduction to Psychology",                     "tag":"C", "newTag":"C", "credits":4, "grade":"AA"},
                {"id":"c12", "code":"MA 110",  "name":"Linear Algebra & Differential Equations",        "tag":"C", "newTag":"C", "credits":8, "grade":"AA"},
                {"id":"c13", "code":"NOCS02",  "name":"NCC/NSS/NSO",                                    "tag":"N", "newTag":"N", "credits":0, "grade":"PP"},
                {"id":"c14", "code":"PH 117",  "name":"Physics Lab",                                    "tag":"C", "newTag":"C", "credits":3, "grade":"AA"},
                {"id":"c15", "code":"TA 101",  "name":"Teaching Assistant Skill Enhancement (TASET)",   "tag":"N", "newTag":"N", "credits":0, "grade":"PP"},
            ]
        },
        {
            "id": "s3", "name": "Semester 3",
            "courses": [
                {"id":"c16", "code":"AE 223",  "name":"Thermodynamics and Propulsion",                  "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c17", "code":"AE 227",  "name":"Solid Mechanics",                                "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c18", "code":"AE 229",  "name":"Intro to Aerodynamics & Propulsion Lab",         "tag":"C", "newTag":"C", "credits":3, "grade":"AA"},
                {"id":"c19", "code":"AE 231",  "name":"Intro to Aerospace Structures & Control Lab",    "tag":"C", "newTag":"C", "credits":3, "grade":"AA"},
                {"id":"c20", "code":"AE 308",  "name":"Control Theory",                                 "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c22", "code":"EC 101",  "name":"Economics",                                      "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c23", "code":"ES250 & HS250",  "name":"Environmental Studies",                   "tag":"C", "newTag":"C", "credits":6, "grade":"PP"},
            ]
        },
        {
            "id": "s4", "name": "Semester 4",
            "courses": [
                {"id":"c27", "code":"AE 233",  "name":"Control Systems Laboratory",                     "tag":"C", "newTag":"C", "credits":3, "grade":"AA"},
                {"id":"c28", "code":"AE 238",  "name":"Aerospace Structural Mechanics",                 "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c29", "code":"AE 244",  "name":"Low Speed Aerodynamics",                         "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c30", "code":"AE 246",  "name":"Aircraft Structures Laboratory",                 "tag":"C", "newTag":"C", "credits":3, "grade":"AA"},
                {"id":"c31", "code":"AE 248",  "name":"AI and Data Science",                            "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c33", "code":"DE 250",  "name":"Design Thinking for Innovation",                 "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c34", "code":"PH 111",  "name":"Introduction to Classical Physics",              "tag":"C", "newTag":"C", "credits":4, "grade":"AA"},
            ]
        },
        {
            "id": "s5", "name": "Semester 5",
            "courses": [
                {"id":"c38", "code":"AE 339",  "name":"High Speed Aerodynamics",                        "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c39", "code":"AE 341",  "name":"Flight Mechanics of Aircrafts and Spacecrafts",  "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c40", "code":"AE 343",  "name":"Aerodynamics Laboratory",                        "tag":"C", "newTag":"C", "credits":3, "grade":"AA"},
                {"id":"c41", "code":"AE 344",  "name":"Aero Propulsion",                                "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c42", "code":"AE 345",  "name":"Aircraft Propulsion Laboratory",                 "tag":"C", "newTag":"C", "credits":3, "grade":"AA"},
            ]
        },
        {
            "id": "s6", "name": "Semester 6",
            "courses": [
            ]
        },
        {
            "id": "s7", "name": "Semester 7",
            "courses": [
            ]
        },
        {
            "id": "s8", "name": "Semester 8",
            "courses": [
            ]
        },
    ]
}

# ── Embedded HTML page ────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RetagHelper — IIT Bombay</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:ital,wght@0,400;0,500;1,400&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0d1117;--bg2:#131920;--bg3:#1a2230;
  --border:rgba(255,255,255,0.08);--border2:rgba(255,255,255,0.13);
  --text:#e8edf2;--muted:#8a9bae;
  --blue:#3b82f6;--green:#3ecf8e;--red:#e05260;--amber:#f0913a;--purple:#8b5cf6;
}
body{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;min-height:100vh}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.12);border-radius:3px}

/* ── TOPBAR ── */
#topbar{
  position:sticky;top:0;z-index:200;
  background:rgba(13,17,23,0.93);backdrop-filter:blur(16px);
  border-bottom:1px solid var(--border);padding:0 22px;
}
#topbar-main{display:flex;align-items:center;justify-content:space-between;height:56px;gap:12px}
#logo{display:flex;align-items:center;gap:10px;flex-shrink:0}
#logo .icon{
  width:30px;height:30px;border-radius:7px;
  background:linear-gradient(135deg,var(--blue),var(--purple));
  display:flex;align-items:center;justify-content:center;
  font-weight:900;font-size:15px;font-family:'Syne',sans-serif;
}
#logo .title{font-family:'Syne',sans-serif;font-weight:800;font-size:16px;letter-spacing:-.02em}
#logo .badge{font-size:10px;color:var(--muted);background:rgba(255,255,255,0.06);border-radius:20px;padding:2px 9px;font-weight:600}

.score-cards{display:flex;gap:7px;align-items:center;flex-shrink:0}
.score-card{background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:9px;padding:5px 13px;min-width:105px}
.score-card .sc-label{font-size:9px;color:var(--muted);font-weight:700;letter-spacing:.09em;text-transform:uppercase;margin-bottom:2px}
.score-card .sc-val{display:flex;align-items:baseline;gap:5px}
.score-card .sc-num{font-size:18px;font-weight:800;font-variant-numeric:tabular-nums;font-family:'DM Mono',monospace}
.score-card .sc-delta{font-size:10px;font-weight:700}
.score-card .sc-was{font-size:9px;color:var(--muted);margin-top:1px}

.toolbar{display:flex;gap:7px;align-items:center;flex-shrink:0}
.tb-btn{
  display:flex;align-items:center;gap:5px;
  padding:7px 13px;border-radius:8px;border:1px solid var(--border2);
  font-size:12px;font-weight:600;font-family:inherit;cursor:pointer;
  transition:background .15s,border-color .15s;white-space:nowrap;
}
.tb-btn:hover{border-color:rgba(255,255,255,0.25)}
.tb-btn.primary{background:var(--blue);border-color:var(--blue);color:#fff}
.tb-btn.primary:hover{background:#2563eb}
.tb-btn.secondary{background:rgba(255,255,255,0.05);color:var(--text)}
.tb-btn.secondary:hover{background:rgba(255,255,255,0.09)}
.tb-btn.summary-btn{background:rgba(139,92,246,0.1);border-color:rgba(139,92,246,0.35);color:#a78bfa}
.tb-btn.summary-btn:hover{background:rgba(139,92,246,0.18)}
#file-input{display:none}

/* Credit strip */
#credit-strip{
  display:flex;flex-wrap:wrap;gap:5px;align-items:center;
  padding:6px 0 8px;border-top:1px solid rgba(255,255,255,0.05);
}
.cstrip-total{
  display:flex;align-items:center;gap:5px;
  background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);
  border-radius:6px;padding:3px 10px;font-size:11.5px;font-weight:700;color:#93c5fd;
  margin-right:4px;
}
.cstrip-item{
  display:flex;align-items:center;gap:4px;
  background:rgba(255,255,255,0.03);border:1px solid var(--border);
  border-radius:6px;padding:3px 9px;font-size:11px;
}
.cstrip-badge{display:inline-block;padding:1px 6px;border-radius:3px;font-size:10px;font-weight:700;letter-spacing:.04em}
.cstrip-cr{font-weight:700;font-variant-numeric:tabular-nums;color:var(--text)}
.cstrip-lbl{color:var(--muted)}

/* ── MAIN ── */
#main{max-width:1160px;margin:0 auto;padding:20px 18px 60px}
#legend{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px}
.leg{display:flex;align-items:center;gap:4px;font-size:11px;color:var(--muted)}
.lbadge{display:inline-block;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:700;letter-spacing:.04em}
.cpi-dot{color:var(--green);font-size:10px}
#spi-row{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:18px}
.infobar{
  background:rgba(59,130,246,0.07);border:1px solid rgba(59,130,246,0.22);
  border-radius:9px;padding:9px 14px;margin-bottom:16px;
  font-size:11.5px;color:#93c5fd;line-height:1.6;
}

/* ── SEMESTER BLOCK ── */
.sem-block{
  background:rgba(255,255,255,0.025);border:1px solid var(--border);
  border-radius:13px;overflow:hidden;margin-bottom:11px;transition:border-color .2s;
}
.sem-block:hover{border-color:rgba(255,255,255,0.13)}
.sem-header{
  display:flex;align-items:center;justify-content:space-between;
  padding:10px 17px;cursor:pointer;
  background:rgba(59,130,246,0.05);border-bottom:1px solid var(--border);user-select:none;
}
.sem-header .sh-left{display:flex;align-items:center;gap:9px}
.sem-header .sh-title{font-family:'Syne',sans-serif;font-weight:800;font-size:13.5px}
.sem-header .sh-meta{font-size:11px;color:var(--muted)}
.sh-warn{font-size:10px;color:var(--amber);background:rgba(240,145,58,0.12);border:1px solid rgba(240,145,58,0.35);border-radius:4px;padding:2px 7px;font-weight:700}
.sem-header .sh-right{display:flex;align-items:center;gap:11px}
.sem-spi .spi-label{font-size:9px;color:var(--muted);font-weight:700;letter-spacing:.08em}
.sem-spi .spi-val{display:flex;align-items:baseline;gap:4px}
.sem-spi .spi-num{font-size:14px;font-weight:800;font-variant-numeric:tabular-nums;font-family:'DM Mono',monospace}
.sem-spi .spi-delta{font-size:10px;font-weight:700}
.toggle-arrow{color:var(--muted);font-size:14px;transition:transform .2s}

/* Table */
.tbl-header{
  display:grid;grid-template-columns:84px 1fr 74px 68px 84px 98px 30px;
  gap:5px;padding:6px 17px;
  font-size:9.5px;color:var(--muted);font-weight:700;letter-spacing:.09em;
  border-bottom:1px solid rgba(255,255,255,0.05);
}
.course-row{
  display:grid;grid-template-columns:84px 1fr 74px 68px 84px 98px 30px;
  gap:5px;padding:5px 17px;align-items:center;
  border-bottom:1px solid rgba(255,255,255,0.04);transition:background .15s;
}
.course-row:hover{background:rgba(255,255,255,0.02)}
.course-row.changed{background:rgba(59,130,246,0.045)}
.c-code{font-family:'DM Mono',monospace;font-size:11px;color:#a0b4c8;font-weight:500}
.c-name{font-size:12px;color:#c8d5e0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
input.num-input,select.sel{
  background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);
  border-radius:6px;padding:5px 7px;color:var(--text);font-size:12.5px;
  outline:none;width:100%;font-family:inherit;transition:border-color .15s;
}
input.num-input:focus,select.sel:focus{border-color:var(--blue)}
select.sel{background:#131920;cursor:pointer}
select.sel:disabled{opacity:.45;cursor:not-allowed}
select.sel.changed{background:rgba(59,130,246,0.14);border-color:var(--blue);color:#93c5fd;font-weight:700}
.tag-badge{display:inline-block;padding:3px 8px;border-radius:4px;font-size:10.5px;font-weight:700;letter-spacing:.04em;white-space:nowrap}
.new-tag-wrap{position:relative}
.effect-dot{
  position:absolute;top:-5px;right:-5px;
  width:14px;height:14px;border-radius:50%;
  font-size:10px;font-weight:900;display:flex;align-items:center;justify-content:center;
  color:#fff;pointer-events:none;
}
.del-btn{background:transparent;border:none;color:rgba(224,82,96,0.4);cursor:pointer;font-size:16px;padding:3px 5px;border-radius:5px;transition:color .15s,background .15s;line-height:1}
.del-btn:hover{color:var(--red);background:rgba(224,82,96,0.1)}
.add-course-btn{
  display:flex;align-items:center;gap:6px;
  background:rgba(59,130,246,0.07);border:1px dashed rgba(59,130,246,0.38);
  border-radius:7px;padding:6px 13px;margin:7px 17px 9px;
  color:var(--blue);cursor:pointer;font-weight:600;font-size:12.5px;
  font-family:inherit;transition:background .15s;
}
.add-course-btn:hover{background:rgba(59,130,246,0.13)}

/* Add semester */
#add-sem-area{margin-top:7px}
.add-sem-btn{
  display:flex;align-items:center;justify-content:center;gap:7px;
  background:rgba(255,255,255,0.03);border:1px dashed rgba(255,255,255,0.16);
  border-radius:11px;padding:11px 20px;color:var(--muted);
  cursor:pointer;font-weight:600;font-size:13px;width:100%;
  font-family:inherit;transition:background .15s;
}
.add-sem-btn:hover{background:rgba(255,255,255,0.06)}
.add-sem-row{display:flex;gap:9px;align-items:center}
.add-sem-row input{
  flex:1;background:rgba(255,255,255,0.06);border:1px solid var(--border2);
  border-radius:8px;padding:8px 13px;color:var(--text);font-size:13.5px;
  outline:none;font-family:inherit;
}
.add-sem-row input:focus{border-color:var(--blue)}
.btn-primary{padding:8px 18px;border-radius:8px;background:var(--blue);border:none;color:#fff;cursor:pointer;font-weight:700;font-size:13px;font-family:inherit;transition:background .15s}
.btn-primary:hover{background:#2563eb}
.btn-ghost{padding:8px 14px;border-radius:8px;background:transparent;border:1px solid var(--border2);color:var(--muted);cursor:pointer;font-family:inherit;transition:background .15s}
.btn-ghost:hover{background:rgba(255,255,255,0.06)}

/* ── MODAL ── */
.modal-overlay{
  position:fixed;inset:0;background:rgba(0,0,0,0.76);
  backdrop-filter:blur(9px);display:flex;align-items:center;justify-content:center;z-index:999;
}
.modal{
  background:#1a2230;border:1px solid rgba(255,255,255,0.12);
  border-radius:15px;padding:26px;width:460px;max-width:96vw;
  max-height:92vh;overflow-y:auto;
}
.modal h3{font-family:'Syne',sans-serif;font-weight:700;font-size:17px;margin-bottom:18px}
.field{display:flex;flex-direction:column;gap:4px}
.field label{font-size:10.5px;color:var(--muted);font-weight:700;letter-spacing:.08em}
.field input,.field select{
  background:rgba(255,255,255,0.06);border:1px solid var(--border2);
  border-radius:7px;padding:8px 11px;color:var(--text);font-size:13.5px;
  outline:none;font-family:inherit;
}
.field input:focus,.field select:focus{border-color:var(--blue)}
.field select{background:#1a2230}
.modal-fields{display:flex;flex-direction:column;gap:13px}
.modal-3col{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
.modal-footer{display:flex;gap:9px;justify-content:flex-end;margin-top:20px}

/* ── SUMMARY MODAL ── */
.summary-modal-inner{width:580px}
.summary-section{margin-bottom:20px}
.summary-section h4{
  font-size:11px;font-weight:700;color:var(--muted);letter-spacing:.09em;
  text-transform:uppercase;margin-bottom:10px;padding-bottom:6px;
  border-bottom:1px solid var(--border);
}
.cpi-summary-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:2px}
.cpi-box{background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:9px;padding:12px 15px}
.cpi-box .cb-label{font-size:10px;color:var(--muted);font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin-bottom:4px}
.cpi-box .cb-val{font-size:23px;font-weight:800;font-family:'DM Mono',monospace}
.cpi-box .cb-sub{font-size:11px;color:var(--muted);margin-top:3px;line-height:1.5}
.tag-summary-row{
  display:flex;justify-content:space-between;align-items:center;
  padding:5px 0;font-size:12.5px;border-bottom:1px solid rgba(255,255,255,0.04);
}
.tag-summary-row:last-child{border-bottom:none}
.tsr-label{display:flex;align-items:center;gap:6px}
.tsr-cr{font-weight:700;font-variant-numeric:tabular-nums}
.summary-row{
  display:grid;grid-template-columns:78px 1fr auto auto;
  gap:8px;align-items:center;padding:6px 0;
  border-bottom:1px solid rgba(255,255,255,0.04);font-size:12px;
}
.summary-row:last-child{border-bottom:none}
.sr-code{font-family:'DM Mono',monospace;color:#a0b4c8;font-size:10.5px}
.sr-name{color:#c8d5e0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sr-cr{font-size:11px;color:var(--muted);white-space:nowrap}
.no-retag{color:var(--muted);font-size:13px;text-align:center;padding:14px 0}
.sem-group-label{font-size:10.5px;color:var(--muted);font-weight:700;letter-spacing:.06em;margin:10px 0 5px}

/* Toast */
#toast{
  position:fixed;bottom:22px;right:22px;z-index:9999;
  background:#1a2230;border:1px solid var(--green);border-radius:10px;
  padding:11px 18px;font-size:13px;color:var(--green);font-weight:600;
  box-shadow:0 4px 24px rgba(0,0,0,0.4);
  transform:translateY(70px);opacity:0;transition:all .3s ease;pointer-events:none;
}
#toast.show{transform:translateY(0);opacity:1}
#toast.error{border-color:var(--red);color:var(--red)}

.sem-body.collapsed{display:none}
.footer{margin-top:30px;text-align:center;font-size:11px;color:#526070;line-height:1.8}
</style>
</head>
<body>

<!-- Topbar -->
<div id="topbar">
  <div id="topbar-main">
    <div id="logo">
      <div class="icon">R</div>
      <span class="title">RetagHelper</span>
      <span class="badge">IIT Bombay · v2</span>
    </div>

    <div class="score-cards">
      <div class="score-card" style="min-width:150px">
        <div class="sc-label">Total CPI Credits</div>
        <div class="sc-val">
          <span class="sc-num" id="sc-orig-cr" style="font-size:17px">—</span>
          <span class="sc-delta" id="sc-cr-delta"></span>
        </div>
        <div class="sc-was" id="sc-cr-was"></div>
      </div>
      <div class="score-card">
        <div class="sc-label">CPI</div>
        <div class="sc-val"><span class="sc-num" id="sc-cpi-num">—</span><span class="sc-delta" id="sc-cpi-delta"></span></div>
        <div class="sc-was" id="sc-cpi-was"></div>
      </div>
      <div class="score-card">
        <div class="sc-label">GPA / 4</div>
        <div class="sc-val"><span class="sc-num" id="sc-gpa-num">—</span><span class="sc-delta" id="sc-gpa-delta"></span></div>
        <div class="sc-was" id="sc-gpa-was"></div>
      </div>
    </div>

    <div class="toolbar">
      <button class="tb-btn summary-btn" onclick="openSummary()">📊 Summary</button>
      <button class="tb-btn secondary"   onclick="saveState()">💾 Save</button>
      <button class="tb-btn secondary"   onclick="document.getElementById('file-input').click()">📂 Load</button>
      <input type="file" id="file-input" accept=".json" onchange="loadState(event)">
    </div>
  </div>
  <div id="credit-strip"></div>
</div>

<!-- Main content -->
<div id="main">
  <div id="legend"></div>
  <div id="spi-row"></div>
  <div class="infobar">
    ℹ&nbsp; Change <strong>New Tag</strong> to simulate retagging — CPI updates instantly.
    Tags that count toward CPI: <strong>Core (C), Dept Elective (D), STEM (SE), HASMED (HE)</strong>. Check your curriculum for minimum credit requirements per tag (Ex: in aerospace, DE=36, SE=12, HE=12, FE=36). Flexible electives(Institute electives) can be any course from DE/SE/HE categories above the minimums, thus that tag is not explicitly tracked.
    Min <strong>18 credits/sem</strong> required. Retagging allowed <strong>twice</strong> per program (pre-placement & post-curriculum).
    &nbsp;|&nbsp; <strong>💾 Save</strong> exports your state as a JSON file &nbsp;·&nbsp; <strong>📂 Load</strong> restores a saved file &nbsp;·&nbsp; <strong>📊 Summary</strong> shows the full retag report.
  </div>
  <div id="sem-container"></div>
  <div id="add-sem-area">
    <button class="add-sem-btn" onclick="showAddSem()"><span style="font-size:17px">+</span> Add Semester</button>
    <div class="add-sem-row" id="add-sem-row" style="display:none">
      <input id="new-sem-name" placeholder="e.g. Semester 9" onkeydown="if(event.key==='Enter')addSemester()">
      <button class="btn-primary" onclick="addSemester()">Add</button>
      <button class="btn-ghost"   onclick="hideAddSem()">Cancel</button>
    </div>
  </div>
  <div class="footer">
    Tag rules per IIT Bombay UG Rulebook 2025-26 &nbsp;·&nbsp;
    Retagging: twice in program (pre-placements & post-curriculum) &nbsp;·&nbsp;
    Blue rows = CPI-affecting changes &nbsp;·&nbsp;
    💾 Save / 📂 Load to persist across sessions
  </div>
</div>

<!-- Add Course Modal -->
<div class="modal-overlay" id="add-modal" style="display:none" onclick="if(event.target===this)closeModal('add-modal')">
  <div class="modal">
    <h3>Add Course</h3>
    <div class="modal-fields">
      <div class="field"><label>COURSE CODE</label><input id="m-code" placeholder="e.g. AE 301"></div>
      <div class="field"><label>COURSE NAME</label><input id="m-name" placeholder="e.g. Advanced Aerodynamics"></div>
      <div class="modal-3col">
        <div class="field"><label>TAG</label><select id="m-tag"></select></div>
        <div class="field"><label>CREDITS</label><input id="m-credits" type="number" min="0" max="48" value="6"></div>
        <div class="field">
          <label>GRADE</label>
          <select id="m-grade">
            <option>AA</option><option>AB</option><option selected>BB</option>
            <option>BC</option><option>CC</option><option>CD</option><option>DD</option>
            <option>FF</option><option value="PP">PP</option>
          </select>
        </div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn-ghost"   onclick="closeModal('add-modal')">Cancel</button>
      <button class="btn-primary" onclick="submitAddCourse()">Add Course</button>
    </div>
  </div>
</div>

<!-- Summary Modal -->
<div class="modal-overlay" id="summary-modal" style="display:none" onclick="if(event.target===this)closeModal('summary-modal')">
  <div class="modal summary-modal-inner">
    <h3>📊 Retag Summary</h3>
    <div id="summary-body"></div>
    <div class="modal-footer">
      <button class="btn-ghost"   onclick="closeModal('summary-modal')">Close</button>
      <button class="btn-primary" onclick="saveState()">💾 Save State</button>
    </div>
  </div>
</div>

<!-- Toast notification -->
<div id="toast">✓ Done!</div>

<script>
// ── Tag definitions ───────────────────────────────────────────────────────────
const TAG_META = {
  C:  {label:"Core Course",               short:"Core",   color:"#e05260", counts:true },
  D:  {label:"Department Elective",       short:"Dept E", color:"#f07d3a", counts:true },
  SE: {label:"STEM Elective",             short:"STEM",   color:"#4ca4e0", counts:true },
  HE: {label:"HASMED Elective",           short:"HSMD",   color:"#9b63d8", counts:true },
  M:  {label:"Minor Course",              short:"Minor",  color:"#2db58e", counts:false},
  T:  {label:"Additional Learning (ALC)", short:"ALC",    color:"#8a9bae", counts:false},
  O:  {label:"Honors Course",             short:"Honors", color:"#c9a227", counts:false},
  E:  {label:"Honors Elective",           short:"Hon. E", color:"#b08040", counts:false},
  N:  {label:"Non-credit",               short:"N/A",    color:"#555555", counts:false},
};
const TAG_TRANSITIONS = {
  T:["D","SE","HE","O","E","M"], C:[], D:["T","O","E"],
  SE:["T"], HE:["T"], O:["T","D","E"], E:["T","D","O"], M:["T","SE","HE"], N:[],
};
const GRADE_POINTS = {AA:10,AB:9,BB:8,BC:7,CC:6,CD:5,DD:4,FF:0,FR:0};

// ── State ─────────────────────────────────────────────────────────────────────
let data = __INITIAL_DATA__;
let _uid = 300;
const uid = () => `u${++_uid}`;
let collapsedSems = {};
let modalTargetSemId = null;

// ── Calculations ──────────────────────────────────────────────────────────────
function calcSPI(courses, useNew) {
  let ws=0,tc=0;
  for (const c of courses) {
    const tag = useNew ? c.newTag : c.tag;
    if (!TAG_META[tag]?.counts) continue;
    const gp = GRADE_POINTS[c.grade];
    if (gp===undefined) continue;
    ws += gp*c.credits; tc += c.credits;
  }
  return tc>0 ? ws/tc : null;
}
function calcCPI(useNew) {
  let ws=0,tc=0;
  for (const sem of data.semesters)
    for (const c of sem.courses) {
      const tag = useNew ? c.newTag : c.tag;
      if (!TAG_META[tag]?.counts) continue;
      const gp = GRADE_POINTS[c.grade];
      if (gp===undefined) continue;
      ws += gp*c.credits; tc += c.credits;
    }
  return tc>0 ? {val:ws/tc, credits:tc} : null;
}
function tagCredits(useNew) {
  const r={};
  for (const sem of data.semesters)
    for (const c of sem.courses) {
      const tag = useNew ? c.newTag : c.tag;
      if (!TAG_META[tag]?.counts) continue;
      if (GRADE_POINTS[c.grade]===undefined) continue;
      r[tag] = (r[tag]||0) + c.credits;
    }
  return r;
}
function semTotalCredits(courses) { return courses.reduce((s,c)=>s+(c.credits||0),0); }
function getRetagged() {
  const list=[];
  for (const sem of data.semesters)
    for (const c of sem.courses)
      if (c.newTag !== c.tag)
        list.push({sem:sem.name,code:c.code,name:c.name,from:c.tag,to:c.newTag,credits:c.credits,grade:c.grade});
  return list;
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function tagBadge(tag) {
  const m = TAG_META[tag]||{short:tag,color:"#666"};
  return `<span class="tag-badge" style="background:${m.color}22;color:${m.color};border:1px solid ${m.color}44">${m.short}</span>`;
}
let toastTimer;
function showToast(msg, isError=false) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.className = isError ? "error show" : "show";
  clearTimeout(toastTimer);
  toastTimer = setTimeout(()=>t.className="", 3000);
}

// ── Credit strip (under topbar) ───────────────────────────────────────────────
function renderCreditStrip() {
  const origTags = tagCredits(false);
  const newTags  = tagCredits(true);
  const origTotal = Object.values(origTags).reduce((a,b)=>a+b,0);
  const newTotal  = Object.values(newTags).reduce((a,b)=>a+b,0);
  const crDiff    = newTotal - origTotal;
  const allTags   = [...new Set([...Object.keys(origTags),...Object.keys(newTags)])];

  const totalHtml = `<div class="cstrip-total">
    Total: <strong>${newTotal}</strong> CPI credits
    ${crDiff!==0?`<span style="font-size:10px;font-weight:700;color:${crDiff>0?"var(--green)":"var(--red)"}">${crDiff>0?"+":""}${crDiff}</span>`:""}
  </div>`;

  const items = allTags.map(tag => {
    const m   = TAG_META[tag]; if (!m) return "";
    const o   = origTags[tag]||0;
    const n   = newTags[tag]||0;
    const d   = n - o;
    return `<div class="cstrip-item">
      <span class="cstrip-badge" style="background:${m.color}22;color:${m.color};border:1px solid ${m.color}44">${m.short}</span>
      <span class="cstrip-cr">${n}</span>
      ${d!==0?`<span style="font-size:10px;color:${d>0?"var(--green)":"var(--red)"};font-weight:700">${d>0?"+":""}${d}</span>`:""}
      <span class="cstrip-lbl">cr</span>
    </div>`;
  });
  document.getElementById("credit-strip").innerHTML = totalHtml + items.join("");
}

// ── Topbar scores ─────────────────────────────────────────────────────────────
function updateTopbar() {
  const origR = calcCPI(false), newR = calcCPI(true);
  const origCPI = origR?.val??null, newCPI = newR?.val??null;
  const origCr  = origR?.credits??0, newCr = newR?.credits??0;

  // Credits card
  document.getElementById("sc-orig-cr").textContent = newCr;
  const crDiff = newCr - origCr;
  document.getElementById("sc-cr-delta").textContent =
    crDiff!==0 ? (crDiff>0?"▲ ":"▼ ")+Math.abs(crDiff) : "";
  document.getElementById("sc-cr-delta").style.color =
    crDiff>0?"var(--green)":crDiff<0?"var(--red)":"";
  document.getElementById("sc-cr-was").textContent =
    crDiff!==0 ? `was ${origCr}` : "no credit changes";

  // CPI card
  const setCard = (numId,deltaId,wasId,orig,upd) => {
    document.getElementById(numId).textContent = upd!==null ? upd.toFixed(3) : "—";
    if (orig!==null && upd!==null) {
      const d = upd-orig;
      if (Math.abs(d)>0.0001) {
        document.getElementById(deltaId).textContent = (d>0?"▲ ":"▼ ")+Math.abs(d).toFixed(3);
        document.getElementById(deltaId).style.color = d>0?"var(--green)":"var(--red)";
        document.getElementById(wasId).textContent = `was ${orig.toFixed(3)}`;
      } else {
        document.getElementById(deltaId).textContent="";
        document.getElementById(wasId).textContent="";
      }
    }
  };
  setCard("sc-cpi-num","sc-cpi-delta","sc-cpi-was",origCPI,newCPI);
  setCard("sc-gpa-num","sc-gpa-delta","sc-gpa-was",
    origCPI!==null?origCPI*0.4:null, newCPI!==null?newCPI*0.4:null);

  renderCreditStrip();
}

// ── Legend ────────────────────────────────────────────────────────────────────
function renderLegend() {
  document.getElementById("legend").innerHTML =
    Object.entries(TAG_META).map(([k,v])=>
      `<div class="leg">
        <span class="lbadge" style="background:${v.color}22;color:${v.color};border:1px solid ${v.color}44">${v.short}</span>
        <span>${v.label}</span>
        ${v.counts?'<span class="cpi-dot">⟵ CPI</span>':""}
      </div>`
    ).join("");
}

// ── SPI row ───────────────────────────────────────────────────────────────────
function renderSPIRow() {
  document.getElementById("spi-row").innerHTML = data.semesters.map((sem,i)=>{
    const orig=calcSPI(sem.courses,false), upd=calcSPI(sem.courses,true);
    const diff=(orig!==null&&upd!==null)?upd-orig:null;
    const ch=diff!==null&&Math.abs(diff)>0.0001;
    return `<div class="score-card">
      <div class="sc-label">Sem ${i+1} SPI</div>
      <div class="sc-val">
        <span class="sc-num" style="font-size:15px">${upd!==null?upd.toFixed(2):"—"}</span>
        ${ch?`<span class="sc-delta" style="color:${diff>0?"var(--green)":"var(--red)"}">${diff>0?"▲":"▼"} ${Math.abs(diff).toFixed(3)}</span>`:""}
      </div>
      ${ch&&orig!==null?`<div class="sc-was">was ${orig.toFixed(2)}</div>`:""}
    </div>`;
  }).join("");
}

// ── Semester blocks ───────────────────────────────────────────────────────────
function renderSemesterContainer() {
  document.getElementById("sem-container").innerHTML =
    data.semesters.map((sem,i)=>renderSemBlock(sem,i)).join("");
}
function renderSemBlock(sem,idx) {
  const orig=calcSPI(sem.courses,false), upd=calcSPI(sem.courses,true);
  const diff=(orig!==null&&upd!==null)?upd-orig:null;
  const ch=diff!==null&&Math.abs(diff)>0.0001;
  const totalCr=semTotalCredits(sem.courses);
  const belowMin=totalCr>0&&totalCr<18;
  const collapsed=collapsedSems[sem.id];
  return `
  <div class="sem-block" id="semblock-${sem.id}">
    <div class="sem-header" onclick="toggleSem('${sem.id}')">
      <div class="sh-left">
        <span class="sh-title">${sem.name}</span>
        <span class="sh-meta">${sem.courses.length} courses · ${totalCr} cr</span>
        ${belowMin?'<span class="sh-warn">⚠ Below 18 cr</span>':""}
      </div>
      <div class="sh-right">
        ${orig!==null?`<div class="sem-spi">
          <div class="spi-label">SPI</div>
          <div class="spi-val">
            <span class="spi-num">${(upd??orig).toFixed(2)}</span>
            ${ch?`<span class="spi-delta" style="color:${diff>0?"var(--green)":"var(--red)"}">${diff>0?"▲":"▼"} ${Math.abs(diff).toFixed(3)}</span>`:""}
          </div>
        </div>`:""}
        <span class="toggle-arrow" style="transform:rotate(${collapsed?"-90deg":"0deg"})">▾</span>
      </div>
    </div>
    <div class="sem-body${collapsed?" collapsed":""}">
      <div class="tbl-header">
        <span>CODE</span><span>COURSE NAME</span><span>CREDITS</span>
        <span>GRADE</span><span>ORIG TAG</span><span>NEW TAG</span><span></span>
      </div>
      ${sem.courses.map(c=>renderCourseRow(c,sem.id)).join("")}
      <button class="add-course-btn" onclick="openAddModal('${sem.id}')">
        <span style="font-size:15px;line-height:1">+</span> Add Course
      </button>
    </div>
  </div>`;
}
function renderCourseRow(c,semId) {
  const allowed=TAG_TRANSITIONS[c.tag]??[];
  const allOpts=[c.tag,...allowed];
  const isChanged=c.newTag!==c.tag;
  const origCounts=TAG_META[c.tag]?.counts;
  const newCounts=TAG_META[c.newTag]?.counts;
  const effectChanged=origCounts!==newCounts;
  const gradeOpts=["AA","AB","BB","BC","CC","CD","DD","FF","PP"].map(g=>
    `<option value="${g}"${c.grade===g?" selected":""}>${g}</option>`).join("");
  const newTagOpts=allOpts.map(t=>
    `<option value="${t}"${c.newTag===t?" selected":""}>${TAG_META[t]?.short??t}</option>`).join("");
  return `
  <div class="course-row${isChanged?" changed":""}" id="row-${c.id}">
    <span class="c-code">${c.code}</span>
    <span class="c-name" title="${c.name}">${c.name}</span>
    <input class="num-input" type="number" min="0" max="48" value="${c.credits}"
      onchange="updateCourse('${semId}','${c.id}','credits',+this.value)">
    <select class="sel" onchange="updateCourse('${semId}','${c.id}','grade',this.value)">${gradeOpts}</select>
    ${tagBadge(c.tag)}
    <div class="new-tag-wrap">
      <select class="sel${isChanged?" changed":""}" ${allOpts.length<=1?"disabled":""}
        onchange="updateCourse('${semId}','${c.id}','newTag',this.value)">${newTagOpts}</select>
      ${effectChanged?`<span class="effect-dot" style="background:${newCounts?"var(--green)":"var(--red)"}"
        title="${newCounts?"Now counts toward CPI":"No longer counts toward CPI"}">${newCounts?"+":"−"}</span>`:""}
    </div>
    <button class="del-btn" onclick="deleteCourse('${semId}','${c.id}')" title="Remove">×</button>
  </div>`;
}

// ── Full render ───────────────────────────────────────────────────────────────
function renderAll() {
  renderLegend();
  renderSemesterContainer();
  renderSPIRow();
  updateTopbar();
}

// ── Event handlers ────────────────────────────────────────────────────────────
function toggleSem(semId) {
  collapsedSems[semId]=!collapsedSems[semId];
  renderSemesterContainer();
}
function updateCourse(semId,courseId,field,val) {
  const sem=data.semesters.find(s=>s.id===semId); if(!sem)return;
  const c=sem.courses.find(x=>x.id===courseId);   if(!c)return;
  c[field]=val;
  if(field==="tag") c.newTag=val;
  const semIdx=data.semesters.findIndex(s=>s.id===semId);
  const el=document.getElementById(`semblock-${semId}`);
  if(el) el.outerHTML=renderSemBlock(data.semesters[semIdx],semIdx);
  renderSPIRow(); updateTopbar();
}
function deleteCourse(semId,courseId) {
  const sem=data.semesters.find(s=>s.id===semId); if(!sem)return;
  sem.courses=sem.courses.filter(c=>c.id!==courseId);
  const semIdx=data.semesters.findIndex(s=>s.id===semId);
  const el=document.getElementById(`semblock-${semId}`);
  if(el) el.outerHTML=renderSemBlock(data.semesters[semIdx],semIdx);
  renderSPIRow(); updateTopbar();
}

// ── Add Course Modal ──────────────────────────────────────────────────────────
function openAddModal(semId) {
  modalTargetSemId=semId;
  document.getElementById("m-tag").innerHTML=Object.entries(TAG_META).map(([k,v])=>
    `<option value="${k}">${v.short} — ${v.label}</option>`).join("");
  document.getElementById("m-code").value="";
  document.getElementById("m-name").value="";
  document.getElementById("m-credits").value=6;
  document.getElementById("add-modal").style.display="flex";
}
function closeModal(id) { document.getElementById(id).style.display="none"; }
function submitAddCourse() {
  const code=document.getElementById("m-code").value.trim();
  const name=document.getElementById("m-name").value.trim();
  const tag=document.getElementById("m-tag").value;
  const credits=+document.getElementById("m-credits").value;
  const grade=document.getElementById("m-grade").value;
  if(!code||!name){alert("Please fill in Code and Name.");return;}
  const sem=data.semesters.find(s=>s.id===modalTargetSemId); if(!sem)return;
  sem.courses.push({id:uid(),code,name,tag,newTag:tag,credits,grade});
  closeModal("add-modal");
  const semIdx=data.semesters.findIndex(s=>s.id===modalTargetSemId);
  const el=document.getElementById(`semblock-${modalTargetSemId}`);
  if(el) el.outerHTML=renderSemBlock(data.semesters[semIdx],semIdx);
  renderSPIRow(); updateTopbar();
}

// ── Add Semester ──────────────────────────────────────────────────────────────
function showAddSem() {
  document.querySelector(".add-sem-btn").style.display="none";
  document.getElementById("add-sem-row").style.display="flex";
  document.getElementById("new-sem-name").focus();
}
function hideAddSem() {
  document.querySelector(".add-sem-btn").style.display="flex";
  document.getElementById("add-sem-row").style.display="none";
}
function addSemester() {
  const name=document.getElementById("new-sem-name").value.trim(); if(!name)return;
  data.semesters.push({id:uid(),name,courses:[]});
  hideAddSem();
  document.getElementById("new-sem-name").value="";
  renderSemesterContainer(); renderSPIRow();
}

// ── Save / Load ───────────────────────────────────────────────────────────────
function saveState() {
  const payload=JSON.stringify({version:2,savedAt:new Date().toISOString(),data},null,2);
  const blob=new Blob([payload],{type:"application/json"});
  const url=URL.createObjectURL(blob);
  const a=document.createElement("a");
  a.href=url;
  a.download=`retag_helper_${new Date().toISOString().replace(/[:.]/g,"-").slice(0,19)}.json`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("✓ State saved — check your Downloads folder!");
}
function loadState(event) {
  const file=event.target.files[0]; if(!file)return;
  const reader=new FileReader();
  reader.onload=e=>{
    try {
      const parsed=JSON.parse(e.target.result);
      const loaded=parsed.data||parsed;
      if(!loaded.semesters) throw new Error("Invalid file — missing semesters");
      data=loaded; collapsedSems={};
      renderAll();
      showToast(`✓ Loaded "${file.name}" successfully!`);
    } catch(err) {
      showToast("✗ Load failed: "+err.message, true);
    }
  };
  reader.readAsText(file);
  event.target.value="";
}

// ── Summary Modal ─────────────────────────────────────────────────────────────
function openSummary() {
  const retagged  = getRetagged();
  const origR     = calcCPI(false), newR = calcCPI(true);
  const origCPI   = origR?.val??null, newCPI = newR?.val??null;
  const origCr    = origR?.credits??0, newCr = newR?.credits??0;
  const cpiDiff   = (origCPI!==null&&newCPI!==null) ? newCPI-origCPI : null;
  const origTags  = tagCredits(false), newTags = tagCredits(true);
  const allTagKeys=[...new Set([...Object.keys(origTags),...Object.keys(newTags)])];

  // Group retagged by semester
  const bySem={};
  for(const r of retagged) { if(!bySem[r.sem]) bySem[r.sem]=[]; bySem[r.sem].push(r); }

  // 1. CPI Impact
  const cpiSection=`
  <div class="summary-section">
    <h4>CPI &amp; Credit Impact</h4>
    <div class="cpi-summary-grid">
      <div class="cpi-box">
        <div class="cb-label">Original</div>
        <div class="cb-val">${origCPI!==null?origCPI.toFixed(3):"—"}</div>
        <div class="cb-sub">
          ${origCr} CPI credits<br>
          GPA: ${origCPI!==null?(origCPI*0.4).toFixed(3):"—"} / 4
        </div>
      </div>
      <div class="cpi-box" style="border-color:${cpiDiff===null?"var(--border)":cpiDiff>0?"rgba(62,207,142,0.4)":"rgba(224,82,96,0.4)"}">
        <div class="cb-label">After Retag</div>
        <div class="cb-val" style="color:${cpiDiff===null?"inherit":cpiDiff>0?"var(--green)":"var(--red)"}">${newCPI!==null?newCPI.toFixed(3):"—"}</div>
        <div class="cb-sub">
          ${newCr} CPI credits
          ${newCr!==origCr?`<span style="color:${newCr>origCr?"var(--green)":"var(--red)"};font-weight:700"> (${newCr>origCr?"+":""}${newCr-origCr})</span>`:""}
          <br>
          GPA: ${newCPI!==null?(newCPI*0.4).toFixed(3):"—"} / 4
          ${cpiDiff!==null&&Math.abs(cpiDiff)>0.0001
            ?`<span style="font-weight:700;color:${cpiDiff>0?"var(--green)":"var(--red)"}"> (${cpiDiff>0?"▲ +":"▼ "}${cpiDiff.toFixed(4)})</span>`
            :" · No change"}
        </div>
      </div>
    </div>
  </div>`;

  // 2. Tag-wise credits
  const tagSection=`
  <div class="summary-section">
    <h4>Tag-wise Credit Breakdown (CPI courses only)</h4>
    ${allTagKeys.length===0?'<div class="no-retag">No CPI-counted courses.</div>':
      allTagKeys.map(tag=>{
        const m=TAG_META[tag];
        const o=origTags[tag]||0, n=newTags[tag]||0, d=n-o;
        return `<div class="tag-summary-row">
          <div class="tsr-label">
            <span class="tag-badge" style="background:${m.color}22;color:${m.color};border:1px solid ${m.color}44">${m.short}</span>
            <span style="color:var(--muted);font-size:12px">${m.label}</span>
          </div>
          <div style="display:flex;align-items:center;gap:9px">
            <span class="tsr-cr">${n} cr</span>
            ${d!==0
              ?`<span style="font-size:11px;color:${d>0?"var(--green)":"var(--red)"};font-weight:700">${d>0?"+":""}${d} from ${o}</span>`
              :`<span style="font-size:11px;color:var(--muted)">(unchanged)</span>`}
          </div>
        </div>`;
      }).join("")
    }
  </div>`;

  // 3. Retagged courses list
  const retagSection=`
  <div class="summary-section">
    <h4>Retagged Courses (${retagged.length})</h4>
    ${retagged.length===0
      ?'<div class="no-retag">No courses retagged yet. Change the New Tag column to start.</div>'
      :Object.entries(bySem).map(([semName,courses])=>`
        <div class="sem-group-label">${semName}</div>
        ${courses.map(r=>{
          const fm=TAG_META[r.from], tm=TAG_META[r.to];
          const origCounts=fm?.counts, newCounts=tm?.counts;
          const cpiNote=origCounts!==newCounts
            ?`<span style="font-size:10px;font-weight:700;color:${newCounts?"var(--green)":"var(--red)"};margin-left:4px">${newCounts?"▲ into CPI":"▼ out of CPI"}</span>`
            :"";
          return `<div class="summary-row">
            <span class="sr-code">${r.code}</span>
            <span class="sr-name" title="${r.name}">${r.name}</span>
            <span style="white-space:nowrap;display:flex;align-items:center;gap:4px">
              <span class="tag-badge" style="background:${fm?.color}22;color:${fm?.color};border:1px solid ${fm?.color}44">${fm?.short??r.from}</span>
              <span style="color:var(--muted)">→</span>
              <span class="tag-badge" style="background:${tm?.color}22;color:${tm?.color};border:1px solid ${tm?.color}44">${tm?.short??r.to}</span>
              ${cpiNote}
            </span>
            <span class="sr-cr">${r.credits} cr · ${r.grade}</span>
          </div>`;
        }).join("")}
      `).join("")
    }
  </div>`;

  document.getElementById("summary-body").innerHTML = cpiSection + tagSection + retagSection;
  document.getElementById("summary-modal").style.display = "flex";
}

// ── Boot ──────────────────────────────────────────────────────────────────────
renderAll();
</script>
</body>
</html>
"""

# ── HTTP server ───────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # suppress request noise

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            page = HTML.replace("__INITIAL_DATA__", json.dumps(INITIAL_DATA))
            body = page.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

def open_browser(port):
    time.sleep(0.9)
    webbrowser.open(f"http://localhost:{port}")

if __name__ == "__main__":
    PORT = 5000
    server = HTTPServer(("localhost", PORT), Handler)
    print()
    print("  ╔═══════════════════════════════════════════╗")
    print("  ║   RetagHelper v2 — IIT Bombay             ║")
    print("  ╠═══════════════════════════════════════════╣")
    print(f"  ║   Running at  http://localhost:{PORT}      ║")
    print("  ║   Browser opening automatically...        ║")
    print("  ║   Ctrl+C to stop                          ║")
    print("  ╚═══════════════════════════════════════════╝")
    print()
    threading.Thread(target=open_browser, args=(PORT,), daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped. Goodbye!")
