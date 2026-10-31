# THE BRIEF · Scriptable iPad

Widget **mediano** para iPad en español, con estética negra/antracita y acentos plateados. Este repositorio incluye:

- [the-brief.js](the-brief.js): widget para Scriptable, muestra hasta tres titulares y guarda caché local si falla la conexión.
- [noticias.json](noticias.json): fuente remota de titulares reales por sección.
- [index.html](index.html): maqueta responsive del informe con cuatro pestañas, sin dependencias.

## Instalar en iPad

1. Instala **Scriptable** en el iPad.
2. Abre [the-brief.js](the-brief.js) en GitHub, copia todo su contenido y crea en Scriptable un script llamado **THE BRIEF**.
3. Pega el código, guarda y ejecútalo para previsualizarlo.
4. Añade a la pantalla de inicio un widget **Scriptable de tamaño mediano**.
5. Mantén pulsado el widget → **Editar widget** → Script: **THE BRIEF**.

El widget obtiene las noticias desde el JSON alojado en GitHub y mantiene una copia local de la última edición válida. **Todavía no se han incorporado titulares reales**; se muestra un estado vacío hasta publicar una edición.

## Publicar noticias

Edita `noticias.json` con noticias verificadas y enlaces a sus fuentes. Estructura:

```json
{
  "schema_version": 1,
  "fecha": "2026-10-31",
  "actualizado_en": "2026-10-31T08:00:00+01:00",
  "secciones": [
    {"id":"tecnologia","titulo":"Tecnología, IA y eCommerce","noticias":[
      {"titulo":"Titular verificado","resumen":"Resumen","url":"https://example.com/articulo","fuente":"Medio"}
    ]},
    {"id":"oportunidades","titulo":"Empleo, negocios y formación","noticias":[]},
    {"id":"espana","titulo":"España y Andalucía","noticias":[]},
    {"id":"peru","titulo":"Perú","noticias":[]}
  ]
}
```

El titular anterior es **solo un ejemplo de estructura**, no una noticia publicada. Objetivo editorial: 10 noticias verificadas en cada una de las 4 secciones (40 en total). El widget escoge hasta 3 titulares de distintas secciones.

## Publicar la portada

En GitHub, activa **Settings → Pages → Deploy from a branch → main / root** para servir `index.html` en `https://urfab04.github.io/-the-brief/`. Luego cambia `REPORT_URL` en `the-brief.js` por esa URL.

**Límites actuales:** la portada HTML es una plantilla estática que no carga automáticamente el JSON; no hay alimentador automático de noticias ni tarea diaria configurada en este repositorio. Para mostrar la edición completa se debe generar HTML a partir de noticias verificadas. No se requieren claves de API para el widget.

## Actualización automática (GitHub Actions)

El workflow [daily-news.yml](.github/workflows/daily-news.yml) está programado a las **08:00 Europe/Madrid** y también se puede ejecutar manualmente desde la pestaña **Actions → Publicar noticias THE BRIEF → Run workflow**. Ejecuta [scripts/update_news.py](scripts/update_news.py), recupera titulares de feeds RSS de Google Noticias de los últimos 3 días, selecciona **hasta 10 por sección** (40 máximo) y publica los resultados en `noticias.json`. Si no se obtiene ningún titular, la acción falla y se conserva la edición previa; si alguna fuente falla, puede haber menos de diez noticias por sección. No redacta resúmenes ni realiza verificación periodística independiente. Es una selección automática de titulares y fuentes, no el informe curado original de ChatGPT.

La portada `index.html` ya consulta `noticias.json` y presenta el contenido en cuatro pestañas sin cambiar manualmente el HTML. La publicación de **GitHub Pages** sigue requiriendo activación en Settings → Pages, como se explicó arriba. Verifica en GitHub **Settings → Actions → General → Workflow permissions** que se permita escritura si el commit falla por permisos del `GITHUB_TOKEN`. Las tareas programadas pueden sufrir retrasos por la infraestructura de GitHub.
