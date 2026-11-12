
#!/usr/bin/env python3

import json
import re
import argparse

from pathlib import Path
from datetime import datetime
from PIL import Image, ExifTags


# Formati immagine supportati
SUPPORTED_FORMATS = {
    ".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"
}

# Mappa dei tag EXIF
EXIF_TAGS = {
    value: key for key, value in ExifTags.TAGS.items()
}

ORIENTATION_TAG = EXIF_TAGS.get("Orientation")
DATETIME_TAG = EXIF_TAGS.get("DateTimeOriginal")


def extract_filename_date(filename):
    """
    Formato atteso:
    2005 - 10-27-2005.JPG

    MM-DD-YYYY
    """

    match = re.match(
        r"^(\d{4})\s*-\s*(\d{2})-(\d{2})-(\d{4})$",
        Path(filename).stem
    )

    if not match:
        return None

    prefix_year, month, day, file_year = match.groups()

    try:
        photo_date = datetime(
            int(file_year),
            int(month),
            int(day)
        )

        # Verifica coerenza tra anno iniziale e anno della data
        if int(prefix_year) != int(file_year):
            print(f"ATTENZIONE: anno discordante: {filename}")

        return photo_date

    except ValueError:
        return None


def extract_exif_date(image):

    try:
        exif = image.getexif()

        if DATETIME_TAG is None:
            return None

        exif_date = exif.get(DATETIME_TAG)

        if not exif_date:
            return None

        return datetime.strptime(
            exif_date,
            "%Y:%m:%d %H:%M:%S"
        ).isoformat()

    except Exception:
        return None


def get_dimensions(image):

    width, height = image.size

    try:
        exif = image.getexif()

        orientation = exif.get(ORIENTATION_TAG, 1)

        # Le orientazioni 5, 6, 7 e 8
        # richiedono lo scambio di larghezza e altezza
        if orientation in (5, 6, 7, 8):
            width, height = height, width

    except Exception:
        pass

    return width, height


def determine_layout(width, height):

    ratio = width / height

    if ratio >= 2.0:
        return "panorama"

    elif ratio >= 1.35:
        return "wide"

    elif ratio <= 0.80:
        return "tall"

    else:
        return "square"


def process_image(image_path, images_dir):

    try:

        with Image.open(image_path) as image:

            width, height = get_dimensions(image)

            filename_date = extract_filename_date(
                image_path.name
            )

            exif_date = extract_exif_date(image)

            layout = determine_layout(width, height)

            return {

                "filename": image_path.name,

                "src": (
                    Path(images_dir.name) /
                    image_path.name
                ).as_posix(),

                "date": (
                    filename_date.strftime("%Y-%m-%d")
                    if filename_date else None
                ),

                "year": (
                    filename_date.year
                    if filename_date else None
                ),

                "exif_date": exif_date,

                "width": width,

                "height": height,

                "ratio": round(width / height, 3),

                "orientation": (
                    "landscape" if width > height
                    else "portrait" if height > width
                    else "square"
                ),

                "layout": layout,

                "size_bytes": image_path.stat().st_size

            }

    except Exception as error:

        print(f"ERRORE {image_path.name}: {error}")

        return None


def main():

    parser = argparse.ArgumentParser(
        description="Genera JSON per album fotografico"
    )

    parser.add_argument(
        "--images",
        default="images",
        help="Cartella contenente le fotografie"
    )

    parser.add_argument(
        "--output",
        default="photos.json",
        help="Nome del file JSON"
    )

    args = parser.parse_args()

    images_dir = Path(args.images)

    if not images_dir.exists():
        print("Cartella immagini non trovata!")
        return

    photos = []

    files = sorted(
        p for p in images_dir.iterdir()
        if p.is_file()
        and p.suffix.lower() in SUPPORTED_FORMATS
    )

    print(f"Fotografie trovate: {len(files)}")

    for image_path in files:

        photo = process_image(image_path, images_dir)

        if photo:

            if not photo["date"]:
                print(
                    f"ATTENZIONE: data non riconosciuta: "
                    f"{image_path.name}"
                )

            photos.append(photo)

    # Ordinamento cronologico, le immagini senza data
    # vengono collocate alla fine
    photos.sort(
        key=lambda p: (
            p["date"] is None,
            p["date"] or "",
            p["filename"].lower()
        )
    )

    output_path = Path(args.output)

    with output_path.open("w", encoding="utf-8") as file:

        json.dump(
            photos,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print(f"JSON generato: {output_path}")
    print(f"Immagini elaborate: {len(photos)}")

    print("\nDistribuzione layout:")

    for layout in ("square", "wide", "tall", "panorama"):

        count = sum(
            1 for photo in photos
            if photo["layout"] == layout
        )

        print(f"{layout}: {count}")


if __name__ == "__main__":
    main()
