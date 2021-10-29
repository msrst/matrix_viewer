
registered_viewers = set()

def register(viewer):
    assert viewer not in registered_viewers
    registered_viewers.add(viewer)

def unregister(viewer):
    assert viewer in registered_viewers
    registered_viewers.discard(viewer)

def any_viewer():
    return list(registered_viewers)[0]