"""Copia las fotos del catálogo de Google Drive a la carpeta img/ de la web.

Lee la lista de modelos del Apps Script (las mismas carpetas de tallas del Drive),
descarga cada foto, la reduce a 900 px y la guarda como img/<id>.jpg.
Borra las fotos de modelos que ya no están en el Drive.
"""
import io, json, os, sys, time, urllib.request
from PIL import Image

STOCK_URL = "https://script.google.com/macros/s/AKfycbynBozJoRGqJQZwyVUyCVZz0vyK1KwE14T8w9Y2K9DDg4AVkgbRDkm6EJYmk2XY8cGFSQ/exec"
EXTRA = ["1SPydGq9V_FtABuFqxiiSdlMXlm4eetuG", "1gSlDqzY0w4OIDex8spgNjOmcxupPVgqp"]  # fotos de "Clientes"
OUT = "img"
UA = {"User-Agent": "Mozilla/5.0 coolstore-sync"}

def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read(), r.headers.get("Content-Type", "")
        except Exception as e:
            err = e
            time.sleep(2 * (i + 1))
    raise err

def photo(fid):
    for url in (f"https://drive.google.com/thumbnail?id={fid}&sz=w1000",
                f"https://lh3.googleusercontent.com/d/{fid}=w1000",
                f"https://drive.usercontent.google.com/download?id={fid}&export=download"):
        try:
            data, ct = get(url)
            if ct.startswith("image/"):
                return data
        except Exception:
            pass
    return None

def main():
    stock = json.loads(get(STOCK_URL + "?t=%d" % time.time())[0])
    ids = sorted({v["id"] for v in stock["items"].values()} | set(EXTRA))
    os.makedirs(OUT, exist_ok=True)
    nuevas = 0
    for fid in ids:
        path = os.path.join(OUT, fid + ".jpg")
        if os.path.exists(path):
            continue
        data = photo(fid)
        if not data:
            print("sin foto:", fid)
            continue
        im = Image.open(io.BytesIO(data)).convert("RGB")
        im.thumbnail((900, 1200))
        im.save(path, "JPEG", quality=80, optimize=True, progressive=True)
        nuevas += 1
    borradas = 0
    for f in os.listdir(OUT):
        if f.endswith(".jpg") and f[:-4] not in ids:
            os.remove(os.path.join(OUT, f)); borradas += 1
    print(f"modelos={len(stock['items'])} fotos={len(ids)} nuevas={nuevas} borradas={borradas}")

if __name__ == "__main__":
    sys.exit(main())
