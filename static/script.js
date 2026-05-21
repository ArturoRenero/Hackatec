
/* =========================================================
   UI V2: ventanas emergentes, loader global y toasts.
   No cambia la lógica del backend, solo feedback visual.
   ========================================================= */
function showLoader(title = "Analizando documento...", msg = "Verificando datos y comparando información. Espera un momento.") {
  const loader = document.getElementById("globalLoader");
  if (!loader) return;
  document.getElementById("loaderTitle").textContent = title;
  document.getElementById("loaderMsg").textContent = msg;
  loader.classList.add("show");
  loader.setAttribute("aria-hidden", "false");
}

function hideLoader() {
  const loader = document.getElementById("globalLoader");
  if (!loader) return;
  loader.classList.remove("show");
  loader.setAttribute("aria-hidden", "true");
}

function showToast(type, title, msg) {
  const stack = document.getElementById("toastStack");
  if (!stack) return;
  const toast = document.createElement("div");
  toast.className = `vm-toast ${type === "ok" ? "ok" : "bad"}`;
  toast.innerHTML = `<div class="vm-ticon">${type === "ok" ? "✅" : "⚠️"}</div><div><strong>${title}</strong><span>${msg}</span></div>`;
  stack.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(28px) scale(.96)";
    setTimeout(() => toast.remove(), 240);
  }, 4200);
}

function showModal(type, title, msg) {
  const modal = document.getElementById("resultModal");
  if (!modal) return;
  const card = modal.querySelector(".vm-modal-card");
  card.classList.remove("ok", "bad");
  card.classList.add(type === "ok" ? "ok" : "bad");
  document.getElementById("modalIcon").textContent = type === "ok" ? "✓" : "!";
  document.getElementById("modalTitle").textContent = title;
  document.getElementById("modalText").textContent = msg;
  modal.classList.add("show");
  modal.setAttribute("aria-hidden", "false");
}

function hideModal() {
  const modal = document.getElementById("resultModal");
  if (!modal) return;
  modal.classList.remove("show");
  modal.setAttribute("aria-hidden", "true");
}

window.addEventListener("DOMContentLoaded", () => {
  document.body.classList.add("vm-v2");
  showToast("ok", "Sistema listo", "La interfaz de validación está preparada para analizar documentos.");
});

const API = "";

/* ── Navigation ── */
function go(s) {
  ["ine", "curp", "extraer"].forEach((x) => {
    document.getElementById("sec-" + x).style.display = x === s ? "" : "none";
    document.getElementById("nav-" + x).classList.toggle("active", x === s);
  });
}

/* ── Extraction state ── */
const extractFiles = []; // {id, file, status, curps}

function fmtSize(b) {
  if (b < 1024) return b + "B";
  if (b < 1048576) return (b / 1024).toFixed(1) + "KB";
  return (b / 1048576).toFixed(1) + "MB";
}

function fileExt(name) {
  return name.split(".").pop().toLowerCase();
}

function dzDragOver(e) {
  e.preventDefault();
  document.getElementById("dropZone").classList.add("dragover");
}
function dzDragLeave() {
  document.getElementById("dropZone").classList.remove("dragover");
}
function dzDrop(e) {
  e.preventDefault();
  document.getElementById("dropZone").classList.remove("dragover");
  addFiles(e.dataTransfer.files);
}

function addFiles(files) {
  Array.from(files).forEach((f) => {
    const id = "f" + Date.now() + Math.random().toString(36).slice(2, 6);
    extractFiles.push({ id, file: f, status: "pending", curps: [] });
    renderFileItem({ id, file: f, status: "pending", curps: [] });
  });
  document.getElementById("fileQueue").style.display = extractFiles.length
    ? ""
    : "none";
  document.getElementById("bextract").style.display = extractFiles.length
    ? ""
    : "none";
  document.getElementById("bextract").disabled = false;
  document.getElementById("bextract").classList.add("ready");
  document.getElementById("docInput").value = "";
}

function renderFileItem(item) {
  const list = document.getElementById("fileList");
  const ext = fileExt(item.file.name);
  const isPdf = ext === "pdf";
  const isImg = [
    "jpg",
    "jpeg",
    "png",
    "webp",
    "bmp",
    "tiff",
    "gif",
    "heic",
  ].includes(ext);

  const el = document.createElement("div");
  el.className = "file-item";
  el.id = "fi-" + item.id;
  el.innerHTML = `
    <div class="file-thumb ${isPdf ? "is-pdf" : isImg ? "" : "is-doc"}" id="ft-${item.id}">
      ${isPdf ? "PDF" : isImg ? "" : ext.toUpperCase()}
    </div>
    <div class="file-info">
      <div class="file-name">${item.file.name}</div>
      <div class="file-size">${fmtSize(item.file.size)}</div>
    </div>
    <span class="file-status pending" id="fs-${item.id}">Pendiente</span>
    <button class="file-remove" onclick="removeFile('${item.id}')" title="Quitar">
      <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2">
        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>`;
  list.appendChild(el);

  if (isImg) {
    const rd = new FileReader();
    rd.onload = (e) => {
      const t = document.getElementById("ft-" + item.id);
      if (t) {
        t.innerHTML = `<img src="${e.target.result}" alt="" />`;
      }
    };
    rd.readAsDataURL(item.file);
  }
}

function setFileStatus(id, status, label) {
  const el = document.getElementById("fs-" + id);
  if (!el) return;
  el.className = "file-status " + status;
  el.textContent = label;
}

function removeFile(id) {
  const idx = extractFiles.findIndex((f) => f.id === id);
  if (idx > -1) extractFiles.splice(idx, 1);
  const el = document.getElementById("fi-" + id);
  if (el) el.remove();
  if (!extractFiles.length) {
    document.getElementById("fileQueue").style.display = "none";
    document.getElementById("bextract").style.display = "none";
    document.getElementById("extractSummary").style.display = "none";
    document.getElementById("extractResults").innerHTML = "";
  }
}

function clearAll() {
  extractFiles.length = 0;
  document.getElementById("fileList").innerHTML = "";
  document.getElementById("fileQueue").style.display = "none";
  document.getElementById("bextract").style.display = "none";
  document.getElementById("extractSummary").style.display = "none";
  document.getElementById("extractResults").innerHTML = "";
}

/* CURP regex — 18 chars strict */
const CURP_RE = /\b[A-Z]{4}\d{6}[HM][A-Z]{2}[A-Z]{3}[A-Z0-9]\d\b/g;

function extractCURPsFromText(text) {
  const matches = [...text.toUpperCase().matchAll(CURP_RE)];
  return [...new Set(matches.map((m) => m[0]))];
}

/* Read file as text or base64 */
function readFileText(file) {
  return new Promise((res) => {
    const r = new FileReader();
    r.onload = (e) => res(e.target.result);
    r.readAsText(file);
  });
}
function readFileB64(file) {
  return new Promise((res) => {
    const r = new FileReader();
    r.onload = (e) => res(e.target.result.split(",")[1]);
    r.readAsDataURL(file);
  });
}

async function extractFromFile(item) {
  const ext = fileExt(item.file.name);
  const isImg = [
    "jpg",
    "jpeg",
    "png",
    "webp",
    "bmp",
    "tiff",
    "gif",
    "heic",
  ].includes(ext);
  const isTxt = ["txt", "csv", "html", "json", "xml"].includes(ext);

  setFileStatus(item.id, "scanning", "Analizando…");

  try {
    let curps = [];

    if (isTxt) {
      const text = await readFileText(item.file);
      curps = extractCURPsFromText(text);
    } else if (isImg || ext === "pdf") {
      /* Send to backend OCR endpoint */
      const fd = new FormData();
      fd.append("archivo", item.file);
      const res = await fetch(API + "/api/extraer-curp", {
        method: "POST",
        body: fd,
      });
      if (res.ok) {
        const json = await res.json();
        curps = json.curps || [];
        /* Also try regex on any raw text returned */
        if (json.texto_raw)
          curps = [
            ...new Set([...curps, ...extractCURPsFromText(json.texto_raw)]),
          ];
      } else {
        /* Fallback: try regex on file name (edge case) */
        curps = extractCURPsFromText(item.file.name);
      }
    }

    item.curps = curps;
    item.status = curps.length ? "found" : "notfound";
    setFileStatus(
      item.id,
      item.status,
      curps.length
        ? `${curps.length} CURP${curps.length > 1 ? "s" : ""} encontrada${curps.length > 1 ? "s" : ""}`
        : "Sin CURP",
    );
    return curps;
  } catch (e) {
    item.status = "notfound";
    setFileStatus(item.id, "notfound", "Error al leer");
    return [];
  }
}

async function doExtract() {
  if (!extractFiles.length) return;

  const btn = document.getElementById("bextract");
  btn.disabled = true;
  showLoader("Extrayendo CURP...", "Analizando archivos con OCR. Esto puede tardar unos segundos.");
  btn.classList.add("loading");
  btn.classList.remove("ready");
  document.getElementById("eico").style.display = "none";
  document.getElementById("elbl").textContent = "Extrayendo…";
  document.getElementById("extractResults").innerHTML = "";
  document.getElementById("extractSummary").style.display = "none";

  /* Reset all statuses */
  extractFiles.forEach((f) => {
    f.curps = [];
    f.status = "pending";
    setFileStatus(f.id, "pending", "En espera…");
  });

  /* Process sequentially */
  for (const item of extractFiles) {
    await extractFromFile(item);
    renderExtractResult(item);
  }

  /* Summary */
  const found = extractFiles.filter((f) => f.curps.length > 0);
  const none = extractFiles.filter((f) => f.curps.length === 0);
  const allCurps = [...new Set(extractFiles.flatMap((f) => f.curps))];

  document.getElementById("sTotal").textContent = extractFiles.length;
  document.getElementById("sFound").textContent = found.length;
  document.getElementById("sNone").textContent = none.length;
  document.getElementById("sUnique").textContent = allCurps.length;
  document.getElementById("extractSummary").style.display = "";
  document.getElementById("exportBtn").style.display = allCurps.length
    ? ""
    : "none";

  btn.disabled = false;
  btn.classList.remove("loading");
  btn.classList.add("ready");
  document.getElementById("eico").style.display = "";
  document.getElementById("elbl").textContent = "Volver a extraer";
  document.getElementById("espinner").style.display = "none";
  hideLoader();
  showModal(allCurps.length ? "ok" : "bad", allCurps.length ? "Extracción completada" : "No se encontraron CURP", allCurps.length ? `Se encontraron ${allCurps.length} CURP única(s) en los documentos.` : "No se detectó ninguna CURP válida en los archivos cargados.");
  showToast(allCurps.length ? "ok" : "bad", "Extracción finalizada", allCurps.length ? `${allCurps.length} CURP única(s) encontrada(s).` : "No hubo coincidencias válidas.");
}

function renderExtractResult(item) {
  const results = document.getElementById("extractResults");
  const el = document.createElement("div");
  el.className = "extract-item";

  const hasCurps = item.curps.length > 0;
  const iconOk = `<svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="var(--green)" stroke-width="2.2"><polyline points="20 6 9 17 4 12"/></svg>`;
  const iconBad = `<svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="var(--muted2)" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`;

  const curpChips = item.curps
    .map(
      (c) => `
    <div class="curp-found">
      <span class="curp-chip">${c}</span>
      <div class="curp-actions">
        <button class="act-btn" onclick="copyCurp('${c}',this)" title="Copiar">
          <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
          </svg>
          Copiar
        </button>
        <button class="act-btn green" onclick="validarEsta('${c}')" title="Validar contra RENAPO">
          <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
          Validar
        </button>
      </div>
    </div>`,
    )
    .join("");

  el.innerHTML = `
    <div class="extract-head">
      <div style="width:26px;height:26px;border-radius:7px;display:flex;align-items:center;justify-content:center;background:${hasCurps ? "var(--green-dim)" : "var(--surface3)"};border:1px solid ${hasCurps ? "var(--green)40" : "var(--border2)"}">
        ${hasCurps ? iconOk : iconBad}
      </div>
      <span class="extract-filename">${item.file.name}</span>
      ${
        hasCurps
          ? `<span class="badge-ok">${item.curps.length} CURP${item.curps.length > 1 ? "s" : ""}</span>`
          : `<span style="font-size:11px;color:var(--muted2);font-family:var(--mono)">Sin CURP</span>`
      }
    </div>
    <div class="extract-body">
      ${
        hasCurps
          ? `<div style="display:flex;flex-direction:column;gap:10px">${curpChips}</div>`
          : `<p class="no-curp">No se encontró ninguna CURP válida en este archivo.</p>`
      }
    </div>`;

  results.appendChild(el);
}

function copyCurp(curp, btn) {
  navigator.clipboard.writeText(curp).then(() => {
    const orig = btn.innerHTML;
    btn.innerHTML = `<svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="var(--green-txt)" stroke-width="2.2"><polyline points="20 6 9 17 4 12"/></svg> Copiado`;
    btn.style.color = "var(--green-txt)";
    setTimeout(() => {
      btn.innerHTML = orig;
      btn.style.color = "";
    }, 1800);
  });
}

function validarEsta(curp) {
  go("curp");
  const inp = document.getElementById("ci");
  inp.value = curp;
  onCurpInput(inp);
  setTimeout(() => doCURP(), 100);
}

function exportCSV() {
  const allCurps = [...new Set(extractFiles.flatMap((f) => f.curps))];
  const rows = [["CURP", "Archivo"]];
  extractFiles.forEach((f) =>
    f.curps.forEach((c) => rows.push([c, f.file.name])),
  );
  const csv = rows
    .map((r) => r.map((v) => `"${v.replace(/"/g, '""')}"`).join(","))
    .join("\n");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(
    new Blob([csv], { type: "text/csv;charset=utf-8;" }),
  );
  a.download = "curps_extraidas.csv";
  a.click();
}

/* ── CURP counter ── */
function onCurpInput(el) {
  el.value = el.value.toUpperCase();
  const n = el.value.length;
  const lenEl = document.getElementById("curp-len");
  lenEl.textContent = n + "/18";
  lenEl.classList.toggle("ok", n === 18);
  document.getElementById("bcurp").disabled = n !== 18;
}

/* ── File picker ── */
const fileObjs = {};

function pick(side, input) {
  const f = input.files[0];
  if (!f) return;
  fileObjs[side] = f;

  const zid = side === "front" ? "zf" : "zb";
  document.getElementById(zid).classList.add("done");
  const short = f.name.length > 24 ? f.name.slice(0, 22) + "…" : f.name;
  document.getElementById(side === "front" ? "ft" : "bt").textContent =
    side === "front" ? "Frente cargado" : "Reverso cargado";
  document.getElementById(side === "front" ? "fs" : "bs").textContent = short;

  if (!f.type.includes("pdf")) {
    const tid = side === "front" ? "tf" : "tb";
    const rd = new FileReader();
    rd.onload = (e) => {
      document.getElementById(tid).src = e.target.result;
    };
    rd.readAsDataURL(f);
  }

  updateSteps();

  if (fileObjs.front) {
    const btn = document.getElementById("bine");
    btn.disabled = false;
    btn.classList.add("ready");
  }
}

function updateSteps() {
  const s1 = document.getElementById("step1");
  const s2 = document.getElementById("step2");
  const l1 = document.getElementById("line1");
  if (fileObjs.front || fileObjs.back) {
    s1.classList.add("done");
    s1.classList.remove("active");
    s2.classList.add("active");
    l1.classList.add("done");
  }
}

/* ── Loading state ── */
function setLoading(on) {
  const btn = document.getElementById("bine");
  btn.disabled = on;
  btn.classList.toggle("loading", on);
  btn.classList.toggle("ready", !on && !!fileObjs.front);

  const s2 = document.getElementById("step2");
  const l2 = document.getElementById("line2");
  const s3 = document.getElementById("step3");

  if (on) {
    s2.classList.add("active");
    document.getElementById("iico").style.display = "none";
    document.getElementById("ilbl").textContent = "Procesando…";
  } else {
    document.getElementById("iico").style.display = "";
    document.getElementById("ilbl").textContent = "Validar INE";
  }
}

function finishSteps(ok) {
  const s2 = document.getElementById("step2");
  const s3 = document.getElementById("step3");
  const l2 = document.getElementById("line2");
  s2.classList.remove("active");
  s2.classList.add("done");
  s3.classList.add(ok ? "done" : "active");
  l2.classList.toggle("done", ok);
}

/* ── Error display ── */
function showError(container, msg) {
  document.getElementById(container).innerHTML = `
    <div class="errcard">
      <div class="errcard-body">
        <div class="errcard-icon">
          <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="var(--red-txt)" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <div class="errcard-text">
          <div class="errcard-title">Error en la validación</div>
          <div class="errcard-msg">${msg}</div>
        </div>
      </div>
    </div>`;
}

/* ── INE ── */
async function doINE() {
  if (!fileObjs.front) return;

  setLoading(true);
  showLoader("Validando INE...", "Escaneando documento, leyendo OCR y consultando la validación.");
  document.getElementById("ir").innerHTML = "";

  const fd = new FormData();
  fd.append("frente", fileObjs.front);
  fd.append("reverso", fileObjs.back || fileObjs.front);

  try {
    const res = await fetch(API + "/api/validar-ine", {
      method: "POST",
      body: fd,
    });
    const json = await res.json();

    if (json.error) {
      showError("ir", json.mensaje || json.detalle || "Error desconocido.");
      showModal("bad", "Validación no exitosa", json.mensaje || json.detalle || "No fue posible validar la INE.");
      showToast("bad", "Validación no exitosa", "Revisa el archivo o intenta con una imagen más clara.");
      finishSteps(false);
      return;
    }

    const interp = json.interpretacion || {};
    const datos = interp.datos_extraidos || {};
    const nominal = interp.lista_nominal;

    const badge = nominal
      ? `<span class="badge-ok">Lista nominal vigente</span>`
      : `<span class="badge-bad">No encontrado en lista nominal</span>`;

    const MAP = {
      fullName: "Nombre completo",
      curp: "CURP",
      birthDate: "Fecha de nacimiento",
      expirationDate: "Vencimiento",
      electorKey: "Clave de elector",
      gender: "Sexo",
      address: "Dirección",
    };

    const fields = Object.entries(MAP)
      .filter(([k]) => datos[k])
      .map(([k, label]) => {
        const full = ["address", "fullName"].includes(k) ? " full" : "";
        return `<div class="rf${full}"><label>${label}</label><span>${datos[k]}</span></div>`;
      })
      .join("");

    const extraFields = Object.entries(datos)
      .filter(([k]) => !MAP[k] && datos[k])
      .map(
        ([k, v]) =>
          `<div class="rf"><label>${k}</label><span>${v}</span></div>`,
      )
      .join("");

    document.getElementById("ir").innerHTML = `
      <div class="rcard">
        <div class="rhead">
          <div class="rhead-left">
            <div class="rhead-icon ${nominal ? "ok" : "bad"}">
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="${nominal ? "var(--green)" : "var(--red-txt)"}" stroke-width="2">
                ${
                  nominal
                    ? '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/>'
                    : '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>'
                }
              </svg>
            </div>
            <div>
              <div class="rhead-title">Datos extraídos por OCR</div>
              <div class="rhead-sub">${interp.mensaje || "Verificación completada"}</div>
            </div>
          </div>
          ${badge}
        </div>
        <div class="rbody">${
          fields ||
          extraFields ||
          '<div class="rf full"><label>Respuesta</label><span>Sin datos estructurados</span></div>'
        }</div>
      </div>`;

    finishSteps(nominal);
    showModal(nominal ? "ok" : "bad", nominal ? "Documento válido" : "Documento no validado", interp.mensaje || (nominal ? "La INE fue encontrada como vigente en la lista nominal." : "No se encontró coincidencia vigente en la lista nominal."));
    showToast(nominal ? "ok" : "bad", nominal ? "Validación exitosa" : "Validación no exitosa", interp.mensaje || "Proceso finalizado.");
  } catch (err) {
    showError(
      "ir",
      "No se pudo conectar con el servidor Python. ¿Está corriendo server.py?",
    );
    showModal("bad", "Servidor no disponible", "No se pudo conectar con el servidor Python. Revisa que server.py esté corriendo.");
    showToast("bad", "Error de conexión", "No se pudo conectar con el servidor Python.");
    finishSteps(false);
    console.error(err);
  } finally {
    setLoading(false);
    hideLoader();
  }
}

/* ── CURP ── */
async function doCURP() {
  const val = document.getElementById("ci").value.trim().toUpperCase();
  document.getElementById("cr").innerHTML = "";
  if (val.length !== 18) return;

  const btn = document.getElementById("bcurp");
  btn.disabled = true;
  btn.textContent = "Validando…";
  showLoader("Validando CURP...", "Consultando y verificando la clave capturada.");

  try {
    const res = await fetch(API + "/api/validar-curp", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ curp: val }),
    });
    const json = await res.json();

    if (json.error) {
      showError("cr", json.mensaje || "Error desconocido.");
      showModal("bad", "CURP no validada", json.mensaje || "No fue posible validar la CURP.");
      showToast("bad", "Validación no exitosa", "Revisa la CURP e intenta nuevamente.");
      return;
    }

    const interp = json.interpretacion || {};
    const ok = interp.valida;
    const badge = ok
      ? `<span class="badge-ok">CURP válida en RENAPO</span>`
      : `<span class="badge-bad">No encontrada en RENAPO</span>`;

    let body = "";
    if (interp.nombre || interp.sexo || interp.fecha_nacimiento) {
      body = `<div class="cbody">
        ${interp.nombre ? `<div class="rf"><label>Nombre</label><span>${interp.nombre}</span></div>` : ""}
        ${interp.sexo ? `<div class="rf"><label>Sexo</label><span>${interp.sexo}</span></div>` : ""}
        ${interp.fecha_nacimiento ? `<div class="rf"><label>Nacimiento</label><span>${interp.fecha_nacimiento}</span></div>` : ""}
        ${interp.entidad ? `<div class="rf"><label>Entidad</label><span>${interp.entidad}</span></div>` : ""}
        ${interp.status_curp ? `<div class="rf"><label>Status</label><span>${interp.status_curp}</span></div>` : ""}
        ${interp.mensaje ? `<div class="rf"><label>Mensaje</label><span>${interp.mensaje}</span></div>` : ""}
      </div>`;
    } else {
      body = `<div style="padding:14px 18px;font-size:13px;color:var(--muted2)">${interp.mensaje || "Sin información adicional."}</div>`;
    }

    document.getElementById("cr").innerHTML = `
      <div class="ccard">
        <div class="chead">
          <div>
            <div style="font-size:11px;color:var(--muted2);margin-bottom:4px;font-weight:600;letter-spacing:.06em;text-transform:uppercase">CURP consultada</div>
            <span class="cval">${val}</span>
          </div>
          ${badge}
        </div>
        ${body}
      </div>`;
  } catch (err) {
    showError(
      "cr",
      "No se pudo conectar con el servidor Python. ¿Está corriendo server.py?",
    );
    console.error(err);
    showModal("bad", "Error de conexión", "No se pudo conectar con el servidor Python.");
    showToast("bad", "Error de conexión", "Revisa que server.py esté activo.");
  } finally {
    hideLoader();
    btn.disabled = false;
    btn.textContent = "Validar";
  }
}
