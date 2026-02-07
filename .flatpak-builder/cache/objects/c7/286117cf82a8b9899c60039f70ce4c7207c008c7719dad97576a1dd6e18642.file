from gi.repository import Gtk, Adw, Gio, Gdk, GLib
from .models import RevisionLogic
import os
from .window import ReviewWindow

class ReviewApplication(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(application_id='com.github.jobsr.Review',
                         flags=Gio.ApplicationFlags.FLAGS_NONE,
                         **kwargs)
        self.logic = None

    def do_startup(self):
        Adw.Application.do_startup(self)
        # Add custom icons to theme search path
        icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        icons_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
        icon_theme.add_search_path(icons_path)

        self.logic = RevisionLogic()
        
        # Check immediately on startup
        self.check_and_notify_revisions(self.logic)
        
        # Check every 4 hours (timeout is in milliseconds)
        # 4 hours * 60 mins * 60 secs * 1000 ms = 14400000
        GLib.timeout_add(14400000, self.on_timeout_check)

    def on_timeout_check(self):
        self.check_and_notify_revisions(self.logic)
        return True # Return True to keep the timeout active

    def do_activate(self):
        # Load CSS
        style_provider = Gtk.CssProvider()
        css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'style.css')
        style_provider.load_from_path(css_path)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        win = self.get_active_window()
        if not win:
            win = ReviewWindow(application=self)
        win.present()

    def send_notification(self, title, body):
        notification = Gio.Notification.new(title)
        notification.set_body(body)
        notification.set_icon(Gio.ThemedIcon.new("view-list-bullet-symbolic"))
        print(f"DEBUG: Attempting to send notification: {title} - {body}")
        try:
           super().send_notification("review-notification", notification)
           print("DEBUG: Notification sent to system.")
        except Exception as e:
           print(f"DEBUG: Failed to send notification: {e}")

    def check_and_notify_revisions(self, logic):
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        revisions = logic.get_upcoming_revisions(today)
        
        pending_count = sum(1 for rev in revisions if rev[3] == 'pending')
        
        if pending_count > 0:
            title = "Estudos Pendentes"
            body = f"Você tem {pending_count} tópico(s) para revisar hoje!"
            self.send_notification(title, body)
        else:
            self.send_notification("Tudo em dia!", "Nenhuma revisão pendente para hoje.")
