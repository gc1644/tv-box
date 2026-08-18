from library import scan_library
from gui import TVBox


library = scan_library("media")

app = TVBox(library)
app.run()
