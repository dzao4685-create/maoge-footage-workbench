from pathlib import Path
from zipfile import ZipFile
with ZipFile(Path(__file__).with_name("library.zip")) as archive:
    for name in archive.namelist():
        if name.startswith(("public/", "functions/")):
            archive.extract(name, Path(__file__).parent)
print("Cloudflare Pages site and functions extracted")

# Keep legacy theme URLs compatible with the flattened public archive.
import re
import shutil
public = Path(__file__).parent / 'public'
assets = public / 'theme-assets'
assets.mkdir(exist_ok=True)
for name in ('corner-bear.svg', 'corner-friends.svg'):
    source = public / name
    if source.is_file():
        shutil.copy2(source, assets / name)
css = public / 'corner-theme.css'
if css.is_file():
    text = css.read_text()
    text = re.sub(r"url\(['\"]?(?:theme-assets/)?corner-bear\.svg(?:\?[^'\")]+)?['\"]?\)", "url('theme-assets/corner-bear.svg?v=20261017-card-actions')", text)
    css.write_text(text)
index = public / 'index.html'
text = index.read_text()
text = re.sub(r'corner-theme\.css(?:\?[^"\s>]+)?', 'corner-theme.css?v=20261017-card-actions', text)
index.write_text(text)
print('Theme icon paths repaired')
