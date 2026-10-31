// THE BRIEF — Scriptable para iPad (widget mediano)
// Instala este archivo en Scriptable. Los titulares se leen de noticias.json.
const BASE = "https://raw.githubusercontent.com/urfab04/-the-brief/main/";
const REPORT_URL = "https://github.com/urfab04/-the-brief/blob/main/index.html";
const DATA_URL = BASE + "noticias.json";
const CACHE_KEY = "the-brief-noticias-cache.json";
const fm = FileManager.local();
const cachePath = fm.joinPath(fm.documentsDirectory(), CACHE_KEY);
const F = { bg: new Color("#101114"), panel: new Color("#1c1e23"), white: new Color("#f4f4f5"), muted: new Color("#a5a8b0"), silver: new Color("#c5c9d0") };
async function loadData() {
  try {
    const req = new Request(DATA_URL + "?t=" + Math.floor(Date.now() / 900000));
    req.timeoutInterval = 12;
    const data = await req.loadJSON();
    if (!data || !Array.isArray(data.secciones)) throw new Error("Formato inválido");
    fm.writeString(cachePath, JSON.stringify(data));
    return {data, cached:false};
  } catch (e) {
    if (fm.fileExists(cachePath)) {
      try { return {data: JSON.parse(fm.readString(cachePath)), cached:true}; } catch (_) {}
    }
    return {data: {fecha:null,secciones:[]}, cached:true};
  }
}
function pickThree(secciones) {
  const groups = secciones.map(s => ({
    section: s.titulo || s.id || "Actualidad",
    items: (Array.isArray(s.noticias) ? s.noticias : []).filter(n=>n && n.titulo && n.url)
  }));
  const out = [];
  let round = 0;
  while (out.length < 3 && round < 100) {
    let picked = false;
    for (const g of groups) {
      if (g.items[round] && out.length < 3) {
        out.push({ ...g.items[round], section:g.section });
        picked = true;
      }
    }
    if (!picked) break;
    round++;
  }
  return out;
}
function txt(container, value, size, color, weight) {
  const t = container.addText(value);
  t.font = weight === "bold" ? Font.boldSystemFont(size) : Font.systemFont(size);
  t.textColor = color;
  t.lineLimit = 2;
  return t;
}
const {data,cached} = await loadData();
const news = pickThree(data.secciones);
const w = new ListWidget();
w.backgroundColor = F.bg;
w.setPadding(17,18,14,18);
w.url = REPORT_URL;
const top = w.addStack();
top.layoutHorizontally();
top.centerAlignContent();
txt(top, "THE BRIEF", 16, F.white, "bold");
top.addSpacer();
txt(top, "●  DAILY INTELLIGENCE", 8, F.silver, "bold");
w.addSpacer(7);
const line = w.addStack(); line.backgroundColor = F.silver; line.size = new Size(0,1);
w.addSpacer(9);
if (news.length) {
  for (const [i, n] of news.entries()) {
    const section = txt(w, String(n.section).toUpperCase(), 8, F.silver, "bold");
    section.lineLimit = 1;
    w.addSpacer(2);
    const title = txt(w, n.titulo, 11, F.white, "bold");
    title.lineLimit = 2;
    if (i < news.length - 1) w.addSpacer(9);
  }
} else {
  txt(w, "AÚN NO HAY TITULARES PUBLICADOS", 12, F.white, "bold");
  w.addSpacer(6);
  const info = txt(w, "El widget está instalado. Publica noticias verificadas en noticias.json para ver aquí los tres titulares destacados.", 10, F.muted);
  info.lineLimit = 5;
}
w.addSpacer();
const footer = w.addStack(); footer.layoutHorizontally();
txt(footer, data.fecha || "SIN EDICIÓN", 9, F.muted);
footer.addSpacer();
txt(footer, cached ? "CACHÉ / SIN CONEXIÓN  ›" : "ABRIR INFORME  ›", 9, F.silver, "bold");
if (config.runsInWidget) Script.setWidget(w);
else await w.presentMedium();
Script.complete();
