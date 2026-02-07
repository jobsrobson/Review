from gi.repository import Gtk, Adw, GObject
from datetime import datetime
from .revision_popover import RevisionPopover
import re

HEX_COLOR_REGEX = re.compile(r"^(?:#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})|rgba?\([0-9\s,.]+\))$")

class DayCell(Gtk.MenuButton):
    def __init__(self, day, month, year, revisions, logic, refresh_callback, edit_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.day = day
        self.month = month
        self.year = year
        self.revisions = revisions
        self.logic = logic
        self.refresh_callback = refresh_callback
        self.edit_callback = edit_callback
        
        # Make cell responsive
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.add_css_class("flat")
        self.add_css_class("day-cell")
        
        # Content Box
        self.content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.content.set_margin_top(6)
        self.content.set_margin_bottom(6)
        self.content.set_margin_start(8)
        self.content.set_margin_end(8)
        self.set_child(self.content)
        
        # Day Number Header
        self.header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        self.header.append(spacer)
        
        day_label = Gtk.Label(label=str(day))
        day_label.add_css_class("caption")
        if day == datetime.now().day and month == datetime.now().month and year == datetime.now().year:
            day_label.add_css_class("today-label")
        
        self.header.append(day_label)
        self.content.append(self.header)
        
        # Revision Indicators Container
        self.indicators = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.indicators.set_margin_start(4)
        self.indicators.set_margin_end(4)
        self.content.append(self.indicators)
        
        self.add_indicators()
        
        # Popover setup (Standard HIG approach)
        date_str = f"{year}-{month:02d}-{day:02d}"
        popover = RevisionPopover(date_str, revisions, logic, refresh_callback, edit_callback)
        self.set_popover(popover)

    def add_indicators(self):
        # Show max 2 indicators to keep cells compact
        for rev in self.revisions[:2]:
            topic_title = rev[5]
            indicator = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            indicator.add_css_class("revision-indicator")
            
            dot = Gtk.Box()
            dot.set_size_request(4, 4)
            dot.set_valign(Gtk.Align.CENTER)
            dot.add_css_class("indicator-dot")
            
            # Apply color if available (index 7 from query)
            if len(rev) > 7 and rev[7]:
                col = rev[7]
                if isinstance(col, str) and HEX_COLOR_REGEX.match(col.strip()):
                    try:
                        provider = Gtk.CssProvider()
                        css = f"* {{ background-color: {col}; border-radius: 50%; }}"
                        provider.load_from_data(css.encode())
                        context = dot.get_style_context()
                        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                    except: pass
                
            indicator.append(dot)
            
            label = Gtk.Label(label=topic_title)
            label.set_ellipsize(3)
            label.set_max_width_chars(15)
            label.set_halign(Gtk.Align.START)
            label.add_css_class("caption")
            if rev[3] == 'studied':
                label.add_css_class("studied-text")
            
            indicator.append(label)
            self.indicators.append(indicator)
            
        if len(self.revisions) > 2:
            more_label = Gtk.Label(label=f"+{len(self.revisions) - 2} mais")
            more_label.add_css_class("caption")
            more_label.add_css_class("dim-label")
            self.indicators.append(more_label)

