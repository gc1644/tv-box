from library import scan_library
from gui import TVBox


library = scan_library("/home/kotki/Videos")

app = TVBox(library)
app.run()
