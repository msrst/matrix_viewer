
registered_viewers = set()
last_viewer = None

def register(viewer):
    global last_viewer
    assert viewer not in registered_viewers
    registered_viewers.add(viewer)
    last_viewer = viewer

def unregister(viewer):
    global last_viewer
    assert viewer in registered_viewers
    registered_viewers.discard(viewer)
    if viewer == last_viewer:
        last_viewer = None

def any_viewer():
    return last_viewer