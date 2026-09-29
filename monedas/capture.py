"""Interactive, reproducible Nikon D60 capture sessions."""

import argparse
import json
import math
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


BOARD = {"kind": "ChArUco", "width_mm": 600, "height_mm": 400, "square_mm": 40}
QUIT = {":q", ":quit", ":salir"}


class EndSession(Exception):
    pass


def ask(label, previous=None, convert=str):
    suffix = f" [{previous}]" if previous is not None else ""
    value = input(f"{label}{suffix}: ").strip()
    if value.lower() in QUIT:
        raise EndSession
    if not value:
        return previous
    return convert(value)


def positive(value):
    result = float(value.replace(",", "."))
    if not math.isfinite(result) or result <= 0:
        raise ValueError("debe ser un número positivo")
    return result


def nonnegative_int(value):
    result = int(value)
    if result < 0:
        raise ValueError("debe ser un entero no negativo")
    return result


def read_state(path):
    if not path.exists():
        return {}
    state = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(state, dict):
        raise ValueError(f"Estado inválido: {path}")
    return state


def write_json(path, data):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def geometry(hypotenuse, horizontal):
    if horizontal >= hypotenuse:
        raise ValueError("El cateto horizontal debe ser menor que la hipotenusa")
    return round(math.degrees(math.acos(horizontal / hypotenuse)), 3)


def collect(previous):
    while True:
        try:
            print("\nIntro para conservar el dato; :q para salir (también Ctrl+C).")
            h = ask("Distancia cámara → punto enfocado (hipotenusa, mm)", previous.get("hypotenuse_mm"), positive)
            a = ask("Distancia horizontal al punto enfocado (cateto, mm)", previous.get("horizontal_mm"), positive)
            f = ask("Focal ajustada (mm)", previous.get("focal_length_mm"), positive)
            count = ask("Número de monedas visibles (0 si solo calibración)", previous.get("coin_count"), nonnegative_int)
            label = ask("País / tipo de moneda (libre; 'mixto' si procede)", previous.get("coin_label"))
            description = ask("Descripción de esta toma", previous.get("description"))
            if any(v is None for v in (h, a, f, count)):
                raise ValueError("hipotenusa, cateto, focal y número de monedas son obligatorios")
            angle = geometry(h, a)
            values = dict(hypotenuse_mm=h, horizontal_mm=a, focal_length_mm=f,
                          coin_count=count, coin_label=label, description=description)
            print(f"Ángulo estimado respecto al plano: {angle}°")
            confirm = input("Intro para capturar; :q para salir; 'r' para corregir: ").strip().lower()
            if confirm in QUIT:
                raise EndSession
            if confirm == "r":
                previous = values
                continue
            if confirm:
                raise ValueError("Respuesta desconocida")
            return values, angle
        except ValueError as exc:
            print(f"Dato inválido: {exc}. Repite la ficha.")


def capture(output, capture_id, values, angle, session_id, command):
    staging = output / (".capturing-" + capture_id)
    staging.mkdir()
    try:
        subprocess.run([command, "--capture-image-and-download", "--filename",
                        str(staging / "image.%C")], check=True)
        images = sorted(p for p in staging.iterdir() if p.is_file() and p.stat().st_size)
        if not images:
            raise RuntimeError("gphoto2 no descargó ninguna imagen")
        names = [f"{capture_id}{p.suffix.lower()}" for p in images]
        if len(set(names)) != len(names) or any((output / name).exists() for name in names):
            raise RuntimeError("Colisión de nombres de imagen")
        metadata = {
            "schema_version": 1,
            "capture_id": capture_id,
            "session_id": session_id,
            "captured_at_utc": datetime.now(timezone.utc).isoformat(),
            "camera": "Nikon D60",
            "board": BOARD,
            "measurements": {
                "hypotenuse_mm": values["hypotenuse_mm"],
                "horizontal_mm": values["horizontal_mm"],
                "focal_length_mm_manual": values["focal_length_mm"],
                "angle_to_plane_deg_estimated": angle,
                "angle_method": "acos(horizontal_mm / hypotenuse_mm)",
            },
            "annotation": {"coin_count": values["coin_count"],
                           "coin_label": values["coin_label"],
                           "description": values["description"]},
            "image_files": names,
        }
        for source, name in zip(images, names):
            source.replace(output / name)
        write_json(output / f"{capture_id}.json", metadata)
        return names
    finally:
        shutil.rmtree(staging)


def main():
    parser = argparse.ArgumentParser(description="Captura monedas con gphoto2 y anota cada toma")
    parser.add_argument("--output", type=Path, default=Path("captures"), help="Directorio de fotos y JSON")
    parser.add_argument("--gphoto2", default="gphoto2", help="Ruta al ejecutable gphoto2")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    state_path = args.output / ".session-defaults.json"
    try:
        state = read_state(state_path)
        session_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
        print(f"Sesión {session_id} · salida {args.output.resolve()}")
        while True:
            values, angle = collect(state)
            capture_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid.uuid4().hex[:8]
            try:
                names = capture(args.output, capture_id, values, angle, session_id, args.gphoto2)
            except (subprocess.CalledProcessError, FileNotFoundError, RuntimeError, OSError) as exc:
                print(f"Captura fallida: {exc}. No se modifican los valores guardados.", file=sys.stderr)
                continue
            write_json(state_path, values)
            state = values
            print(f"Guardado: {', '.join(names)} y {capture_id}.json")
    except (EndSession, KeyboardInterrupt, EOFError):
        print("\nSesión cerrada.")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
