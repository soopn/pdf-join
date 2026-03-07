import io
import json
from os import _exit
import sys
from pypdf import PdfWriter, PdfReader
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utilities import *

pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", "arialbd.ttf"))

# TODO: could get rid of printing to stderr
# TODO: make it rewrite the manifest

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


def load_manifest():
    try:
        with open(manifestPath, "r") as file:
            data = json.load(file)

    except FileNotFoundError:
        print(ERR_NO_MANIFEST, file=sys.stderr)
        _exit(-1)
    return data


def verify_manifest(manifest):
    if "targets" not in manifest or "target-folder" not in manifest:
        print(ERR_BAD_FORMAT, file=sys.stderr)
        _exit(-1)

    if len(manifest["targets"]) < 1:
        print(ERR_EMPTY_MANIFEST, file=sys.stderr)
        _exit(-1)

    if "output-file" not in manifest:
        print("Error: No output file specified")

    if "font" not in manifest:
        print("NOTE: No font specified, defaulting to Arial-Bold")

    if "font-size" not in manifest:
        print("NOTE: No font size specified, defaulting to 18pt")

    if "page-number-location" not in manifest:
        print("NOTE: No location specified, defaulting to top-right")

    if (
        type(manifest["target-folder"]) is not str
        or type(manifest["targets"]) is not list
        or not 1 < len(manifest["targets"])
    ):
        print(ERR_BAD_FORMAT, file=sys.stderr)
        _exit(-1)


def format_file_list(files, toProcess, order):
    string_builder = ""

    for i in range(toProcess):
        string_builder += f"""{i}. {files[i]}\n"""

    string_builder += ", ".join(order) + "\n"
    return string_builder


def prompt_create_manifest():
    # BUG: \targets is broken
    valid = False

    while not valid:
        choice = input(
            """Manifest not found, would you like to create one?\n1. Create new manifest\n2. Exit program\n"""
        )
        if choice == "1":
            valid = True
        elif choice == "2":
            exit(0)

    targetDir = input(
        f"""Please designate path to target pdf files\n{Path.cwd()}\\"""
    )

    files = [p.name for p in Path(targetDir).rglob("*.pdf") if p.is_file()]
    targets = []
    targetDir = str(Path.cwd()) + "\\" + targetDir + "\\"

    toProcess = len(files)
    while toProcess > 1:
        prompt = f"""Please designate the order of the files you would like to merge\n{format_file_list(files, toProcess, targets)}"""

        target = input(prompt)
        if not int(target) in range(toProcess):
            continue

        targets.append(targetDir + files[int(target)])
        toProcess -= 1

    output = input(
        f"Please designate an output file (without the .pdf)\n{Path.cwd()}\\"
    )

    output = str(Path.cwd()) + "\\" + output + ".pdf"

    return (targetDir, targets, output)


if __name__ == "__main__":
    manifestPath = DEFAULT_MANIFEST_PATH

    if not Path("manifest.json").exists():
        (targetFolder, targets, outputFile) = prompt_create_manifest()
        OUTPUT_FILE = outputFile
    else:
        data = load_manifest()
        verify_manifest(data)

        #! everything here works atp!#
        targetFolder = data["target-folder"]
        targets = data["targets"]

        check_all_files_used(data["target-folder"], targets)

        # add target directory to filename
        targets = [targetFolder + o for o in targets]

    writer = PdfWriter()

    # print(targets)
    pdfs = [PdfReader(file) for file in targets]
    pageNum = 1

    for reader in pdfs:

        pages = reader.pages
        for page in pages:
            overlay = write_page_nums(pageNum)
            page.merge_page(overlay)

            writer.add_page(page)
            pageNum += 1

    # write to output file
    with open(OUTPUT_FILE, "wb") as f:
        writer.write(f)

    _exit(0)
