from library import scan_library
from gui import TVBox


library = scan_library("/home/gleb/Downloads/tv-box/media")

app = TVBox(library)
app.run()
