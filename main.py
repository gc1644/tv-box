from pathlib import Path

from library import scan_library
from gui import TVBox


library = scan_library(
    Path.home() / "Videos"
)

app = TVBox(library)
app.run()
