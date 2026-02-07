from gi.repository import Gtk, Adw, Gio

class SettingsDialog(Adw.PreferencesWindow):
    def __init__(self, app, logic, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.logic = logic
        
        self.set_title("Configurações")
        self.set_default_size(500, 400)
        self.set_modal(True)
        
        # General Page
        page = Adw.PreferencesPage()
        page.set_title("Geral")
        page.set_icon_name("emblem-system-symbolic")
        self.add(page)
        
        # Notifications Group
        notif_group = Adw.PreferencesGroup()
        notif_group.set_title("Notificações")
        notif_group.set_description("Gerenciar lembretes de estudos.")
        page.add(notif_group)
        
        # Test Notification Row
        test_row = Adw.ActionRow()
        test_row.set_title("Testar Notificação")
        test_row.set_subtitle("Envia uma notificação de teste agora.")
        
        test_btn = Gtk.Button(label="Testar")
        test_btn.set_valign(Gtk.Align.CENTER)
        test_btn.connect("clicked", self.on_test_clicked)
        
        test_row.add_suffix(test_btn)
        notif_group.add(test_row)
        
        # Check Today's Revisions Row (Manual Trigger)
        check_row = Adw.ActionRow()
        check_row.set_title("Verificar Estudos de Hoje")
        check_row.set_subtitle("Força uma verificação de revisão.")
        
        check_btn = Gtk.Button(label="Verificar")
        check_btn.set_valign(Gtk.Align.CENTER)
        check_btn.connect("clicked", self.on_check_clicked)
        
        check_row.add_suffix(check_btn)
        check_row.add_suffix(check_btn)
        notif_group.add(check_row)

        # Danger Zone
        danger_group = Adw.PreferencesGroup()
        danger_group.set_title("Zona de Perigo")
        danger_group.add_css_class("error") 
        page.add(danger_group)

        reset_row = Adw.ActionRow()
        reset_row.set_title("Resetar Banco de Dados")
        reset_row.set_subtitle("Apaga TODOS os dados. Irreversível.")
        
        reset_btn = Gtk.Button(label="Resetar")
        reset_btn.add_css_class("destructive-action")
        reset_btn.set_valign(Gtk.Align.CENTER)
        reset_btn.connect("clicked", self.on_reset_clicked)
        
        reset_row.add_suffix(reset_btn)
        danger_group.add(reset_row)

    def on_test_clicked(self, btn):
        self.app.send_notification("Teste de Notificação", "O sistema de notificações do Review está funcionando!")

    def on_check_clicked(self, btn):
        self.app.check_and_notify_revisions(self.logic)

    def on_reset_clicked(self, btn):
        # Double Confirmation Dialog
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading="Tem certeza absoluta?",
            body="Esta ação apagará TODOS os tópicos, áreas, tags e histórico de revisões. Não pode ser desfeita."
        )
        dialog.add_response("cancel", "Cancelar")
        dialog.add_response("reset", "SIM, APAGAR TUDO")
        dialog.set_response_appearance("reset", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response", self.on_reset_confirm)
        dialog.present()

    def on_reset_confirm(self, dialog, response):
        if response == "reset":
            # Second confirmation just to be safe (requested double confirmation)
            dialog.destroy()
            
            confirm2 = Adw.MessageDialog(
                 transient_for=self,
                 heading="Confirmação Final",
                 body="Última chance. Deseja realmente resetar o banco de dados?"
            )
            confirm2.add_response("cancel", "Cancelar")
            confirm2.add_response("destroy", "APAGAR")
            confirm2.set_response_appearance("destroy", Adw.ResponseAppearance.DESTRUCTIVE)
            confirm2.connect("response", self.on_reset_final)
            confirm2.present()
        else:
            dialog.destroy()

    def on_reset_final(self, dialog, response):
        if response == "destroy":
            self.logic.db.reset_database()
            self.app.send_notification("Banco de Dados Resetado", "Todos os dados foram apagados com sucesso.")
            # Trigger refresh if possible via app, but logic is tied, maybe close dialog
        dialog.destroy()
