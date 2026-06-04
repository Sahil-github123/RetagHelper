// ── HTML Import: Tag mapping from portal tag text → internal code ─────────────
const PORTAL_TAG_MAP = {
  "core course":         "C",
  "department elective": "D",
  "dept elective":       "D",
  "stem elective":       "SE",
  "se":                  "SE",
  "hasmed elective":     "HE",
  "he":                  "HE",
  "minor course":        "M",
  "minor":               "M",
  "honors course":       "O",
  "honours course":      "O",
  "honors elective":     "E",
  "honours elective":    "E",
  "additional learning": "T",
  "alc":                 "T",
  "institute elective":  "IE",   // best-effort mapping
  "non-credit":          "N",
  "audit":               "N",
};
function portalTagToCode(raw) {

    const k = raw
        .replace(/\s+/g, " ")
        .trim()
        .toLowerCase();

    return PORTAL_TAG_MAP[k] || "UNKNOWN";
}

// ── Graduation Requirements State ─────────────────────────────────────────────
let gradReqs = null; // null = not set; object when set

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
  IE: {label:"Institute Elective",        short:"IE",     color:"#6c8cff",counts:true}
};
const TAG_TRANSITIONS = {
  T:["D","SE","HE","O","E","M"], C:[], D:["T","O","E"],
  SE:["T"], HE:["T"], O:["T","D","E"], E:["T","D","O"], M:["T","SE","HE"], N:[],IE:["T","SE","D","HE","M","O","E"],
};
const GRADE_POINTS = {AA:10,AB:9,BB:8,BC:7,CC:6,CD:5,DD:4,FF:0,FR:0};
const flexTags = ["IE","D","SE","HE"];
// ── State ─────────────────────────────────────────────────────────────────────
let data = window.INITIAL_DATA;
let _uid = 300;
const uid = () => `u${++_uid}`;
let collapsedSems = {};
let modalTargetSemId = null;

// ── Calculations ──────────────────────────────────────────────────────────────
function calcSPI(courses, useNew) {
  let ws = 0;
  let tc = 0;

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

function getCurrentCredits() {
    const result = {
        core: 0,
        department: 0,
        stem: 0,
        hasmed: 0,
        flexible: 0
    };

    for (const sem of data.semesters) {
        for (const c of sem.courses) {

            const tag = c.newTag;

            if (GRADE_POINTS[c.grade] === undefined)
                continue;

            switch(tag) {
                case "C":
                    result.core += c.credits;
                    break;

                case "D":
                    result.department += c.credits;
                    break;

                case "SE":
                    result.stem += c.credits;
                    break;

                case "HE":
                    result.hasmed += c.credits;
                    break;

                case "IE":
                    result.flexible += c.credits;
                    break;
            }
        }
    }

    return result;
}


function getRemainingCredits() {

    if (!gradReqs)
        return null;

    const current = getCurrentCredits();

    return {
        core: Math.max(0, gradReqs.core - current.core),
        department: Math.max(0, gradReqs.department - current.department),
        stem: Math.max(0, gradReqs.stem - current.stem),
        hasmed: Math.max(0, gradReqs.hasmed - current.hasmed),
        flexible: Math.max(0, gradReqs.flexible - current.flexible)
    };
}



const DEFAULT_GRAD_REQS = {
  core:       { label: "Core (C)",           tag: "C",  required: 156 },
  hasmed:     { label: "HASMED (HE)",        tag: "HE", required: 12  },
  stem:       { label: "STEM (SE)",          tag: "SE", required: 12  },
  department: { label: "Department (D)",     tag: "D",  required: 36  },
  flexible:   { label: "Flexible (T/other)", tag: null, required: 36  },
};

function calcGradProgress() {
  const reqs = gradReqs || DEFAULT_GRAD_REQS;
  const tagTotals = {}; // tag → credits (using newTag)
  let totalCredits = 0;
  for (const sem of data.semesters) {
    for (const c of sem.courses) {
      if (!TAG_META[c.newTag]?.counts && c.newTag !== "T") continue;
      const gp = GRADE_POINTS[c.grade];
      if (gp === undefined) continue;
      tagTotals[c.newTag] = (tagTotals[c.newTag] || 0) + c.credits;
      totalCredits += c.credits;
    }
  }
  // "Flexible" = everything that counts but isn't C/D/SE/HE
  const flexTags = Object.keys(TAG_META).filter(t => !["C","D","SE","HE"].includes(t) && TAG_META[t].counts);
  const flexCredits = flexTags.reduce((s, t) => s + (tagTotals[t] || 0), 0);

  const rows = [];
  for (const [key, req] of Object.entries(reqs)) {
    const earned = req.tag ? (tagTotals[req.tag] || 0) : flexCredits;
    const remaining = Math.max(0, req.required - earned);
    rows.push({ key, label: req.label, required: req.required, earned, remaining });
  }
  return rows;
}

function openGradModal() {
  const reqs = gradReqs || DEFAULT_GRAD_REQS;
  document.getElementById("grad-core").value    = reqs.core.required;
  document.getElementById("grad-hasmed").value  = reqs.hasmed.required;
  document.getElementById("grad-stem").value    = reqs.stem.required;
  document.getElementById("grad-dept").value    = reqs.department.required;
  document.getElementById("grad-flex").value    = reqs.flexible.required;
  document.getElementById("grad-modal").style.display = "flex";
  renderGradProgress();
}
function saveGradReqs() {
  gradReqs = {
    core:       { label: "Core (C)",           tag: "C",  required: +document.getElementById("grad-core").value   || 156 },
    hasmed:     { label: "HASMED (HE)",        tag: "HE", required: +document.getElementById("grad-hasmed").value || 12  },
    stem:       { label: "STEM (SE)",          tag: "SE", required: +document.getElementById("grad-stem").value   || 12  },
    department: { label: "Department (D)",     tag: "D",  required: +document.getElementById("grad-dept").value   || 36  },
    flexible:   { label: "Flexible (T/other)", tag: null, required: +document.getElementById("grad-flex").value   || 36  },
  };
  renderGradProgress();
  closeModal("grad-modal");
  renderCreditStrip();
  updateTopbar();
  showToast("✓ Graduation requirements updated!");

}
function renderGradProgress() {
  const rows = calcGradProgress();

  const current = getCurrentCredits();
  const remaining = getRemainingCredits();
  const totalReq  = rows.reduce((s,r) => s + r.required, 0);
  const totalEarn = rows.reduce((s,r) => s + r.earned, 0);
  const totalRem  = rows.reduce((s,r) => s + r.remaining, 0);

  const barHtml = rows.map(r => {
    const pct = Math.min(100, Math.round((r.earned / r.required) * 100));
    const done = r.remaining === 0;
    const barColor = done ? "var(--green)" : r.earned > 0 ? "var(--amber)" : "var(--red)";
    return `
    <div class="grad-row">
      <div class="grad-label">${r.label}</div>
      <div class="grad-bar-wrap">
        <div class="grad-bar-bg">
          <div class="grad-bar-fill" style="width:${pct}%;background:${barColor}"></div>
        </div>
        <span class="grad-bar-pct" style="color:${barColor}">${pct}%</span>
      </div>
      <div class="grad-nums">
        <span style="color:${done?'var(--green)':'var(--text)'}">
          ${r.earned} / ${r.required} cr
        </span>
        ${done
          ? `<span class="grad-done">✓ Done</span>`
          : `<span class="grad-need" style="color:var(--amber)">Need ${r.remaining} more cr</span>`}
      </div>
    </div>`;
  }).join("");

  const totalHtml = `
  <div class="grad-total-row">
    <span>Total:</span>
    <span style="font-weight:800;color:${totalRem===0?'var(--green)':'var(--amber)'}">
      ${totalEarn} / ${totalReq} credits
    </span>
    <span style="color:${totalRem===0?'var(--green)':'var(--amber)'}">
      ${totalRem===0 ? "🎓 All requirements met!" : `${totalRem} credits remaining`}
    </span>
  </div>`;

  const body = document.getElementById("grad-body");
  if (body) body.innerHTML = barHtml + totalHtml;
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

};

const items = allTags.map(tag => {

    const m = TAG_META[tag];
    if (!m) return "";

    const earned = newTags[tag] || 0;

    const req = reqMap[tag];

    let progressText = `${earned} cr`;

    if (req) {
        progressText =
            `${earned}/${req.required}`;

        if (req.remaining === 0)
            progressText += ` ✓`;
        else
            progressText += ` (-${req.remaining})`;
    }

    return `
    <div class="cstrip-item">
      <span class="cstrip-badge"
            style="background:${m.color}22;
                   color:${m.color};
                   border:1px solid ${m.color}44">
          ${m.short}
      </span>

      <span class="cstrip-cr">${progressText}</span>
    </div>`;
});





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
  renderGradProgress();
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

// ── HTML Portal Import ────────────────────────────────────────────────────────
function parsePortalHTML(htmlText) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(htmlText, "text/html");

  // Find the "Semester-wise Details" section header
  const semDetailAnchor = doc.querySelector('a[name="semDetails"]');
  if (!semDetailAnchor) {
    showToast("✗ Could not find 'Semester-wise Details' section in the HTML.", true);
    return null;
  }

  const semesters = [];
  let ctr = 0;
  // Walk sibling nodes after the anchor to find all h3 + table pairs
  let node = semDetailAnchor.parentElement ? semDetailAnchor.parentElement.nextElementSibling : null;
  // Fallback: search the whole doc for h3 elements containing Year/Semester
  const allH3 = Array.from(doc.querySelectorAll("h3"));
  const semH3s = allH3.filter(h => /Year\/Semester/.test(h.textContent));

  if (semH3s.length === 0) {
    showToast("✗ No semester headings (Year/Semester: ...) found.", true);
    return null;
  }

  // Semesters in portal are listed newest-first; we'll reverse to chronological
  const semBlocksRaw = [];
  for (const h3 of semH3s) {
    const titleMatch = h3.textContent.match(/(\d{4}(?:-\d{2})?)[\/\s]+(Autumn|Spring|Summer)/i);
    let semName = h3.textContent.replace(/Year\/Semester:\s*/i, "").trim();
    // Normalise: "2023-24/Autumn" → "Autumn 2023"
    if (titleMatch) {
      const yr = titleMatch[1].split("-")[0];
      const season = titleMatch[2];
      semName = `${season} ${yr}`;
    }
    // Find the nearest following table
    let sib = h3.nextElementSibling;

    while (
        sib &&
        (
            sib.tagName !== "TABLE" ||
            sib.querySelectorAll("tr").length < 2
        )
    ) {
        sib = sib.nextElementSibling;
    }
    
    if (!sib) continue;

    const courses = [];
    const rows = sib.querySelectorAll("tr");
    for (const row of rows) {
      const cells = Array.from(row.querySelectorAll("td"));
      if (cells.length < 5) continue;
      const code = cells[0].textContent.replace(/\(.*?\)/g, "").trim();
      const name = cells[1].childNodes[0]?.textContent?.trim() || cells[1].textContent.trim();
      const credits = parseFloat(cells[2].textContent.trim()) || 0;
      const tagRaw = cells[3].textContent.trim();
      const grade = cells[4].textContent.trim().toUpperCase();
      if (!code || !name || !grade) continue;
      const tagCode = portalTagToCode(tagRaw);
      const creditAudit = cells[5]?.textContent?.trim() || "C";
      // N/audit courses
      const finalTag = (creditAudit === "N" || grade === "PP" && credits === 0) ? "N" : tagCode;
      courses.push({ id: uid(), code, name, tag: finalTag, newTag: finalTag, credits, grade: grade || "PP" });
    }
    if (courses.length > 0) semBlocksRaw.push({ semName, courses });
  }

  if (semBlocksRaw.length === 0) {
    showToast("✗ No courses found in the HTML. Are you uploading the right page?", true);
    return null;
  }

  // Reverse so oldest semester comes first (portal shows newest first)
  semBlocksRaw.reverse();
  const result = semBlocksRaw.map((b, i) => ({
    id: uid(),
    name: b.semName || `Semester ${i + 1}`,
    courses: b.courses,
  }));
  return result;
}

function importFromPortalHTML(event) {
  const file = event.target.files[0]; if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    const parsed = parsePortalHTML(e.target.result);
    if (!parsed) return;
    // Ask user: replace or merge?
    const replace = confirm(
      `Found ${parsed.length} semesters with courses from the portal HTML.\n\n` +
      `Click OK to REPLACE current data, or Cancel to MERGE (add semesters that don't already exist).`
    );
    if (replace) {
      data = { semesters: parsed };
      collapsedSems = {};
    } else {
      // Merge: only add semesters whose names don't already exist
      const existingNames = new Set(data.semesters.map(s => s.name.toLowerCase()));
      let added = 0;
      for (const s of parsed) {
        if (!existingNames.has(s.name.toLowerCase())) {
          data.semesters.push(s);
          added++;
        }
      }
      showToast(`✓ Merged: added ${added} new semester(s).`);
    }
    renderAll();
    if (replace) showToast(`✓ Imported ${parsed.length} semesters from portal HTML!`);
  };
  reader.readAsText(file);
  event.target.value = "";
}

// ── Graduation Requirements ───────────────────────────────────────────────────
// Default profile for IIT Bombay AE B.Tech (user can override in the modal)

// ── Boot ──────────────────────────────────────────────────────────────────────
renderAll();
