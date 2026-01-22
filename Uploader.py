#!/usr/bin/env python3
import os
import time
import shutil
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OUTPUT_PATH = os.getenv("OUTPUTPATH")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_PREFIX = os.getenv("S3_PREFIX", "outputs").strip("/")
UPLOADED_PATH = os.getenv("UPLOADEDPATH")
FAILED_PATH = os.getenv("FAILEDPATH")
IGNORE_DIRS = {"fail", "_uploaded", "_failed"}


root = Path(OUTPUT_PATH)
uploaded = Path(UPLOADED_PATH)
failed = Path(FAILED_PATH)


uploaded.mkdir(parents=True, exist_ok=True)
failed.mkdir(parents=True, exist_ok=True)



# Función para mover directorios
def safe_move_dir(src: Path, dst_dir: Path) -> Path:
    dst = dst_dir / src.name
    if dst.exists():
        dst = dst_dir / f"{src.name}_{int(time.time())}"
    try:
        src.rename(dst)  # rápido si es mismo filesystem
    except OSError:
        shutil.move(str(src), str(dst))  # cross-filesystem
    return dst

#loop infinito
while True:
    for item in root.iterdir(): #lista contenido directo de la carpeta root (no subcarpetas)
        #si lo que hay dentro de la carpeta output no es un directorio entonces 
        #lo ignora (recorda que la salida de cada ejecución es una carpeta con el nombre del video y timestamp).
        if not item.is_dir():
            continue

        #ignorar algunos directorios que no tienen que ver con videos procesados.
        if item.name in IGNORE_DIRS:
            continue

        success_flag = item / "_SUCCESS"
        running_flag = item / "_RUNNING"

        # solo subir si terminó (success_flag existe y running_flag no existe)
        if not (success_flag.exists() and not running_flag.exists()):
            continue

        print("subiendo archivos....")

        s3_dest = f"s3://{S3_BUCKET}/{S3_PREFIX}/{item.name}/"
        print(f"[UPLOAD] {item} -> {s3_dest}")

        proc = subprocess.run(
            ["aws", "s3", "sync", str(item), s3_dest, "--only-show-errors"],
            text=True,
            capture_output=True
        )

        if proc.returncode == 0:
            moved_to = safe_move_dir(item, uploaded)
            print(f"[OK] Subido y movido a: {moved_to}")
        else:
            print(f"[ERROR] aws s3 sync falló (code={proc.returncode}) para {item}")
            if proc.stderr:
                print(f"[STDERR] {proc.stderr.strip()}")
            if proc.stdout:
                print(f"[STDOUT] {proc.stdout.strip()}")

            moved_to = safe_move_dir(item, failed)
            print(f"[FAIL] Movido a: {moved_to}")

    time.sleep(5)
