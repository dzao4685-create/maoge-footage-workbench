from pathlib import Path
from zipfile import ZipFile
with ZipFile(Path(__file__).with_name("library.zip")) as archive:
    for name in archive.namelist():
        if name.startswith("public/"):
            archive.extract(name, Path(__file__).parent)
print("Cloudflare Pages static site extracted to public/")
