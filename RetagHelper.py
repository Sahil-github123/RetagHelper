#!/usr/bin/env python3
"""
RetagHelper - IIT Bombay CPI/SPI Retag Calculator
Run:  python retag_helper.py
Open: http://localhost:5000
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
                {"id":"c21", "code":"AE 410",  "name":"Navigation and Guidance",                        "tag":"D", "newTag":"D", "credits":6, "grade":"AA"},
                {"id":"c22", "code":"EC 101",  "name":"Economics",                                      "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c23", "code":"ES 250",  "name":"Environmental Studies: Science & Engineering",   "tag":"N", "newTag":"N", "credits":3, "grade":"PP"},
                {"id":"c24", "code":"HS 250",  "name":"Environmental Studies",                          "tag":"N", "newTag":"N", "credits":3, "grade":"PP"},
                {"id":"c25", "code":"SC 618",  "name":"Analytical and Geometric Dynamics",              "tag":"M", "newTag":"M", "credits":6, "grade":"AA"},
                {"id":"c26", "code":"SC 639",  "name":"Mathematical Structures for Control",            "tag":"M", "newTag":"M", "credits":6, "grade":"AA"},
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
                {"id":"c32", "code":"AE 686",  "name":"Guidance of Aerospace Vehicles",                 "tag":"T", "newTag":"T", "credits":6, "grade":"AA"},
                {"id":"c33", "code":"DE 250",  "name":"Design Thinking for Innovation",                 "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c34", "code":"PH 111",  "name":"Introduction to Classical Physics",              "tag":"C", "newTag":"C", "credits":4, "grade":"AA"},
                {"id":"c35", "code":"SC 202",  "name":"Signals and Feedback Systems",                   "tag":"M", "newTag":"M", "credits":6, "grade":"AA"},
                {"id":"c36", "code":"SC 602",  "name":"Control of Nonlinear Dynamical Systems",         "tag":"SE","newTag":"SE","credits":6, "grade":"AA"},
            ]
        },
        {
            "id": "s5", "name": "Semester 5",
            "courses": [
                {"id":"c37", "code":"AE 219",  "name":"Supervised Learning",                            "tag":"T", "newTag":"T", "credits":6, "grade":"AA"},
                {"id":"c38", "code":"AE 339",  "name":"High Speed Aerodynamics",                        "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c39", "code":"AE 341",  "name":"Flight Mechanics of Aircrafts and Spacecrafts",  "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c40", "code":"AE 343",  "name":"Aerodynamics Laboratory",                        "tag":"C", "newTag":"C", "credits":3, "grade":"AA"},
                {"id":"c41", "code":"AE 344",  "name":"Aero Propulsion",                                "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c42", "code":"AE 345",  "name":"Aircraft Propulsion Laboratory",                 "tag":"C", "newTag":"C", "credits":3, "grade":"AA"},
                {"id":"c43", "code":"AE 667",  "name":"Rotary Wing Aerodynamics",                       "tag":"D", "newTag":"D", "credits":6, "grade":"AA"},
                {"id":"c44", "code":"ENT617",  "name":"Tech-Opportunities Identification",              "tag":"HE","newTag":"HE","credits":6, "grade":"AA"},
                {"id":"c45", "code":"ME 781",  "name":"Statistical Machine Learning and Data Mining",   "tag":"M", "newTag":"M", "credits":6, "grade":"AA"},
                {"id":"c46", "code":"SC 301",  "name":"Linear and Nonlinear Systems",                   "tag":"M", "newTag":"M", "credits":6, "grade":"AA"},
            ]
        },
        {
            "id": "s6", "name": "Semester 6",
            "courses": [
                {"id":"c47", "code":"SEM 6",   "name":"All Electives",                                  "tag":"C", "newTag":"C", "credits":35,"grade":"AA"},
                {"id":"c48", "code":"SLP 2",   "name":"Supervised Learning Project 2",                  "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
                {"id":"c49", "code":"HON-E",   "name":"Honours Elective",                               "tag":"E", "newTag":"E", "credits":6, "grade":"AA"},
                {"id":"c50", "code":"SC 607",  "name":"SC 607",                                         "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
            ]
        },
        {
            "id": "s7", "name": "Semester 7",
            "courses": [
                {"id":"c51", "code":"SEM 7",   "name":"All Electives",                                  "tag":"C", "newTag":"C", "credits":48,"grade":"AA"},
                {"id":"c52", "code":"BTP 1",   "name":"B.Tech Project 1",                               "tag":"C", "newTag":"C", "credits":6, "grade":"AA"},
            ]
        },
        {
            "id": "s8", "name": "Semester 8",
            "courses": [
                {"id":"c53", "code":"SEM 8",   "name":"All Electives",                                  "tag":"C", "newTag":"C", "credits":42,"grade":"AA"},
                {"id":"c54", "code":"BTP 2",   "name":"B.Tech Project 2",                               "tag":"C", "newTag":"C", "credits":0, "grade":"AA"},
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
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg:       #0d1117;
    --bg2:      #131920;
    --bg3:      #1a2230;
    --border:   rgba(255,255,255,0.08);
    --border2:  rgba(255,255,255,0.13);
    --text:     #e8edf2;
    --muted:    #8a9bae;
    --blue:     #3b82f6;
    --green:    #3ecf8e;
    --red:      #e05260;
    --amber:    #f0913a;
    --purple:   #8b5cf6;
  }
  body { background: var(--bg); color: var(--text); font-family: 'DM Sans', sans-serif; min-height: 100vh; }

  /* scrollbar */
  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 3px; }

  /* ── Top bar ── */
  #topbar {
    position: sticky; top: 0; z-index: 100;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 28px; height: 58px;
    background: rgba(13,17,23,0.88); backdrop-filter: blur(14px);
    border-bottom: 1px solid var(--border);
  }
  #logo { display: flex; align-items: center; gap: 11px; }
  #logo .icon {
    width: 32px; height: 32px; border-radius: 8px;
    background: linear-gradient(135deg, var(--blue), var(--purple));
    display: flex; align-items: center; justify-content: center;
    font-weight: 900; font-size: 17px; font-family: 'Syne', sans-serif;
  }
  #logo .title { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 17px; letter-spacing: -0.02em; }
  #logo .badge { font-size: 11px; color: var(--muted); background: rgba(255,255,255,0.06); border-radius: 20px; padding: 2px 10px; font-weight: 600; }

  /* score cards */
  .score-cards { display: flex; gap: 10px; align-items: center; }
  .score-card {
    background: rgba(255,255,255,0.04); border: 1px solid var(--border);
    border-radius: 10px; padding: 8px 16px; min-width: 120px;
  }
  .score-card .sc-label { font-size: 10px; color: var(--muted); font-weight: 700; letter-spacing: .09em; text-transform: uppercase; margin-bottom: 3px; }
  .score-card .sc-val { display: flex; align-items: baseline; gap: 7px; }
  .score-card .sc-num { font-size: 22px; font-weight: 800; font-variant-numeric: tabular-nums; font-family: 'DM Mono', monospace; }
  .score-card .sc-delta { font-size: 11px; font-weight: 700; }
  .score-card .sc-was { font-size: 10px; color: var(--muted); margin-top: 1px; }

  /* ── Main ── */
  #main { max-width: 1160px; margin: 0 auto; padding: 26px 22px 60px; }

  /* legend */
  #legend { display: flex; flex-wrap: wrap; gap: 7px; margin-bottom: 22px; }
  .leg { display: flex; align-items: center; gap: 5px; font-size: 11px; color: var(--muted); }
  .leg .lbadge {
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: 11px; font-weight: 700; letter-spacing: .04em; white-space: nowrap;
  }
  .leg .cpi-dot { color: var(--green); font-size: 10px; }

  /* SPI row */
  #spi-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px; }

  /* info bar */
  .infobar {
    background: rgba(59,130,246,0.07); border: 1px solid rgba(59,130,246,0.22);
    border-radius: 10px; padding: 10px 16px; margin-bottom: 20px;
    font-size: 12.5px; color: #93c5fd; line-height: 1.55;
  }

  /* ── Semester block ── */
  .sem-block {
    background: rgba(255,255,255,0.025); border: 1px solid var(--border);
    border-radius: 14px; overflow: hidden; margin-bottom: 14px;
    transition: border-color .2s;
  }
  .sem-block:hover { border-color: rgba(255,255,255,0.14); }

  .sem-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 20px; cursor: pointer;
    background: rgba(59,130,246,0.05);
    border-bottom: 1px solid var(--border);
    user-select: none;
  }
  .sem-header .sh-left { display: flex; align-items: center; gap: 12px; }
  .sem-header .sh-title { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 14px; }
  .sem-header .sh-meta { font-size: 11.5px; color: var(--muted); }
  .sem-header .sh-warn {
    font-size: 11px; color: var(--amber);
    background: rgba(240,145,58,0.12); border: 1px solid rgba(240,145,58,0.35);
    border-radius: 4px; padding: 2px 8px; font-weight: 700;
  }
  .sem-header .sh-right { display: flex; align-items: center; gap: 14px; }
  .sem-spi { text-align: right; }
  .sem-spi .spi-label { font-size: 10px; color: var(--muted); font-weight: 700; letter-spacing: .08em; }
  .sem-spi .spi-val { display: flex; align-items: baseline; gap: 6px; }
  .sem-spi .spi-num { font-size: 15px; font-weight: 800; font-variant-numeric: tabular-nums; font-family: 'DM Mono', monospace; }
  .sem-spi .spi-delta { font-size: 11px; font-weight: 700; }
  .toggle-arrow { color: var(--muted); font-size: 16px; transition: transform .2s; }

  /* table */
  .tbl-header {
    display: grid;
    grid-template-columns: 88px 1fr 80px 72px 88px 100px 34px;
    gap: 6px; padding: 7px 20px;
    font-size: 10px; color: var(--muted); font-weight: 700; letter-spacing: .08em;
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }
  .course-row {
    display: grid;
    grid-template-columns: 88px 1fr 80px 72px 88px 100px 34px;
    gap: 6px; padding: 5px 20px;
    align-items: center;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    transition: background .15s;
  }
  .course-row:hover { background: rgba(255,255,255,0.02); }
  .course-row.changed { background: rgba(59,130,246,0.04); }

  .c-code { font-family: 'DM Mono', monospace; font-size: 11.5px; color: #a0b4c8; font-weight: 500; }
  .c-name { font-size: 12.5px; color: #c8d5e0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

  input.num-input, select.sel {
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 6px; padding: 5px 8px; color: var(--text); font-size: 13px;
    outline: none; width: 100%; font-family: inherit;
    transition: border-color .15s;
  }
  input.num-input:focus, select.sel:focus { border-color: var(--blue); }
  select.sel { background: #131920; cursor: pointer; }
  select.sel:disabled { opacity: 0.5; cursor: not-allowed; }
  select.sel.changed { background: rgba(59,130,246,0.14); border-color: var(--blue); color: #93c5fd; font-weight: 700; }

  .tag-badge {
    display: inline-block; padding: 3px 9px; border-radius: 5px;
    font-size: 11px; font-weight: 700; letter-spacing: .04em; white-space: nowrap;
  }
  .new-tag-wrap { position: relative; }
  .effect-dot {
    position: absolute; top: -5px; right: -5px;
    width: 14px; height: 14px; border-radius: 50%;
    font-size: 10px; font-weight: 900; display: flex; align-items: center; justify-content: center;
    color: #fff; pointer-events: none;
  }

  .del-btn {
    background: transparent; border: none; color: rgba(224,82,96,0.45);
    cursor: pointer; font-size: 17px; padding: 3px 6px; border-radius: 5px;
    transition: color .15s, background .15s; line-height: 1;
  }
  .del-btn:hover { color: var(--red); background: rgba(224,82,96,0.1); }

  /* add course row */
  .add-course-btn {
    display: flex; align-items: center; gap: 7px;
    background: rgba(59,130,246,0.07); border: 1px dashed rgba(59,130,246,0.38);
    border-radius: 8px; padding: 7px 14px; margin: 8px 20px 10px;
    color: var(--blue); cursor: pointer; font-weight: 600; font-size: 13px;
    font-family: inherit; transition: background .15s;
  }
  .add-course-btn:hover { background: rgba(59,130,246,0.13); }

  /* add semester */
  #add-sem-area { margin-top: 8px; }
  .add-sem-btn {
    display: flex; align-items: center; justify-content: center; gap: 8px;
    background: rgba(255,255,255,0.03); border: 1px dashed rgba(255,255,255,0.18);
    border-radius: 12px; padding: 12px 20px; color: var(--muted);
    cursor: pointer; font-weight: 600; font-size: 14px; width: 100%;
    font-family: inherit; transition: background .15s;
  }
  .add-sem-btn:hover { background: rgba(255,255,255,0.06); }
  .add-sem-row { display: flex; gap: 10px; align-items: center; }
  .add-sem-row input {
    flex: 1; background: rgba(255,255,255,0.06); border: 1px solid var(--border2);
    border-radius: 8px; padding: 9px 14px; color: var(--text); font-size: 14px;
    outline: none; font-family: inherit;
  }
  .add-sem-row input:focus { border-color: var(--blue); }
  .btn-primary {
    padding: 9px 20px; border-radius: 8px; background: var(--blue); border: none;
    color: #fff; cursor: pointer; font-weight: 700; font-size: 14px; font-family: inherit;
    transition: background .15s;
  }
  .btn-primary:hover { background: #2563eb; }
  .btn-ghost {
    padding: 9px 16px; border-radius: 8px; background: transparent;
    border: 1px solid var(--border2); color: var(--muted); cursor: pointer;
    font-family: inherit; transition: background .15s;
  }
  .btn-ghost:hover { background: rgba(255,255,255,0.06); }

  /* ── Modal ── */
  .modal-overlay {
    position: fixed; inset: 0; background: rgba(0,0,0,0.72);
    backdrop-filter: blur(7px); display: flex; align-items: center; justify-content: center;
    z-index: 999;
  }
  .modal {
    background: #1a2230; border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px; padding: 28px; width: 440px; max-width: 95vw;
  }
  .modal h3 { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 18px; margin-bottom: 20px; }
  .field { display: flex; flex-direction: column; gap: 5px; }
  .field label { font-size: 11px; color: var(--muted); font-weight: 700; letter-spacing: .08em; }
  .field input, .field select {
    background: rgba(255,255,255,0.06); border: 1px solid var(--border2);
    border-radius: 8px; padding: 9px 12px; color: var(--text); font-size: 14px;
    outline: none; font-family: inherit;
  }
  .field input:focus, .field select:focus { border-color: var(--blue); }
  .field select { background: #1a2230; }
  .modal-fields { display: flex; flex-direction: column; gap: 14px; }
  .modal-3col { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
  .modal-footer { display: flex; gap: 10px; justify-content: flex-end; margin-top: 22px; }

  .footer { margin-top: 36px; text-align: center; font-size: 11.5px; color: #526070; line-height: 1.75; }

  /* collapsed */
  .sem-body.collapsed { display: none; }

  @media (max-width: 700px) {
    .tbl-header, .course-row { grid-template-columns: 70px 1fr 60px 60px 76px 90px 30px; font-size: 11px; }
    #topbar .score-cards .score-card:last-child { display: none; }
  }
</style>
</head>
<body>

<div id="topbar">
  <div id="logo">
    <div class="icon">R</div>
    <span class="title">RetagHelper</span>
    <span class="badge">IIT Bombay</span>
  </div>
  <div class="score-cards">
    <div class="score-card" id="sc-cpi">
      <div class="sc-label">CPI</div>
      <div class="sc-val"><span class="sc-num" id="sc-cpi-num">—</span><span class="sc-delta" id="sc-cpi-delta"></span></div>
      <div class="sc-was" id="sc-cpi-was"></div>
    </div>
    <div class="score-card" id="sc-gpa">
      <div class="sc-label">GPA / 4</div>
      <div class="sc-val"><span class="sc-num" id="sc-gpa-num">—</span><span class="sc-delta" id="sc-gpa-delta"></span></div>
      <div class="sc-was" id="sc-gpa-was"></div>
    </div>
  </div>
</div>

<div id="main">
  <div id="legend"></div>
  <div id="spi-row"></div>
  <div class="infobar">
    ℹ&nbsp; Change the <strong>New Tag</strong> column to simulate retagging. Tags counting toward CPI: <strong>Core (C), Dept Elective (D), STEM Elective (SE), HASMED Elective (HE)</strong>.
    Min <strong>18 credits</strong> per semester. Retagging is allowed only <strong>twice</strong> in the entire program (before placements & post curriculum).
    Indicators: <span style="color:var(--green)">▲ gain</span> · <span style="color:var(--red)">▼ loss</span> · <span style="background:var(--green);color:#fff;border-radius:50%;padding:0 3px;font-size:10px">+</span> now counts · <span style="background:var(--red);color:#fff;border-radius:50%;padding:0 3px;font-size:10px">−</span> no longer counts.
  </div>
  <div id="sem-container"></div>
  <div id="add-sem-area">
    <button class="add-sem-btn" onclick="showAddSem()"><span style="font-size:18px">+</span> Add Semester</button>
    <div class="add-sem-row" id="add-sem-row" style="display:none">
      <input id="new-sem-name" placeholder="e.g. Semester 9" onkeydown="if(event.key==='Enter')addSemester()">
      <button class="btn-primary" onclick="addSemester()">Add</button>
      <button class="btn-ghost" onclick="hideAddSem()">Cancel</button>
    </div>
  </div>
  <div class="footer">
    Tag transition rules per IIT Bombay UG Rulebook 2025-26 &nbsp;·&nbsp;
    Retagging available twice: before placements (2nd last sem) &amp; post curriculum completion (last sem) &nbsp;·&nbsp;
    Changes shown in blue affect CPI
  </div>
</div>

<!-- Add Course Modal -->
<div class="modal-overlay" id="add-modal" style="display:none" onclick="if(event.target===this)closeModal()">
  <div class="modal">
    <h3>Add Course</h3>
    <div class="modal-fields">
      <div class="field"><label>COURSE CODE</label><input id="m-code" placeholder="e.g. AE 301"></div>
      <div class="field"><label>COURSE NAME</label><input id="m-name" placeholder="e.g. Advanced Aerodynamics"></div>
      <div class="modal-3col">
        <div class="field">
          <label>TAG</label>
          <select id="m-tag"></select>
        </div>
        <div class="field">
          <label>CREDITS</label>
          <input id="m-credits" type="number" min="0" max="24" value="6">
        </div>
        <div class="field">
          <label>GRADE</label>
          <select id="m-grade">
            <option>AA</option><option>AB</option><option selected>BB</option>
            <option>BC</option><option>CC</option><option>CD</option><option>DD</option>
            <option>FF</option><option value="PP">PP (non-credit)</option>
          </select>
        </div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn-ghost" onclick="closeModal()">Cancel</button>
      <button class="btn-primary" onclick="submitAddCourse()">Add Course</button>
    </div>
  </div>
</div>

<script>
// ── Tag definitions ─────────────────────────────────────────────────────────
const TAG_META = {
  C:  { label: "Core Course",              short: "Core",   color: "#e05260", counts: true  },
  D:  { label: "Department Elective",      short: "Dept E", color: "#f07d3a", counts: true  },
  SE: { label: "STEM Elective",            short: "STEM",   color: "#4ca4e0", counts: true  },
  HE: { label: "HASMED Elective",          short: "HSMD",   color: "#9b63d8", counts: true  },
  M:  { label: "Minor Course",             short: "Minor",  color: "#2db58e", counts: false },
  T:  { label: "Additional Learning (ALC)","short": "ALC",  color: "#8a9bae", counts: false },
  O:  { label: "Honors Course",            short: "Honors", color: "#c9a227", counts: false },
  E:  { label: "Honors Elective",          short: "Hon. E", color: "#b08040", counts: false },
  N:  { label: "Non-credit",               short: "N/A",    color: "#555",    counts: false },
};

const TAG_TRANSITIONS = {
  T:  ["D","SE","HE","O","E","M"],
  C:  [],
  D:  ["T","O","E"],
  SE: ["T"],
  HE: ["T"],
  O:  ["T","D","E"],
  E:  ["T","D","O"],
  M:  ["T","SE","HE"],
  N:  [],
};

const GRADE_POINTS = { AA:10, AB:9, BB:8, BC:7, CC:6, CD:5, DD:4, FF:0, FR:0 };

// ── State ────────────────────────────────────────────────────────────────────
let data = __INITIAL_DATA__;
let _uid = 200;
const uid = () => `uid_${++_uid}`;
let collapsedSems = {};
let modalTargetSemId = null;

// ── Calculations ─────────────────────────────────────────────────────────────
function calcSPI(courses, useNew) {
  let ws = 0, tc = 0;
  for (const c of courses) {
    const tag = useNew ? c.newTag : c.tag;
    if (!TAG_META[tag]?.counts) continue;
    const gp = GRADE_POINTS[c.grade];
    if (gp === undefined) continue;
    ws += gp * c.credits;
    tc += c.credits;
  }
  return tc > 0 ? ws / tc : null;
}

function calcCPI(useNew) {
  let ws = 0, tc = 0;
  for (const sem of data.semesters) {
    for (const c of sem.courses) {
      const tag = useNew ? c.newTag : c.tag;
      if (!TAG_META[tag]?.counts) continue;
      const gp = GRADE_POINTS[c.grade];
      if (gp === undefined) continue;
      ws += gp * c.credits;
      tc += c.credits;
    }
  }
  return tc > 0 ? ws / tc : null;
}

function semTotalCredits(courses) {
  return courses.reduce((s, c) => s + (c.credits || 0), 0);
}

// ── Render helpers ────────────────────────────────────────────────────────────
function tagBadge(tag) {
  const m = TAG_META[tag] || { short: tag, color: "#666" };
  return `<span class="tag-badge" style="background:${m.color}22;color:${m.color};border:1px solid ${m.color}44">${m.short}</span>`;
}

function scoreCardUpdate(id, orig, updated) {
  const numEl   = document.getElementById(`sc-${id}-num`);
  const deltaEl = document.getElementById(`sc-${id}-delta`);
  const wasEl   = document.getElementById(`sc-${id}-was`);
  if (!numEl) return;
  const val = updated !== null ? updated : orig;
  numEl.textContent = val !== null ? val.toFixed(3) : "—";
  if (orig !== null && updated !== null) {
    const diff = updated - orig;
    if (Math.abs(diff) > 0.0001) {
      deltaEl.textContent = (diff > 0 ? "▲ " : "▼ ") + Math.abs(diff).toFixed(3);
      deltaEl.style.color = diff > 0 ? "var(--green)" : "var(--red)";
      wasEl.textContent = `was ${orig.toFixed(3)}`;
    } else {
      deltaEl.textContent = "";
      wasEl.textContent = "";
    }
  }
}

// ── Legend ────────────────────────────────────────────────────────────────────
function renderLegend() {
  const el = document.getElementById("legend");
  el.innerHTML = Object.entries(TAG_META).map(([k, v]) =>
    `<div class="leg">
      <span class="lbadge" style="background:${v.color}22;color:${v.color};border:1px solid ${v.color}44">${v.short}</span>
      <span>${v.label}</span>
      ${v.counts ? '<span class="cpi-dot">⟵ CPI</span>' : ''}
    </div>`
  ).join("");
}

// ── SPI row ───────────────────────────────────────────────────────────────────
function renderSPIRow() {
  const el = document.getElementById("spi-row");
  el.innerHTML = data.semesters.map((sem, i) => {
    const orig = calcSPI(sem.courses, false);
    const upd  = calcSPI(sem.courses, true);
    const diff = (orig !== null && upd !== null) ? upd - orig : null;
    const changed = diff !== null && Math.abs(diff) > 0.0001;
    return `<div class="score-card">
      <div class="sc-label">Sem ${i+1} SPI</div>
      <div class="sc-val">
        <span class="sc-num" style="font-size:17px">${upd !== null ? upd.toFixed(2) : "—"}</span>
        ${changed ? `<span class="sc-delta" style="color:${diff>0?"var(--green)":"var(--red)"}">${diff>0?"▲":"▼"} ${Math.abs(diff).toFixed(3)}</span>` : ""}
      </div>
      ${changed && orig !== null ? `<div class="sc-was">was ${orig.toFixed(2)}</div>` : ""}
    </div>`;
  }).join("");
}

// ── Full render ───────────────────────────────────────────────────────────────
function renderAll() {
  renderLegend();
  renderSemesterContainer();
  renderSPIRow();
  updateTopbar();
}

function updateTopbar() {
  const origCPI = calcCPI(false);
  const newCPI  = calcCPI(true);
  scoreCardUpdate("cpi", origCPI, newCPI);
  scoreCardUpdate("gpa",
    origCPI !== null ? origCPI * 0.4 : null,
    newCPI  !== null ? newCPI  * 0.4 : null
  );
}

function renderSemesterContainer() {
  const container = document.getElementById("sem-container");
  container.innerHTML = data.semesters.map((sem, i) => renderSemBlock(sem, i)).join("");
}

function renderSemBlock(sem, idx) {
  const origSPI = calcSPI(sem.courses, false);
  const newSPI  = calcSPI(sem.courses, true);
  const diff    = (origSPI !== null && newSPI !== null) ? newSPI - origSPI : null;
  const changed = diff !== null && Math.abs(diff) > 0.0001;
  const totalCr = semTotalCredits(sem.courses);
  const belowMin = totalCr > 0 && totalCr < 18;
  const collapsed = collapsedSems[sem.id];

  const coursesHTML = sem.courses.map(c => renderCourseRow(c, sem.id)).join("");
  const allOpts    = (TAG_TRANSITIONS[sem.tag] ?? []).concat(sem.tag);

  return `
  <div class="sem-block" id="semblock-${sem.id}">
    <div class="sem-header" onclick="toggleSem('${sem.id}')">
      <div class="sh-left">
        <span class="sh-title">${sem.name}</span>
        <span class="sh-meta">${sem.courses.length} courses · ${totalCr} credits</span>
        ${belowMin ? '<span class="sh-warn">⚠ Below 18 cr</span>' : ''}
      </div>
      <div class="sh-right">
        ${origSPI !== null ? `<div class="sem-spi">
          <div class="spi-label">SPI</div>
          <div class="spi-val">
            <span class="spi-num">${(newSPI ?? origSPI).toFixed(2)}</span>
            ${changed ? `<span class="spi-delta" style="color:${diff>0?"var(--green)":"var(--red)"}">${diff>0?"▲":"▼"} ${Math.abs(diff).toFixed(3)}</span>` : ""}
          </div>
        </div>` : ""}
        <span class="toggle-arrow" style="transform:rotate(${collapsed?"-90deg":"0deg"})"">▾</span>
      </div>
    </div>
    <div class="sem-body${collapsed ? " collapsed" : ""}">
      <div class="tbl-header">
        <span>CODE</span><span>COURSE NAME</span><span>CREDITS</span>
        <span>GRADE</span><span>ORIG TAG</span><span>NEW TAG</span><span></span>
      </div>
      ${coursesHTML}
      <button class="add-course-btn" onclick="openAddModal('${sem.id}')">
        <span style="font-size:16px;line-height:1">+</span> Add Course
      </button>
    </div>
  </div>`;
}

function renderCourseRow(c, semId) {
  const allowed   = TAG_TRANSITIONS[c.tag] ?? [];
  const allOpts   = [c.tag, ...allowed];
  const isChanged = c.newTag !== c.tag;
  const origCounts = TAG_META[c.tag]?.counts;
  const newCounts  = TAG_META[c.newTag]?.counts;
  const effectChanged = origCounts !== newCounts;

  const gradeOpts = ["AA","AB","BB","BC","CC","CD","DD","FF","PP"].map(g =>
    `<option value="${g}"${c.grade===g?" selected":""}>${g}</option>`
  ).join("");

  const newTagOpts = allOpts.map(t =>
    `<option value="${t}"${c.newTag===t?" selected":""}>${TAG_META[t]?.short ?? t}</option>`
  ).join("");

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
      ${effectChanged ? `<span class="effect-dot" style="background:${newCounts?"var(--green)":"var(--red)"}"
        title="${newCounts?"Now counts toward CPI":"No longer counts toward CPI"}">${newCounts?"+":"−"}</span>` : ""}
    </div>
    <button class="del-btn" onclick="deleteCourse('${semId}','${c.id}')" title="Remove">×</button>
  </div>`;
}

// ── Event handlers ────────────────────────────────────────────────────────────
function toggleSem(semId) {
  collapsedSems[semId] = !collapsedSems[semId];
  renderSemesterContainer();
  renderSPIRow();
}

function updateCourse(semId, courseId, field, val) {
  const sem = data.semesters.find(s => s.id === semId);
  if (!sem) return;
  const c = sem.courses.find(x => x.id === courseId);
  if (!c) return;
  c[field] = val;
  if (field === "tag") { c.newTag = val; }  // reset newTag when orig tag changes
  // Partial re-render: just update the row + topbar + spi row
  const rowEl = document.getElementById(`row-${courseId}`);
  if (rowEl) rowEl.outerHTML = renderCourseRow(c, semId);
  // Re-render sem header
  const semBlock = document.getElementById(`semblock-${semId}`);
  if (semBlock) {
    const semIdx = data.semesters.findIndex(s => s.id === semId);
    semBlock.outerHTML = renderSemBlock(data.semesters[semIdx], semIdx);
  }
  renderSPIRow();
  updateTopbar();
}

function deleteCourse(semId, courseId) {
  const sem = data.semesters.find(s => s.id === semId);
  if (!sem) return;
  sem.courses = sem.courses.filter(c => c.id !== courseId);
  const semIdx = data.semesters.findIndex(s => s.id === semId);
  const semBlock = document.getElementById(`semblock-${semId}`);
  if (semBlock) semBlock.outerHTML = renderSemBlock(data.semesters[semIdx], semIdx);
  renderSPIRow();
  updateTopbar();
}

// ── Add course modal ──────────────────────────────────────────────────────────
function openAddModal(semId) {
  modalTargetSemId = semId;
  // populate tag select
  const tagSel = document.getElementById("m-tag");
  tagSel.innerHTML = Object.entries(TAG_META).map(([k,v]) =>
    `<option value="${k}">${v.short} — ${v.label}</option>`
  ).join("");
  document.getElementById("m-code").value = "";
  document.getElementById("m-name").value = "";
  document.getElementById("m-credits").value = 6;
  document.getElementById("add-modal").style.display = "flex";
}
function closeModal() { document.getElementById("add-modal").style.display = "none"; }

function submitAddCourse() {
  const code    = document.getElementById("m-code").value.trim();
  const name    = document.getElementById("m-name").value.trim();
  const tag     = document.getElementById("m-tag").value;
  const credits = +document.getElementById("m-credits").value;
  const grade   = document.getElementById("m-grade").value;
  if (!code || !name) { alert("Please fill in code and name."); return; }
  const sem = data.semesters.find(s => s.id === modalTargetSemId);
  if (!sem) return;
  sem.courses.push({ id: uid(), code, name, tag, newTag: tag, credits, grade });
  closeModal();
  const semIdx = data.semesters.findIndex(s => s.id === modalTargetSemId);
  const semBlock = document.getElementById(`semblock-${modalTargetSemId}`);
  if (semBlock) semBlock.outerHTML = renderSemBlock(data.semesters[semIdx], semIdx);
  renderSPIRow();
  updateTopbar();
}

// ── Add semester ──────────────────────────────────────────────────────────────
function showAddSem() {
  document.querySelector(".add-sem-btn").style.display = "none";
  document.getElementById("add-sem-row").style.display = "flex";
  document.getElementById("new-sem-name").focus();
}
function hideAddSem() {
  document.querySelector(".add-sem-btn").style.display = "flex";
  document.getElementById("add-sem-row").style.display = "none";
}
function addSemester() {
  const name = document.getElementById("new-sem-name").value.trim();
  if (!name) return;
  data.semesters.push({ id: uid(), name, courses: [] });
  hideAddSem();
  document.getElementById("new-sem-name").value = "";
  renderSemesterContainer();
  renderSPIRow();
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
        pass  # suppress request logs

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            page = HTML.replace("__INITIAL_DATA__", json.dumps(INITIAL_DATA))
            body = page.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

def open_browser(port):
    time.sleep(0.8)
    webbrowser.open(f"http://localhost:{port}")

if __name__ == "__main__":
    PORT = 5000
    server = HTTPServer(("localhost", PORT), Handler)
    print(f"\n  ╔══════════════════════════════════════╗")
    print(f"  ║   RetagHelper — IIT Bombay           ║")
    print(f"  ╠══════════════════════════════════════╣")
    print(f"  ║   Running at http://localhost:{PORT}   ║")
    print(f"  ║   Opening in your browser...         ║")
    print(f"  ║   Press Ctrl+C to stop               ║")
    print(f"  ╚══════════════════════════════════════╝\n")
    threading.Thread(target=open_browser, args=(PORT,), daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
