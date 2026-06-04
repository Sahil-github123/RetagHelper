const PROGRAM_SCHEMAS = {
  ug: {
    badge: "IIT Bombay · UG",
    footer: `Tag rules per IIT Bombay UG Rulebook 2025-26 &nbsp;·&nbsp; Retagging: twice in program (pre-placements &amp; post-curriculum) &nbsp;·&nbsp; Blue rows = CPI-affecting changes &nbsp;·&nbsp; 💾 Save / 📂 Load to persist across sessions`,
    infobar: [
      `🏷️ Change <strong>New Tag</strong> to simulate retagging — CPI updates instantly.`,
      `📊 Tags that count toward CPI: <strong>Core (C), Dept Elective (D), STEM (SE), HASMED (HE)</strong>.`,
      `📋 Check your curriculum for minimum credits per tag (example varies by department).`,
      `⚠️ Min <strong>18 credits/sem</strong> required. Retagging allowed <strong>twice</strong> per program (pre-placement &amp; post-curriculum).`,
      `💾 <strong>Save</strong> exports state as JSON &nbsp;·&nbsp; 📂 <strong>Load</strong> restores a saved file &nbsp;·&nbsp; 📊 <strong>Summary</strong> shows the full retag report.`,
    ],
    tagMeta: {
      C:  {label:"Core Course",               short:"Core",   color:"#e05260", counts:true },
      D:  {label:"Department Elective",       short:"Dept E", color:"#f07d3a", counts:true },
      SE: {label:"STEM Elective",             short:"STEM",   color:"#4ca4e0", counts:true },
      HE: {label:"HASMED Elective",           short:"HSMD",   color:"#9b63d8", counts:true },
      M:  {label:"Minor Course",              short:"Minor",  color:"#2db58e", counts:false},
      T:  {label:"Additional Learning (ALC)", short:"ALC",    color:"#8a9bae", counts:false},
      O:  {label:"Honors Course",             short:"Honors", color:"#c9a227", counts:false},
      E:  {label:"Honors Elective",           short:"Hon. E", color:"#b08040", counts:false},
      N:  {label:"Non-credit",               short:"N/A",    color:"#555555", counts:false},
    },
    transitions: {
      T:["D","SE","HE","O","E","M"], C:[], D:["T","O","E"],
      SE:["T"], HE:["T"], O:["T","D","E"], E:["T","D","O"], M:["T","SE","HE"], N:[],
    },
    initialData: () => window.INITIAL_DATA_UG,
  },
  mtech: {
    badge: "IIT Bombay · PG",
    footer: `PG mode &nbsp;·&nbsp; Blue rows = CPI-affecting changes &nbsp;·&nbsp; 💾 Save / 📂 Load to persist across sessions`,
    infobar: [
      `🏷️ Change <strong>New Category</strong> to simulate how re-categorising coursework changes CPI credits and CPI.`,
      `📚 Audit is limited to one per semester (with instructor consent).`,
      `💾 <strong>Save</strong> exports state as JSON &nbsp;·&nbsp; 📂 <strong>Load</strong> restores a saved file &nbsp;·&nbsp; 📊 <strong>Summary</strong> shows the full report.`,
    ],
    tagMeta: {
      C:   {label:"Core Course",               short:"Core",   color:"#e05260", counts:true },
      E:   {label:"Elective",                  short:"Elect",  color:"#4ca4e0", counts:true },
      IE:  {label:"Institute Elective",        short:"InstE",  color:"#9b63d8", counts:true },
      LAB: {label:"Software Lab",              short:"Lab",    color:"#f07d3a", counts:true },
      SEM: {label:"Seminar",                   short:"Sem",    color:"#2db58e", counts:true },
      RND: {label:"R&D Project",               short:"R&D",    color:"#3ecf8e", counts:true },
      AL:  {label:"Additional Learning",       short:"ALC",    color:"#8a9bae", counts:false},
      AU:  {label:"Audit",                     short:"Audit",  color:"#555555", counts:false},
      PN:  {label:"PP/NP Course",              short:"P/NP",   color:"#c9a227", counts:false},
    },
    transitions: {
      C:["E","IE","AL","AU"],
      E:["C","IE","AL","AU"],
      IE:["C","E","AL","AU"],
      LAB:["C","E","IE","AL","AU"],
      SEM:["C","E","IE","AL","AU"],
      RND:["C","E","IE","AL","AU"],
      AL:["C","E","IE","LAB","SEM","RND","AU"],
      AU:["C","E","IE","AL"],
      PN:[],
    },
    initialData: () => window.INITIAL_DATA_MTECH,
  },
};

let programKey = window.INITIAL_PROGRAM || "ug";
let TAG_META = (PROGRAM_SCHEMAS[programKey]||PROGRAM_SCHEMAS.ug).tagMeta;
let TAG_TRANSITIONS = (PROGRAM_SCHEMAS[programKey]||PROGRAM_SCHEMAS.ug).transitions;

const GRADE_POINTS = {AA:10,AB:9,BB:8,BC:7,CC:6,CD:5,DD:4,FF:0,FR:0};
const GRADE_ORDER = ["AA","AB","BB","BC","CC","CD","DD","FF","FR","II","PP","NP","AU"];

const deepCopy = (obj) => JSON.parse(JSON.stringify(obj));

// ── State ─────────────────────────────────────────────────────────────────────
let data = deepCopy((PROGRAM_SCHEMAS[programKey]||PROGRAM_SCHEMAS.ug).initialData());
let _uid = 300;
const uid = () => `u${++_uid}`;
let collapsedSems = {};
let modalTargetSemId = null;

function setProgram(key, resetData=true) {
  const nextKey = PROGRAM_SCHEMAS[key] ? key : "ug";
  programKey = nextKey;
  TAG_META = PROGRAM_SCHEMAS[nextKey].tagMeta;
  TAG_TRANSITIONS = PROGRAM_SCHEMAS[nextKey].transitions;

  const badgeEl = document.getElementById("program-badge");
  if (badgeEl) badgeEl.textContent = PROGRAM_SCHEMAS[nextKey].badge;

  const infobarEl = document.getElementById("infobar-list");
  if (infobarEl) infobarEl.innerHTML = PROGRAM_SCHEMAS[nextKey].infobar.map(t => `<li>${t}</li>`).join("");

  const footerEl = document.getElementById("footer-text");
  if (footerEl) footerEl.innerHTML = PROGRAM_SCHEMAS[nextKey].footer;

  const sel = document.getElementById("program-select");
  if (sel) sel.value = nextKey;

  const disclaimerEl = document.getElementById("program-disclaimer");
  if (disclaimerEl) {
    if (nextKey === "ug") {
      disclaimerEl.innerHTML = `Disclaimer: This is by default for BTech Aerospace Engineering. You can edit or remove subjects as per your branch.`;
      disclaimerEl.style.display = "block";
    } else if (nextKey === "mtech") {
      disclaimerEl.innerHTML = `Disclaimer: This is by default for MTech CSE. You can edit or remove subjects as per your branch.`;
      disclaimerEl.style.display = "block";
    } else {
      disclaimerEl.textContent = "";
      disclaimerEl.style.display = "none";
    }
  }

  if (resetData) {
    data = deepCopy(PROGRAM_SCHEMAS[nextKey].initialData());
    collapsedSems = {};
    modalTargetSemId = null;
    closeModal("add-modal");
  }

  renderAll();
}

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
        <button class="sem-del-btn" onclick="event.stopPropagation(); deleteSemester('${sem.id}')" title="Delete semester">🗑</button>
        <span class="toggle-arrow" style="transform:rotate(${collapsed?"-90deg":"0deg"})">▾</span>
      </div>
    </div>
    <div class="sem-body${collapsed?" collapsed":""}">
      <div class="tbl-header">
        <span>CODE</span><span>COURSE NAME</span><span>CREDITS</span>
        <span>GRADE</span><span>ORIG ${programKey==="mtech"?"CAT":"TAG"}</span><span>NEW ${programKey==="mtech"?"CAT":"TAG"}</span><span></span>
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
  const gradeOpts=GRADE_ORDER.map(g=>
    `<option value="${g}"${c.grade===g?" selected":""}>${g}</option>`).join("");
  const origTagOpts=Object.entries(TAG_META).map(([k,v])=>
    `<option value="${k}"${c.tag===k?" selected":""}>${v.short}</option>`).join("");
  const newTagOpts=allOpts.map(t=>
    `<option value="${t}"${c.newTag===t?" selected":""}>${TAG_META[t]?.short??t}</option>`).join("");
  return `
  <div class="course-row${isChanged?" changed":""}" id="row-${c.id}">
    <input class="text-input code-input" value="${c.code}"
      onchange="updateCourse('${semId}','${c.id}','code',this.value.trim())">
    <input class="text-input name-input" value="${c.name}" title="${c.name}"
      onchange="updateCourse('${semId}','${c.id}','name',this.value.trim())">
    <input class="num-input" type="number" min="0" max="48" value="${c.credits}"
      onchange="updateCourse('${semId}','${c.id}','credits',+this.value)">
    <select class="sel" onchange="updateCourse('${semId}','${c.id}','grade',this.value)">${gradeOpts}</select>
    ${programKey==="mtech"
      ?`<select class="sel" onchange="updateCourse('${semId}','${c.id}','tag',this.value)">${origTagOpts}</select>`
      :tagBadge(c.tag)
    }
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
  if ((field==="code" || field==="name") && !val) {
    showToast(`✗ ${field==="code" ? "Course code" : "Course name"} cannot be empty.`, true);
    const semIdx=data.semesters.findIndex(s=>s.id===semId);
    const el=document.getElementById(`semblock-${semId}`);
    if(el) el.outerHTML=renderSemBlock(data.semesters[semIdx],semIdx);
    return;
  }
  if (field==="credits") {
    const n = Number(val);
    val = Number.isFinite(n) ? Math.max(0, n) : 0;
  }
  if (field==="newTag" && programKey==="mtech" && val==="AU") {
    const otherAuditCount = sem.courses.filter(x => x.id!==courseId && x.newTag==="AU").length;
    if (otherAuditCount >= 1) {
      showToast("✗ Only one Audit course per semester is allowed.", true);
      const semIdx=data.semesters.findIndex(s=>s.id===semId);
      const el=document.getElementById(`semblock-${semId}`);
      if(el) el.outerHTML=renderSemBlock(data.semesters[semIdx],semIdx);
      return;
    }
  }
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
function deleteSemester(semId) {
  const sem=data.semesters.find(s=>s.id===semId); if(!sem)return;
  if(!confirm(`Delete "${sem.name}"? This will remove all its courses.`)) return;
  data.semesters=data.semesters.filter(s=>s.id!==semId);
  delete collapsedSems[semId];
  if(modalTargetSemId===semId) { modalTargetSemId=null; closeModal("add-modal"); }
  renderSemesterContainer(); renderSPIRow(); updateTopbar();
  showToast(`✓ Deleted "${sem.name}"`);
}

// ── Add Course Modal ──────────────────────────────────────────────────────────
function openAddModal(semId) {
  modalTargetSemId=semId;
  document.getElementById("m-tag").innerHTML=Object.entries(TAG_META).map(([k,v])=>
    `<option value="${k}">${v.short} — ${v.label}</option>`).join("");
  document.getElementById("m-grade").innerHTML = GRADE_ORDER.map(g =>
    `<option value="${g}">${g}</option>`).join("");
  document.getElementById("m-code").value="";
  document.getElementById("m-name").value="";
  document.getElementById("m-credits").value=6;
  document.getElementById("m-grade").value="BB";
  document.getElementById("add-modal").style.display="flex";
}
function closeModal(id) { document.getElementById(id).style.display="none"; }
function submitAddCourse() {
  const code=document.getElementById("m-code").value.trim();
  const name=document.getElementById("m-name").value.trim();
  const tag=document.getElementById("m-tag").value;
  const credits=+document.getElementById("m-credits").value;
  const grade=document.getElementById("m-grade").value;
  if(!code||!name){showToast("✗ Please fill in Code and Name.", true);return;}
  const sem=data.semesters.find(s=>s.id===modalTargetSemId); if(!sem)return;
  if (programKey==="mtech" && tag==="AU") {
    const auditCount = sem.courses.filter(x => x.newTag==="AU").length;
    if (auditCount >= 1) { showToast("✗ Only one Audit course per semester is allowed.", true); return; }
  }
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
  renderSemesterContainer(); renderSPIRow(); updateTopbar();
}

// ── Save / Load ───────────────────────────────────────────────────────────────
function saveState() {
  const payload=JSON.stringify({version:3,savedAt:new Date().toISOString(),program:programKey,data},null,2);
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
      const loadedProgram = parsed.program || parsed.data?.program || parsed.programKey || "ug";
      const loaded=parsed.data||parsed;
      if(!loaded.semesters) throw new Error("Invalid file — missing semesters");
      setProgram(loadedProgram, false);
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
setProgram(programKey, false);
