import tkinter as tk


class ManagerSingleton:
    def __init__(self):
        self.registered_viewers = set()
        self.last_viewer = None
        self.tk_root = None
        self.event_loop_id = None
        self.mainloop_running = False

    def register(self, viewer):
        assert viewer not in self.registered_viewers
        self.registered_viewers.add(viewer)
        self.last_viewer = viewer

    def unregister(self, viewer):
        assert viewer in self.registered_viewers
        self.registered_viewers.discard(viewer)
        if viewer == self.last_viewer:
            self.last_viewer = None

        if len(self.registered_viewers) == 0:  # all windows are closed now
            if self.mainloop_running:
                self.stop_event_loop()

    def any_viewer(self):
        return self.last_viewer

    def get_or_create_root(self):
        if self.tk_root is None:
            self.tk_root = tk.Tk()
            # Usually, tk apps have a main window created with tk.Tk() and child windows created with tk.Toplevel. But the child
            # windows are all closed if the main window is closed. Therefore, we cannot use the main window here. Instead, hide
            # it and only create child windows.
            # self.tk_root.overrideredirect(1)  # prevents flashing up window
            self.tk_root.withdraw()
        return self.tk_root

    def show(self, block=True):
        if block:
            self.mainloop_running = True
            self.tk_root.mainloop()
            self.mainloop_running = False
        else:
            pass

    def pause(self, timeout):
        # timeout: in seconds

        milliseconds = int(1000 * timeout)
        if milliseconds > 0:
            self.event_loop_id = self.tk_root.after(milliseconds, self.stop_event_loop)
        else:
            self.event_loop_id = self.tk_root.after_idle(self.stop_event_loop)

        self.mainloop_running = True
        self.tk_root.mainloop()
        self.mainloop_running = False

    def stop_event_loop(self):
        if self.event_loop_id:
            self.tk_root.after_cancel(self.event_loop_id)
            self.event_loop_id = None
        self.tk_root.quit()

manager = ManagerSingleton()
