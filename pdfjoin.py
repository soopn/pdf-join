import io
import json
from os import _exit
import sys
from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pathlib import Path
from utilities import *
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", "arialbd.ttf"))

# TODO: page number location, font, font size
# TODO: have targets be indescriminate of .pdf extension

DEFAULT_MANIFEST_PATH = "./manifest.json"
FONT = "Arial"
FONT_SZ = 18
OUTPUT_FILE = "Lorem Ipsum.pdf"
BOLDED = True

"""
JSON CONVERSIONS:

JSON    |   PYTHON
-------------------
object  |   dict
array   |   list
string  |   str
null    |   None
int     |   int

"""

# def parse_json() -> dict[str, str]:
#     pass


def count_pages(pdfs: list[PdfReader]) -> int:
    tally = 0
    for file in pdfs:
        tally += len(file.pages)

    return tally


def write_page_nums(pgNum):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)

    pageWidth = page.mediabox.width
    pageHeight = page.mediabox.height

    if BOLDED:
        can.setFont(FONT + "-Bold", FONT_SZ)
    else:
        can.setFont(FONT, FONT_SZ)

    can.drawRightString(x=pageWidth - 50, y=pageHeight - 30, text=str(pgNum))

    can.save()
    packet.seek(0)

    return PdfReader(packet).pages[0]


def check_all_files_used(directory_path: str, targets):
    # checking if all files found in dir
    targetPath = Path(directory_path)
    files = [p for p in targetPath.rglob("*.pdf") if p.is_file()]
    for file in files:
        if file.name not in targets:
            print(f"NOTE: {file.name} not assigned to current operation")
    del targetPath


if __name__ == "__main__":
    manifestPath = DEFAULT_MANIFEST_PATH

    if len(sys.argv) > 2:
        print(ERR_USAGE, file=sys.stderr)
        _exit(-1)

    elif len(sys.argv) == 2:
        manifestPath = sys.argv[1]

    try:
        with open(manifestPath, "r") as file:
            data = json.load(file)

    except FileNotFoundError:
        print(ERR_NO_MANIFEST, file=sys.stderr)
        _exit(-1)

    # TODO: check for output filename
    # TODO: check for page number location
    # TODO: check for font
    # TODO: check for font size

    if "targets" not in data or "target-folder" not in data:
        print(ERR_BAD_FORMAT, file=sys.stderr)
        _exit(-1)
    elif len(data["targets"]) < 1:
        print(ERR_EMPTY_MANIFEST, file=sys.stderr)
        _exit(-1)

    #! everything here works atp!#
    targetFolder = data["target-folder"]

    targets = data["targets"]
    if (
        type(targetFolder) is not str
        or type(targets) is not list
        or not 1 < len(targets)
    ):
        print(ERR_BAD_FORMAT, file=sys.stderr)
        _exit(-1)

    check_all_files_used(data["target-folder"], targets)
    targets = [targetFolder + o for o in targets]

    # TODO: check if all target files are found
    # TODO: maybe check if all files in directory are mentioned in manifest

    writer = PdfWriter()

    pdfs = [PdfReader(file) for file in targets]
    # pgCount = 0
    pageNum = 1

    for reader in pdfs:

        pages = reader.pages
        # pgCount += len(pages)

        for page in pages:
            overlay = write_page_nums(pageNum)
            page.merge_page(overlay)

            writer.add_page(page)
            pageNum += 1

    # write to output file
    with open(OUTPUT_FILE, "wb") as f:
        writer.write(f)

    _exit(0)
