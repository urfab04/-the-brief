#!/usr/bin/env python3
"""Recolección RSS THE BRIEF: sin titulares inventados ni validación editorial."""
import json, re, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
NOW = datetime.now(timezone.utc)
LIMIT = NOW - timedelta(days=3)
# Fuentes directas y clasificadas. Una fuente caída no bloquea a las demás.
FEEDS = [
 ("tecnologia", "Tecnología, IA y eCommerce", [
   ("EL PAÍS · Tecnología", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/tecnologia/portada"),
 ]),
 ("oportunidades", "Empleo, negocios y formación", [
   ("EL PAÍS · Economía", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/economia/portada"),
   ("Expansión", "https://e00-expansion.uecdn.es/rss/portada.xml"),
 ]),
 ("espana", "España y Andalucía", [
   ("EL PAÍS · España", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/espana/portada"),
   ("ElDiario.es", "https://www.eldiario.es/rss/"),
 ]),
 ("peru", "Perú", [
   ("RPP", "https://rpp.pe/feed"),
   ("El Comercio Perú", "https://elcomercio.pe/arc/outboundfeeds/rss/?outputType=xml"),
 ]),
]
def read_feed(label, url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; THEBRIEF/1.1; RSS)", "Accept": "application/rss+xml, application/xml, text/xml, */*"})
    with urllib.request.urlopen(req, timeout=9) as response:
        root = ET.fromstring(response.read(3_000_000))
    items = root.findall("./channel/item")
    if not items: items = root.findall(".//{http://www.w3.org/2005/Atom}entry")
    for elem in items:
        title = (elem.findtext("title") or elem.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
        link = (elem.findtext("link") or "").strip()
        if not link:
            atomlink = elem.find("{http://www.w3.org/2005/Atom}link")
            if atomlink is not None: link = atomlink.attrib.get("href", "")
        date = elem.findtext("pubDate") or elem.findtext("{http://www.w3.org/2005/Atom}updated")
        try:
            dt = parsedate_to_datetime(date).astimezone(timezone.utc)
        except (TypeError, ValueError, OverflowError):
            try: dt = datetime.fromisoformat(date.replace("Z","+00:00")).astimezone(timezone.utc)
            except (TypeError, ValueError, AttributeError): continue
        if not (LIMIT <= dt <= NOW + timedelta(hours=1)) or not link.startswith("https://") or len(title) < 15:
            continue
        yield {"titulo":title,"url":link,"fuente":label,"publicado_en":dt.isoformat(),"resumen":""}

def main():
    sections, errors, total = [], [], 0
    for ident, heading, sources in FEEDS:
        found, seen = [], set()
        for label, url in sources:
            try:
                for item in read_feed(label, url):
                    key = re.sub(r"\W+", "", item["titulo"].casefold())[:95]
                    if key in seen: continue
                    seen.add(key)
                    found.append(item)
            except Exception as e:
                msg = f"{ident} / {label}: {type(e).__name__}: {e}"
                print("ADVERTENCIA:", msg, flush=True)
                errors.append(msg)
        found.sort(key=lambda n: n["publicado_en"], reverse=True)
        chosen = found[:10]
        print(f"{ident}: {len(chosen)} titulares", flush=True)
        total += len(chosen)
        sections.append({"id":ident,"titulo":heading,"noticias":chosen})
    if total == 0:
        raise RuntimeError("Ningún feed respondió con noticias recientes; se conserva la edición anterior.")
    current = NOW.astimezone(ZoneInfo("Europe/Madrid"))
    data = {"schema_version":1,"fecha":current.date().isoformat(),"actualizado_en":current.isoformat(timespec="seconds"),
            "descripcion":"Agregación automática de titulares RSS. No constituye edición periodística verificada.",
            "fuentes_con_errores":errors,"secciones":sections}
    (ROOT / "noticias.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Publicación preparada: {total} titulares",flush=True)

if __name__ == "__main__": main()
