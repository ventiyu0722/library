#!/usr/bin/env python3
"""Build the effect table CSV and ordered image folder matching the PDF layout."""

import csv
import shutil
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "test" / "results"
OUTPUT_DIR = Path.home() / "Desktop" / "template_effect_table"
IMAGES_DIR = OUTPUT_DIR / "output_images"

ROWS = [
    # (index, category, play, template_id, input_query, photo_type)
    # photo_type: "selfie", "pet", "baby", "room", None (text-only)

    # 1. Life & Entertainment - Stylization (29)
    (1, "1.Life-Stylization", "Chibi Cartoon", "L01", "Turn my photo into chibi cartoon style", "selfie"),
    (2, "1.Life-Stylization", "3D Pixar", "L02", "Turn me into a 3D Pixar animation character", "selfie"),
    (3, "1.Life-Stylization", "Comic/Manga", "L03", "Turn my photo into comic/manga style", "selfie"),
    (4, "1.Life-Stylization", "Sketch", "L04", "Draw a sketch portrait of me", "selfie"),
    (5, "1.Life-Stylization", "Clay", "L05", "Turn me into a claymation character", "selfie"),
    (6, "1.Life-Stylization", "80s Retro", "L06", "Turn me into 80s retro animation style", "selfie"),
    (7, "1.Life-Stylization", "Retro-Futurism", "L07", "Turn me into retro-futurism style", "selfie"),
    (8, "1.Life-Stylization", "Ukiyo-e/Chinese Painting", "L08", "Turn my photo into ukiyo-e/Chinese painting style", "selfie"),
    (9, "1.Life-Stylization", "Watercolor", "L09", "Draw a watercolor portrait of me", "selfie"),
    (10, "1.Life-Stylization", "K-Pop", "L10", "Turn me into K-Pop idol style", "selfie"),
    (11, "1.Life-Stylization", "Imperial", "L11", "Turn me into imperial portrait style", "selfie"),
    (12, "1.Life-Stylization", "90s Yearbook", "L12", "Turn me into 90s yearbook style", "selfie"),
    (13, "1.Life-Stylization", "High Fashion", "L13", "Turn me into high fashion magazine style", "selfie"),
    (14, "1.Life-Stylization", "Cyberpunk", "L14", "Turn me into cyberpunk style", "selfie"),
    (15, "1.Life-Stylization", "Oil Painting", "L15", "Turn me into classical oil painting style", "selfie"),
    (16, "1.Life-Stylization", "Pixel Art", "L16", "Turn me into pixel art style", "selfie"),
    (17, "1.Life-Stylization", "Flat Illustration", "L17", "Turn me into flat vector illustration style", "selfie"),
    (18, "1.Life-Stylization", "Anime", "L18", "Turn me into anime style", "selfie"),
    (19, "1.Life-Stylization", "Wool Felt", "L19", "Turn me into wool felt style", "selfie"),
    (20, "1.Life-Stylization", "Colored Pencil", "L20", "Turn me into colored pencil drawing style", "selfie"),
    (21, "1.Life-Stylization", "Pop Art", "L21", "Turn me into pop art style", "selfie"),
    (22, "1.Life-Stylization", "Miniature Diorama", "L22", "Turn me into miniature diorama style", "selfie"),
    (23, "1.Life-Stylization", "Children Drawing", "L23", "Turn me into children's drawing style", "selfie"),
    (24, "1.Life-Stylization", "Game CG", "L24", "Turn me into game CG thick paint style", "selfie"),
    (25, "1.Life-Stylization", "Vaporwave", "L25", "Turn me into vaporwave style", "selfie"),
    (26, "1.Life-Stylization", "Printmaking", "L26", "Turn me into printmaking style", "selfie"),
    (27, "1.Life-Stylization", "Gongbi", "L27", "Turn me into gongbi painting style", "selfie"),
    (28, "1.Life-Stylization", "Simple Line", "L28", "Turn me into simple line drawing style", "selfie"),
    (29, "1.Life-Stylization", "Dark Fairy Tale", "L29", "Turn me into dark fairy tale style", "selfie"),

    # 1. Life & Entertainment - Portrait (18)
    (30, "1.Life-Portrait", "Studio Photoshoot", "L30", "Take a professional studio portrait of me", "selfie"),
    (31, "1.Life-Portrait", "ID Photo", "L31", "Generate an ID photo for me", "selfie"),
    (32, "1.Life-Portrait", "Emoji/Sticker", "L32", "Make an emoji/sticker pack from my photo", "selfie"),
    (33, "1.Life-Portrait", "Avatar", "L33", "Generate a stylish avatar for me", "selfie"),
    (34, "1.Life-Portrait", "Cinematic Portrait", "L34", "Turn my photo into cinematic portrait style", "selfie"),
    (35, "1.Life-Portrait", "Dreamy Hazy", "L35", "Generate a dreamy hazy portrait of me", "selfie"),
    (36, "1.Life-Portrait", "Indoor Side Shot", "L36", "Generate an indoor side shot portrait of me", "selfie"),
    (37, "1.Life-Portrait", "Dark Mood", "L37", "Take a dark mood portrait of me", "selfie"),
    (38, "1.Life-Portrait", "Red Wall Shot", "L38", "Take a photo of me in front of a red wall", "selfie"),
    (39, "1.Life-Portrait", "Spring Cherry Blossom", "L39", "Take a spring cherry blossom portrait of me", "selfie"),
    (40, "1.Life-Portrait", "Dappled Shadow", "L40", "Take a dappled tree shadow portrait of me", "selfie"),
    (41, "1.Life-Portrait", "Sunset Golden Hour", "L41", "Take a sunset golden hour portrait of me", "selfie"),
    (42, "1.Life-Portrait", "Retro Film Polaroid", "L42", "Generate a retro film Polaroid style photo of me", "selfie"),
    (43, "1.Life-Portrait", "Winter Snow", "L43", "Take a winter snow portrait of me", "selfie"),
    (44, "1.Life-Portrait", "Beach Portrait", "L44", "Take a beach portrait of me", "selfie"),
    (45, "1.Life-Portrait", "Magic Academy", "L45", "Turn me into a magic academy student", "selfie"),
    (46, "1.Life-Portrait", "Street Style OOTD", "L46", "Take a street style OOTD photo of me", "selfie"),
    (47, "1.Life-Portrait", "Cherry Blossom Triptych", "L48", "Make a cherry blossom themed photo triptych", "selfie"),

    # 1. Life & Entertainment - Pets & Babies (5)
    (48, "1.Life-Pets", "Pet Stylization", "L50", "Stylize my pet into a cute character", "pet"),
    (49, "1.Life-Pets", "Pet VOGUE Magazine", "L52", "Make a VOGUE magazine cover for my pet", "pet"),
    (50, "1.Life-Pets", "Pet Mugshot", "L53", "Make a pet mugshot photo", "pet"),
    (51, "1.Life-Pets", "Pet Humanization", "L54", "Humanize my pet", "pet"),
    (52, "1.Life-Pets", "Baby Comic Grid", "L51", "Make a comic expression grid for my baby", "baby"),

    # 2. Media & Work - Editing Tools (6)
    (53, "2.Media-Editing", "Outfit Change (suit)", "L60", "Change my outfit to a suit", "selfie"),
    (54, "2.Media-Editing", "Hairstyle Change (short)", "L61", "Change my hairstyle to short hair", "selfie"),
    (55, "2.Media-Editing", "Background Change (beach)", "L62", "Change my background to a beach", "selfie"),
    (56, "2.Media-Editing", "Outpaint (expand 30%)", "L63", "Expand my photo 30% on each side", "selfie"),
    (57, "2.Media-Editing", "Object Removal", "L64", "Remove background clutter from my photo", "selfie"),
    (58, "2.Media-Editing", "Image Enhancement", "L65", "Enhance my photo to make it clearer", "selfie"),

    # 2. Media & Work - Social Media (1)
    (59, "2.Media-Social", "Social Media Post", "M01", "Generate a 'Stay Hungry, Stay Foolish' quote card", None),

    # 2. Media & Work - Poster (4)
    (60, "2.Media-Poster", "Poster Design", "M02", "Design a spring concert poster", None),
    (61, "2.Media-Poster", "Handwritten Poster", "M04", "Make an eco-themed bulletin board poster", None),
    (62, "2.Media-Poster", "Illustration", "M05", "Draw a Ghibli-style floating island illustration", None),
    (63, "2.Media-Poster", "Picture Book Illustration", "M08", "Draw a picture book illustration of a fox finding a tree hole", None),

    # 2. Media & Work - Storyboard (1)
    (64, "2.Media-Storyboard", "Storyboard", "M03", "Draw a 4-panel comic about a day in life", None),

    # 2. Media & Work - YouTube Thumbnail (1)
    (65, "2.Media-Thumbnail", "YouTube Thumbnail", "M06", "Make an 'AI Tools TOP 10' YouTube thumbnail", None),

    # 2. Media & Work - Educational Visual (1)
    (66, "2.Media-Educational", "Educational Visual", "M07", "Make a photosynthesis educational diagram", None),

    # 3. Professional Design (8)
    (67, "3.Pro-Design", "E-commerce Main Image", "P01", "Make a honey product e-commerce hero image", None),
    (68, "3.Pro-Design", "Sticker Set Design", "P02", "Make a sticker set from my photo", "selfie"),
    (69, "3.Pro-Design", "Interior Design", "P03", "Redesign my room in Nordic minimalist style", "room"),
    (70, "3.Pro-Design", "Logo Design", "P04", "Design an ALPINE brand mountain logo", None),
    (71, "3.Pro-Design", "Merchandise Design", "P05", "Make a figurine from my photo", "selfie"),
    (72, "3.Pro-Design", "Coloring Book Page", "P06", "Draw a fairy tale coloring book page", None),
    (73, "3.Pro-Design", "Game Asset Design", "P07", "Design an RPG battle mage character", None),
    (74, "3.Pro-Design", "Product Marketing Design", "P08", "Design a headphone product marketing image", None),
]

PHOTO_LABEL = {
    "selfie": "[Upload selfie] ",
    "pet": "[Upload pet photo] ",
    "baby": "[Upload baby photo] ",
    "room": "[Upload room photo] ",
}


def find_image(tid: str) -> str | None:
    d = RESULTS_DIR / tid
    if not d.exists():
        return None
    for ext in ["png", "jpg", "jpeg"]:
        for f in sorted(d.glob(f"*.{ext}")):
            return str(f)
    return None


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = OUTPUT_DIR / "effect_table.csv"
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Index", "Category", "Play", "Template ID", "Input", "Output Image Filename"])

        ok = 0
        miss = 0
        for idx, cat, play, tid, query, photo in ROWS:
            full_input = PHOTO_LABEL.get(photo, "") + query
            img = find_image(tid)
            if img:
                fname = f"{idx:02d}_{tid}_{play}.png"
                fname = fname.replace("/", "_")
                dest = IMAGES_DIR / fname
                shutil.copy2(img, dest)
                writer.writerow([idx, cat, play, tid, full_input, fname])
                ok += 1
            else:
                writer.writerow([idx, cat, play, tid, full_input, "(not generated)"])
                miss += 1

    print(f"CSV saved: {csv_path}")
    print(f"Images: {ok} copied, {miss} missing")
    print(f"Folder: {IMAGES_DIR}")


if __name__ == "__main__":
    main()
