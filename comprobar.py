"""Mira las webs de webs.txt y avisa por correo (Resend) solo cuando alguna CAE o VUELVE.

El estado de la vez anterior está en estado.json (lo guarda el propio Action con un commit, solo
cuando cambia). Sin dependencias: solo la biblioteca estándar de Python.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

AQUI = os.path.dirname(os.path.abspath(__file__))
ESTADO = os.path.join(AQUI, "estado.json")
# Con el User-Agent por defecto de urllib, Cloudflare contesta 403 (error 1010).
UA = "estado-webs/1.0 (+https://github.com/majausone/estado-webs)"


def webs():
    for linea in open(os.path.join(AQUI, "webs.txt"), encoding="utf-8"):
        linea = linea.strip()
        if linea and not linea.startswith("#"):
            nombre, url = linea.split(None, 1)
            yield nombre, url.strip()


class SinRedireccion(urllib.request.HTTPRedirectHandler):
    """Un 3xx cuenta como «responde»: no hace falta seguirlo."""

    def redirect_request(self, *args, **kwargs):
        return None


def mirar(url):
    abridor = urllib.request.build_opener(SinRedireccion)
    fallo = "sin respuesta"
    for intento in range(2):
        try:
            r = abridor.open(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=20)
            return True, f"HTTP {r.status}"
        except urllib.error.HTTPError as e:
            if 300 <= e.code < 400:
                return True, f"HTTP {e.code}"
            fallo = f"HTTP {e.code}"
        except Exception as e:  # DNS, TLS, tiempo agotado...
            fallo = f"{type(e).__name__}: {e}"[:200]
        if intento == 0:
            time.sleep(10)  # dos intentos: no se avisa por un tropiezo de red
    return False, fallo


def avisar(asunto, texto):
    clave = os.environ.get("RESEND_API_KEY")
    if not clave:
        print("SIN RESEND_API_KEY: no se manda el correo", file=sys.stderr)
        return
    datos = json.dumps({
        "from": "Aviso webs <avisos@setensa.com>",
        "to": [os.environ.get("AVISO_PARA", "majaus@gmail.com")],
        "subject": asunto,
        "text": texto,
    }).encode()
    req = urllib.request.Request("https://api.resend.com/emails", data=datos, method="POST", headers={
        "Authorization": f"Bearer {clave}", "Content-Type": "application/json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        print("correo enviado:", r.status)


def main():
    antes = json.load(open(ESTADO, encoding="utf-8")) if os.path.exists(ESTADO) else {}
    ahora, cambios = {}, []
    hora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    for nombre, url in webs():
        arriba, detalle = mirar(url)
        print(f"{'OK   ' if arriba else 'CAÍDA'} {nombre:15} {url}  {detalle}")
        previo = antes.get(nombre, {})
        estaba = previo.get("arriba", True)  # una web nueva se da por «arriba»
        desde = previo.get("desde", hora) if estaba == arriba else hora
        ahora[nombre] = {"arriba": arriba, "url": url, "detalle": detalle, "desde": desde}
        if estaba != arriba:
            cambios.append((nombre, url, arriba, detalle, previo.get("desde")))

    if cambios:
        partes = []
        caidas = [c[0] for c in cambios if not c[2]]
        vueltas = [c[0] for c in cambios if c[2]]
        if caidas:
            partes.append("CAÍDA: " + ", ".join(caidas))
        if vueltas:
            partes.append("VUELVE: " + ", ".join(vueltas))
        lineas = [hora, ""]
        for nombre, url, arriba, detalle, desde in cambios:
            if arriba:
                lineas.append(f"OK: {nombre} vuelve a responder ({detalle}). Estaba caída desde {desde}.")
            else:
                lineas.append(f"CAÍDA: {nombre} NO responde: {detalle}\n   {url}")
        lineas += ["", "Estado de todas:"]
        lineas += [f"  {'OK   ' if v['arriba'] else 'CAÍDA'}  {k}  ({v['detalle']}, desde {v['desde']})"
                   for k, v in ahora.items()]
        lineas += ["", "Solo se avisa al caer y al volver. https://github.com/majausone/estado-webs/actions"]
        avisar(" · ".join(partes), "\n".join(lineas))

    # Se guarda si alguna cambió de estado o si cambió la lista de webs.
    if cambios or set(ahora) != set(antes):
        with open(ESTADO, "w", encoding="utf-8") as f:
            json.dump(ahora, f, ensure_ascii=False, indent=2)
        print("estado.json actualizado")


if __name__ == "__main__":
    main()
