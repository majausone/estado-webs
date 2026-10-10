# estado-webs

> **El aviso de verdad ahora es UptimeRobot** (desde el 2026-10-10): cuenta de majaus@gmail.com (se
> entra con Google), 11 monitores cada 5 minutos que avisan por correo al caer y al volver: majaus.es,
> la puerta de /p (`/p/entrar`), setensa.com, xinpun.com, flopshare.com/healthz, motoloco (web,
> BRouter y el mapa PMTiles con HEAD, para no bajarse 3,5 GB), ecoloco, musicrafter y burnit. Solo URLs
> públicas, sin claves. GitHub lanza este Action programado cuando le sobra sitio (unas 4-5 veces al
> día en vez de cada 5 minutos), así que esto se queda como respaldo.

Aviso por correo cuando una web de majaus cae o vuelve. Corre en GitHub Actions (fuera del OVH), cada
5 minutos: `comprobar.py` mira las URLs de `webs.txt` y, **solo si alguna cambia de estado**, manda un
correo a majaus@gmail.com por Resend (desde `avisos@setensa.com`). El estado anterior vive en
`estado.json`, que el propio Action guarda con un commit cuando cambia.

- Clave de Resend: secreto `RESEND_API_KEY` del repo (clave «aviso-webs», solo envío, solo setensa.com).
- Repo público a propósito: en uno privado, cada 5 minutos durante un mes se come los minutos
  gratis de Actions. Aquí no hay nada secreto: las URLs son públicas y la clave va como secreto cifrado.
- Añadir o quitar una web: una línea en `webs.txt`.
- `latido.yml` hace un commit al mes para que GitHub no desactive el programado por inactividad.
