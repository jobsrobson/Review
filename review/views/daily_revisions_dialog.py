from gi.repository import Gtk, Adw, GObject
from ..utils import db_to_ui_date

class DailyRevisionsDialog(Adw.Window):
    def __init__(self, date_str, revisions, logic, refresh_callback, edit_callback, **kwargs):
        super().__init__(**kwargs)
        self.logic = logic
        self.refresh_callback = refresh_callback
        self.edit_callback = edit_callback
        self.revisions = revisions
        
        self.set_title(f"Revisões do Dia {db_to_ui_date(date_str)}")
        self.set_default_size(500, 600)
        self.set_modal(True)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)
        
        header = Adw.HeaderBar()
        main_box.append(header)
        
        sub_title = Gtk.Label(label=f"Total: {len(revisions)} revisões")
        sub_title.add_css_class("dim-label")
        sub_title.set_margin_bottom(12)
        main_box.append(sub_title)
        
        # Scrolled List
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        main_box.append(scrolled)
        
        list_box = Gtk.ListBox()
        list_box.add_css_class("boxed-list")
        list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        list_box.set_margin_top(12)
        list_box.set_margin_bottom(12)
        list_box.set_margin_start(12)
        list_box.set_margin_end(12)
        scrolled.set_child(list_box)
        
        for rev in revisions:
            # Same logic as Popover but for all items
            # rev: (id, topic_id, scheduled_date, status, interval_days, title, area, color)
            rev_id, topic_id, _, status, interval, title, area, _ = rev
            
            row = Adw.ActionRow(title=title, subtitle=f"{area} • Intervalo: {interval} dias")
            
             # Color indicator
            if len(rev) > 7 and rev[7]:
                dot = Gtk.Box()
                dot.set_size_request(8, 8)
                dot.set_valign(Gtk.Align.CENTER)
                provider = Gtk.CssProvider()
                css = f"* {{ background-color: {rev[7]}; border-radius: 50%; }}"
                provider.load_from_data(css.encode())
                context = dot.get_style_context()
                context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                row.add_prefix(dot)
            
            if status == 'studied':
                row.add_css_class("dim-label")
            
            if status == 'pending':
                btn_ok = Gtk.Button(icon_name="object-select-symbolic")
                btn_ok.add_css_class("flat")
                btn_ok.add_css_class("success")
                btn_ok.set_valign(Gtk.Align.CENTER)
                btn_ok.connect("clicked", self.on_action, rev_id, topic_id, 'studied')
                row.add_suffix(btn_ok)
                
                btn_no = Gtk.Button(icon_name="media-skip-forward-symbolic")
                btn_no.add_css_class("flat")
                btn_no.add_css_class("error")
                btn_no.set_valign(Gtk.Align.CENTER)
                btn_no.connect("clicked", self.on_action, rev_id, topic_id, 'missed')
                row.add_suffix(btn_no)

                # Play Button (Only if pending)
                btn_play = Gtk.Button(icon_name="media-playback-start-symbolic")
                btn_play.add_css_class("suggested-action")
                btn_play.set_valign(Gtk.Align.CENTER)
                btn_play.set_tooltip_text("Iniciar Estudo")
                btn_play.connect("clicked", self.on_play_clicked, topic_id, title)
                row.add_suffix(btn_play)
            elif status == 'studied':
                btn_undo = Gtk.Button(icon_name="edit-undo-symbolic")
                btn_undo.add_css_class("flat")
                btn_undo.set_tooltip_text("Desfazer conclusão")
                btn_undo.set_valign(Gtk.Align.CENTER)
                btn_undo.connect("clicked", self.on_action, rev_id, topic_id, 'undo_studied')
                row.add_suffix(btn_undo)
            
            btn_edit = Gtk.Button(icon_name="document-edit-symbolic")
            btn_edit.add_css_class("flat")
            btn_edit.set_valign(Gtk.Align.CENTER)
            btn_edit.set_tooltip_text("Editar Tópico")
            btn_edit.connect("clicked", self.on_edit_clicked, topic_id)
            row.add_suffix(btn_edit)
            
            list_box.append(row)

    def on_action(self, btn, rev_id, topic_id, action):
        if action == 'studied':
            self.logic.mark_as_studied(rev_id)
        elif action == 'undo_studied':
            self.logic.mark_as_pending(rev_id)
        else:
            self.logic.mark_as_not_studied(rev_id, topic_id)
        
        if self.refresh_callback:
            self.refresh_callback()
            
        self.close() # Close for simplicity to update main view

    def on_edit_clicked(self, btn, topic_id):
        self.close()
        if self.edit_callback:
            self.edit_callback(topic_id)

    def on_play_clicked(self, btn, topic_id, title):
        self.close()
        # Find window to start timer
        win = self.get_transient_for() # Should be ReviewWindow
        if hasattr(win, 'start_timer'):
            win.start_timer(topic_id, title)
