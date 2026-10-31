#!/usr/bin/env python3
"""THE BRIEF: compacta titulares de RSS; no redacta ni verifica las noticias."""
import json, re, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
NOW = datetime.now(timezone.utc)
LIMIT = NOW - timedelta(days=3)
CONFIG = [
 ("tecnologia", "Tecnología, IA y eCommerce", ["inteligencia artificial empresas", "comercio electrónico ecommerce Europa", "tecnología ciberseguridad Europa", "Magento Shopify comercio"]),
 ("oportunidades", "Empleo, negocios y formación", ["ofertas empleo desarrollador España", "becas formación tecnología España", "subvenciones empresas autónomos Andalucía", "convocatorias oportunidades empleo Europa"]),
 ("espana", "España y Andalucía", ["actualidad España política economía", "Andalucía actualidad", "Almería actualidad", "Unión Europea legislación digital"]),
 ("peru", "Perú", ["Perú actualidad economía", "Perú política noticias", "Perú tecnología emprendimiento", "Perú empleo educación"]),
]
def fetch(query):
    params = urllib.parse.urlencode({"q": query + " when:3d", "hl": "es", "gl": "ES", "ceid": "ES:es"})
    url = "https://news.google.com/rss/search?" + params
    req = urllib.request.Request(url, headers={"User-Agent": "THE-BRIEF-RSS/1.0"})
    with urllib.request.urlopen(req, timeout=18) as resp:
        root = ET.fromstring(resp.read(3_000_000))
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        source = item.find("source")
        pub = item.findtext("pubDate")
        try: dt = parsedate_to_datetime(pub).astimezone(timezone.utc)
        except (TypeError, ValueError): continue
        if dt < LIMIT or dt > NOW + timedelta(hours=1) or not link.startswith("https://"):
            continue
        medio = source.text.strip() if source is not None and source.text else ""
        if medio and title.endswith(" - " + medio):
            title = title[:-(len(medio)+3)].strip()
        if not title or len(title) < 15: continue
        yield {"titulo":title, "url":link, "fuente":medio or "Google Noticias", "publicado_en":dt.isoformat(), "resumen":""}

def main():
    sections, global_seen, errors = [], set(), []
    count = 0
    for ident, name, queries in CONFIG:
        found = []
        for query in queries:
            try:
                for item in fetch(query):
                    key = re.sub(r"\\W+", "", item["titulo"].casefold())[:95]
                    if key in global_seen: continue
                    global_seen.add(key)
                    found.append(item)
            except Exception as e:
                errors.append(f"{ident}: {type(e).__name__} en una fuente")
        found.sort(key=lambda x:x["publicado_en"], reverse=True)
        chosen = found[:10]
        count += len(chosen)
        sections.append({"id":ident,"titulo":name,"noticias":chosen})
    if count == 0:
        raise RuntimeError("Ninguna noticia recuperada: se mantiene la edición anterior.")
    local = NOW.astimezone(ZoneInfo("Europe/Madrid"))
    data = {"schema_version":1,"fecha":local.date().isoformat(),"actualizado_en":local.isoformat(timespec="seconds"),
            "descripcion":"Selección automática de titulares RSS de Google Noticias, sin verificación editorial independiente ni resúmenes generados.",
            "fuentes_con_errores":errors,"secciones":sections}
    (ROOT/"noticias.json").write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\\n", encoding="utf-8")
    print(f"Actualizado: {count} titulares; secciones: "+", ".join(str(len(x["noticias"])) for x in sections))
if __name__ == "__main__": main()
