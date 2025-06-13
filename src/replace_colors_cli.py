"""
Créé par : Niels G.
Créé le : 13/06/2025

Script qui permet de remplacer les couleurs "à peu près" équivalentes à la couleur source, selon un seuil de distance euclidienne entre deux couleurs RGB.
"""

import argparse
from PIL import Image
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_lab(rgb):
    rgb_obj = sRGBColor(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
    return convert_color(rgb_obj, LabColor)


def color_distance(c1, c2):
    """Distance DeltaE 2000 entre deux tuples RGB"""
    lab1 = rgb_to_lab(c1)
    lab2 = rgb_to_lab(c2)
    return delta_e_cie2000(lab1, lab2)


def replace_colors(img, replacements, tolerance):
    """Remplace les couleurs proches dans l'image"""
    img = img.convert("RGBA")
    pixels = img.load()

    width, height = img.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            for src_hex, tgt_hex in replacements.items():
                src_rgb = hex_to_rgb(src_hex)
                tgt_rgb = hex_to_rgb(tgt_hex)
                if color_distance((r, g, b), src_rgb) <= tolerance:
                    pixels[x, y] = (*tgt_rgb, a)
                    break  # on remplace par la première correspondance trouvée
    return img


def main():
    parser = argparse.ArgumentParser(description="Remplace des couleurs proches dans une image.")
    parser.add_argument("input", help="Chemin de l'image d'entrée (PNG, JPG)")
    parser.add_argument("output", help="Chemin de sortie")
    parser.add_argument("--map", nargs='+', required=True, help="Liste de remplacements HEX format #source:#cible")
    parser.add_argument("--tolerance", type=float, default=10.0, help="Tolérance DeltaE (par défaut: 10)")

    args = parser.parse_args()

    # construction du mapping
    color_map = {}
    for pair in args.map:
        if ':' not in pair:
            raise ValueError(f"Mauvais format : {pair} (utiliser #source:#cible)")
        src, tgt = pair.split(':')
        color_map[src.lower()] = tgt.lower()

    img = Image.open(args.input)
    img = replace_colors(img, color_map, args.tolerance)
    img.save(args.output)
    print(f"✅ Image sauvegardée dans {args.output}")


if __name__ == "__main__":
    main()