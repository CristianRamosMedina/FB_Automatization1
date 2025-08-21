import os
import re
import csv
import json
import shutil
from collections import defaultdict
from ..utils import AbrirJsonCarruseles
# ===================== Utils generales =====================

def downloads_dir():
    return os.path.join(os.path.expanduser("~"), "Downloads")

def documents_dir():
    return os.path.join(os.path.expanduser("~"), "Documents")

def norm_basename(name: str) -> str:
    base = os.path.splitext(os.path.basename(name))[0].lower()
    base = re.sub(r"\s*\(\d+\)\s*$", "", base)        # (1), (2)...
    base = re.sub(r"\bcopy\b", "", base)              # "copy"
    base = re.sub(r"[_\-\s]+", " ", base).strip()     # separadores
    return base

def pick_one_csv(candidates_from_json):
    dl = downloads_dir()
    # 1) exacto
    for name in candidates_from_json:
        if not name:
            continue
        p = os.path.join(dl, name)
        if os.path.exists(p):
            print(f"✔ CSV exacto encontrado: {p}")
            return p
    # 2) parecido (más reciente)
    normalized_targets = {norm_basename(n) for n in candidates_from_json if n}
    best_path, best_mtime = None, -1.0
    try:
        for entry in os.listdir(dl):
            if not entry.lower().endswith(".csv"):
                continue
            path = os.path.join(dl, entry)
            if norm_basename(entry) in normalized_targets:
                mtime = os.path.getmtime(path)
                if mtime > best_mtime:
                    best_mtime, best_path = mtime, path
    except FileNotFoundError:
        pass
    if best_path:
        print(f"✔ CSV parecido elegido (más reciente): {best_path}")
        return best_path
    print("⚠ No se encontró CSV (ni exacto ni parecido).")
    return None

def pick_one_folder(candidates_from_json):
    dl = downloads_dir()
    # 1) exacto
    for name in candidates_from_json:
        if not name:
            continue
        p = os.path.join(dl, name)
        if os.path.isdir(p):
            print(f"✔ Carpeta exacta encontrada: {p}")
            return p
    # 2) parecido (más reciente)
    normalized_targets = {norm_basename(n) for n in candidates_from_json if n}
    best_path, best_mtime = None, -1.0
    try:
        for entry in os.listdir(dl):
            path = os.path.join(dl, entry)
            if not os.path.isdir(path):
                continue
            if norm_basename(entry) in normalized_targets:
                mtime = os.path.getmtime(path)
                if mtime > best_mtime:
                    best_mtime, best_path = mtime, path
    except FileNotFoundError:
        pass
    if best_path:
        print(f"✔ Carpeta parecida elegida (más reciente): {best_path}")
        return best_path
    print("⚠ No se encontró carpeta (ni exacta ni parecida).")
    return None

def ensure_clean_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)

# ===================== Agrupar CSV por ForX =====================

RE_PROMPT = re.compile(r"^\s*For(?P<for>\d+)\.\s*IMG(?P<img>\d+)\.", re.IGNORECASE)

def group_csv_by_for(csv_path):
    """
    Devuelve dict forN -> lista ordenada de IMG según aparecen en el CSV.
    Si no hay columna 'prompt', usa la primera.
    """
    groups = defaultdict(list)
    if not csv_path or not os.path.exists(csv_path):
        return {}

    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, [])
        # localizar columna 'prompt'
        prompt_ix = None
        for i, col in enumerate(header):
            if isinstance(col, str) and col.strip().lower() == "prompt":
                prompt_ix = i
                break
        if prompt_ix is None:
            prompt_ix = 0

        seen = set()  # evitar duplicar IMG si el CSV tiene repetidos
        for row in reader:
            if not row or len(row) <= prompt_ix:
                continue
            p = row[prompt_ix]
            if not isinstance(p, str):
                continue
            m = RE_PROMPT.match(p)
            if not m:
                continue
            for_n = int(m.group("for"))
            img_n  = int(m.group("img"))
            key = (for_n, img_n)
            if key not in seen:
                groups[for_n].append(img_n)
                seen.add(key)

    # devolver dict normal manteniendo orden de aparición
    return {k: v for k, v in groups.items()}

# ===================== Indexar IMÁGENES por ForX/versión =====================

# Soporta: 0001_2_for23-img8-..., 0229_4_for1-img1-..., etc.
RE_FILE = re.compile(
    r"^(?P<num>\d{4})_(?P<ver>[1-4])_(?:for)?(?P<for>\d+)-img(?P<img>\d+)",
    flags=re.IGNORECASE
)

def index_images_by_for(folder_path):
    """
    Devuelve:
      idx[forN][version][imgN] = ruta absoluta del archivo
    """
    idx = defaultdict(lambda: defaultdict(dict))
    if not folder_path or not os.path.isdir(folder_path):
        return {}

    for fname in os.listdir(folder_path):
        if not fname.lower().endswith(".png"):
            continue
        m = RE_FILE.match(fname)
        if not m:
            continue
        for_n = int(m.group("for"))
        ver    = int(m.group("ver"))
        img_n  = int(m.group("img"))
        abs_path = os.path.join(folder_path, fname)
        # si hay duplicados, nos quedamos con el primero visto
        idx[for_n].setdefault(ver, {})
        idx[for_n][ver].setdefault(img_n, abs_path)

    return idx

# ===================== Copiar al destino final =====================

def extract_for_from_pathImagenes(pathImagenes: str):
    """
    Busca .../F{N}/ en pathImagenes (soporta separador / o \\).
    """
    m = re.search(r"[\\/][Ff](\d+)(?:[\\/]|$)", pathImagenes)
    return int(m.group(1)) if m else None

def copy_ordered_to_destination(for_n, destino_final, csv_order_map, img_index_map):
    """
    Crea c1..c4 en destino_final y copia ordenado:
    - Si hay orden del CSV para for_n, usa esa secuencia de IMG.
    - Si no, usa los imgN disponibles en las imágenes.
    """
    # limpiar/crear c1..c4
    for v in range(1, 5):
        ensure_clean_dir(os.path.join(destino_final, f"c{v}"))

    # fuentes
    img_for = img_index_map.get(for_n, {})
    csv_order = csv_order_map.get(for_n, None)  # lista de imgNs o None

    total_copiadas = 0
    for v in range(1, 5):
        destino_c = os.path.join(destino_final, f"c{v}")
        imgs_dict = img_for.get(v, {})  # dict imgN -> path
        if not imgs_dict:
            continue

        if csv_order:
            # respetar el orden del CSV y filtrar a lo que exista
            ordered_imgs = [n for n in csv_order if n in imgs_dict]
        else:
            # fallback: ordenar por número de IMG disponible
            ordered_imgs = sorted(imgs_dict.keys())

        for i, img_n in enumerate(ordered_imgs, start=1):
            src = imgs_dict[img_n]
            dst = os.path.join(destino_c, f"{i}.png")
            shutil.copy2(src, dst)
            total_copiadas += 1

    print(f"✅ For{for_n}: copiadas {total_copiadas} imágenes en {destino_final}")

# ===================== Helpers de agrupación/diagnóstico =====================

def group_items_by_source(items):
    """
    Agrupa entradas del JSON por (rutalocal.carpeta, rutalocal.csv)
    para procesar cada marca/lote por separado.
    """
    groups = defaultdict(list)
    for it in items:
        rl = it.get("rutalocal", {}) or {}
        key = (rl.get("carpeta") or "", rl.get("csv") or "")
        groups[key].append(it)
    return groups

def summarize_img_index(img_index_map):
    lines = []
    for for_n in sorted(img_index_map.keys()):
        counts = [len(img_index_map[for_n].get(v, {})) for v in range(1, 5)]
        total = sum(counts)
        lines.append(f"   For{for_n}: v1={counts[0]} v2={counts[1]} v3={counts[2]} v4={counts[3]} (total={total})")
    return "\n".join(lines) if lines else "   (sin imágenes indexadas)"

# ===================== Main =====================

def main():
    # 1) Cargar JSON
    
    items=AbrirJsonCarruseles()
    # 2) Agrupar por fuente (carpeta+csv) y procesar cada grupo aparte
    docs = documents_dir()
    groups = group_items_by_source(items)

    for (folder_name, csv_name), entries in groups.items():
        print("\n" + "="*80)
        print(f"→ Grupo fuente:")
        print(f"   carpeta esperada: {folder_name or '(vacía)'}")
        print(f"   csv esperado    : {csv_name or '(vacío)'}")

        folder_path = pick_one_folder([folder_name]) if folder_name else None
        csv_path    = pick_one_csv([csv_name]) if csv_name else None

        if not folder_path:
            print("❌ No hay carpeta de imágenes válida para este grupo. Se omite.")
            continue

        # 3) Construir mapas SOLO con recursos de este grupo
        csv_order_map = group_csv_by_for(csv_path) if csv_path else {}
        img_index_map = index_images_by_for(folder_path)

        print(f"   carpeta usada   : {folder_path or '(no encontrada)'}")
        print(f"   csv usado       : {csv_path or '(no encontrado)'}")
        print("   imágenes vistas :")
        print(summarize_img_index(img_index_map))

        # 4) Copiar por cada entrada del grupo
        for it in entries:
            pathImagenes = it.get("pathImagenes")
            if not pathImagenes:
                continue
            for_n = extract_for_from_pathImagenes(pathImagenes)
            if for_n is None:
                continue

            destino_final = os.path.join(docs, pathImagenes)
            os.makedirs(destino_final, exist_ok=True)

            if for_n not in img_index_map:
                print(f"⚠ For{for_n}: no hay imágenes indexadas en este grupo. Destino: {destino_final}")
                for v in range(1, 5):
                    ensure_clean_dir(os.path.join(destino_final, f"c{v}"))
                continue

            copy_ordered_to_destination(for_n, destino_final, csv_order_map, img_index_map)

    print("\n🎉 Proceso terminado.")

if __name__ == "__main__":
    main()
