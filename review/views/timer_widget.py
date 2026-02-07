from gi.repository import Gtk, Adw, GLib, GObject
import time

class TimerWidget(Gtk.Box):
    __gsignals__ = {
        'session-finished': (GObject.SignalFlags.RUN_FIRST, None, (int, int)), # topic_id, duration
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_spacing(12)
        self.set_visible(False) # Hidden by default
        # self.set_halign(Gtk.Align.CENTER) # Removed for full width
        # self.set_margin_top(12) 
        # self.set_margin_bottom(12) # Removed margin so it touches bottom edge if needed
        # Or keep small margin for "floating" look.
        # "estique-o horizontalmente até as bordas" -> usually means no margin or full width.
        # "flutuando na parte de baixo" -> implies simple overlay positioning.
        
        self.set_halign(Gtk.Align.FILL)
        self.set_hexpand(True)
        
        self.topic_id = None
        self.start_time = 0
        self.elapsed = 0
        self.timer_id = None
        self.is_paused = False
        
        # UI Styling
        self.add_css_class("timer-banner")
        
        # Custom CSS for banner appearance
        provider = Gtk.CssProvider()
        css = """
        .timer-banner {
            background-color: @accent_bg_color;
            color: @accent_fg_color;
            border-radius: 0px; 
            padding: 6px 12px; 
            font-weight: bold;
        }
        .timer-banner label {
            color: @accent_fg_color;
        }
        
        .huge-timer {
            font-size: 120px;
            font-weight: bold;
        }
        .timer-banner button {
             color: @accent_fg_color;
             background: rgba(255, 255, 255, 0.2);
             border: none;
             box-shadow: none;
        }
        .timer-banner button:hover {
             background: rgba(255, 255, 255, 0.4);
        }
        """
        provider.load_from_data(css.encode())
        context = self.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        # State
        self.is_fullscreen = False
        
        # Main Layout: Stack
        self.stack = Gtk.Stack()
        self.stack.set_vhomogeneous(False)
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.append(self.stack)

        # --- View 1: Banner ---
        self.banner_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        
        # Click controller for expansion
        click_ctrl = Gtk.GestureClick()
        click_ctrl.connect("released", self.on_banner_clicked)
        self.banner_box.add_controller(click_ctrl)
        
        # Access: we need to update these labels, so store references
        spacer1 = Gtk.Label()
        spacer1.set_hexpand(True)
        self.banner_box.append(spacer1)

        icon = Gtk.Image.new_from_icon_name("view-reveal-symbolic")
        self.banner_box.append(icon)
        
        self.status_label = Gtk.Label()
        self.banner_box.append(self.status_label)
        
        self.time_label = Gtk.Label(label="00:00")
        self.time_label.add_css_class("numerical") 
        self.banner_box.append(self.time_label)
        
        self.btn_pause = Gtk.Button(icon_name="media-playback-pause-symbolic")
        self.btn_pause.connect("clicked", self.on_pause_clicked)
        self.banner_box.append(self.btn_pause)
        
        self.btn_stop = Gtk.Button(icon_name="media-playback-stop-symbolic")
        self.btn_stop.connect("clicked", self.on_stop_clicked)
        self.banner_box.append(self.btn_stop)
        
        spacer2 = Gtk.Label()
        spacer2.set_hexpand(True)
        self.banner_box.append(spacer2)
        
        self.stack.add_named(self.banner_box, "banner")
        
        # --- View 2: Fullscreen ---
        self.full_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        self.full_box.set_valign(Gtk.Align.CENTER)
        self.full_box.set_halign(Gtk.Align.CENTER)
        
        # Minimize button container (to place it at top right or convenient place)
        # Actually, full_box is centered. We want the minimize button maybe at top right of the whole widget?
        # Let's put minimize button inside full_box for now, or use a Overlay inside overlay? 
        # Simpler: A top box in Fullscreen view.
        
        # We need a wrapper for full screen to align content center but have button top.
        # Add WindowHandle to allow dragging
        self.drag_handle = Gtk.WindowHandle()
        self.full_wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.drag_handle.set_child(self.full_wrapper)
        
        # Top bar for minimize
        top_bar = Gtk.Box()
        top_bar.set_margin_top(24)
        top_bar.set_margin_end(24)
        top_bar.set_halign(Gtk.Align.END)
        
        btn_min = Gtk.Button(icon_name="go-down-symbolic")
        btn_min.add_css_class("circular")
        btn_min.set_tooltip_text("Minimizar")
        btn_min.connect("clicked", self.on_minimize_clicked)
        # Style it to look good on accent bg
        btn_min.add_css_class("flat") 
        top_bar.append(btn_min)
        self.full_wrapper.append(top_bar)
        
        # Center Content
        self.full_box.set_vexpand(True)
        
        self.full_topic_label = Gtk.Label()
        self.full_topic_label.add_css_class("title-3") # Reduced size
        self.full_topic_label.set_wrap(True)
        self.full_topic_label.set_justify(Gtk.Justification.CENTER)
        self.full_topic_label.set_max_width_chars(30)
        self.full_box.append(self.full_topic_label)
        
        self.full_time_label = Gtk.Label(label="00:00")
        self.full_time_label.add_css_class("huge-timer") # Custom Huge Size
        self.full_time_label.add_css_class("numeric")
        self.full_box.append(self.full_time_label)
        
        # Controls Row
        ctl_box = Gtk.Box(spacing=32)
        ctl_box.set_halign(Gtk.Align.CENTER)
        
        self.full_btn_pause = Gtk.Button(icon_name="media-playback-pause-symbolic")
        self.full_btn_pause.set_size_request(64, 64)
        self.full_btn_pause.add_css_class("circular")
        self.full_btn_pause.connect("clicked", self.on_pause_clicked)
        ctl_box.append(self.full_btn_pause)
        
        self.full_btn_stop = Gtk.Button(icon_name="media-playback-stop-symbolic")
        self.full_btn_stop.set_size_request(64, 64)
        self.full_btn_stop.add_css_class("circular")
        self.full_btn_stop.connect("clicked", self.on_stop_clicked)
        ctl_box.append(self.full_btn_stop)
        
        self.full_box.append(ctl_box)
        self.full_wrapper.append(self.full_box)
        
        self.stack.add_named(self.drag_handle, "fullscreen")

    def start_session(self, topic_id, topic_title):
        if self.timer_id:
            self.stop_session() # Stop previous if any
            
        self.topic_id = topic_id
        self.start_time = time.time()
        self.elapsed = 0
        self.is_paused = False
        
        display_title = topic_title
        if len(display_title) > 50:
            display_title = display_title[:47] + "..."
            
        self.status_label.set_text(f"Estudando: {display_title}")
        self.time_label.set_text("00:00")
        self.btn_pause.set_icon_name("media-playback-pause-symbolic")
        
        # Fullscreen labels
        self.full_topic_label.set_text(topic_title)
        # Use simple text to clear, on_tick will update markup
        self.full_time_label.set_text("00:00")
        self.full_btn_pause.set_icon_name("media-playback-pause-symbolic")
        
        self.set_visible(True)
        self.timer_id = GLib.timeout_add(1000, self.on_tick)
        # Initial call to set correct initial text/markup
        self.on_tick()
        
        # Ensure we start in banner mode
        if self.is_fullscreen:
             self.on_minimize_clicked(None)

    def on_tick(self):
        # We run this even if paused to refresh display? No, only on tick.
        # But we called it manually in start_session.
        
        elapsed = self.elapsed
        if not self.is_paused and self.timer_id:
             elapsed = int(time.time() - self.start_time)
             self.elapsed = elapsed
             
        mins, secs = divmod(elapsed, 60)
        hours, mins = divmod(mins, 60)
        
        txt = f"{mins:02}:{secs:02}"
        if hours > 0:
            txt = f"{hours:02}:{mins:02}:{secs:02}"
            
        self.time_label.set_text(txt)
        
        # Use Pango Markup for Fullscreen Label to force size
        markup = f"<span font='120' weight='bold'>{txt}</span>"
        self.full_time_label.set_markup(markup)
                
        return True

    def on_banner_clicked(self, gesture, n_press, x, y):
        self.set_valign(Gtk.Align.FILL)
        self.stack.set_visible_child_name("fullscreen")
        self.is_fullscreen = True
        
    def on_minimize_clicked(self, btn):
        self.set_valign(Gtk.Align.END)
        self.stack.set_visible_child_name("banner")
        self.is_fullscreen = False

    def on_pause_clicked(self, btn):
        if self.is_paused:
            # Resume
            self.is_paused = False
            self.start_time = time.time() - self.elapsed
            icon = "media-playback-pause-symbolic"
        else:
            # Pause
            self.is_paused = True
            icon = "media-playback-start-symbolic"
            
        self.btn_pause.set_icon_name(icon)
        self.full_btn_pause.set_icon_name(icon)

    def on_stop_clicked(self, btn):
        self.stop_session()

    def stop_session(self):
        if self.timer_id:
            GLib.source_remove(self.timer_id)
            self.timer_id = None
        
        # Reset to banner mode if in fullscreen
        if self.is_fullscreen:
            self.set_valign(Gtk.Align.END)
            self.stack.set_visible_child_name("banner")
            self.is_fullscreen = False
            
        self.emit('session-finished', self.topic_id, self.elapsed)
        self.set_visible(False)
