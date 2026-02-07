from gi.repository import Gtk, Adw, Gio, GLib
from datetime import datetime

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

        # Backup & Restore
        backup_group = Adw.PreferencesGroup()
        backup_group.set_title("Backup e Restauração")
        backup_group.set_description("Gerenciar cópias de segurança dos seus dados.")
        page.add(backup_group)

        # Export Row
        export_row = Adw.ActionRow()
        export_row.set_title("Exportar Banco de Dados")
        export_row.set_subtitle("Salva uma cópia de segurança de todos os seus estudos.")
        
        export_btn = Gtk.Button(label="Exportar")
        export_btn.set_valign(Gtk.Align.CENTER)
        export_btn.connect("clicked", self.on_export_clicked)
        
        export_row.add_suffix(export_btn)
        backup_group.add(export_row)

        # Import Row
        import_row = Adw.ActionRow()
        import_row.set_title("Importar Banco de Dados")
        import_row.set_subtitle("Restaura seus dados a partir de um arquivo anterior.")
        
        import_btn = Gtk.Button(label="Importar")
        import_btn.set_valign(Gtk.Align.CENTER)
        import_btn.connect("clicked", self.on_import_clicked)
        
        import_row.add_suffix(import_btn)
        backup_group.add(import_row)

    def on_export_clicked(self, btn):
        dialog = Gtk.FileDialog(title="Exportar Banco de Dados")
        # Suggest a filename
        now = datetime.now().strftime("%Y-%m-%d_%H-%M")
        dialog.set_initial_name(f"review_backup_{now}.db")
        
        filter_db = Gtk.FileFilter()
        filter_db.set_name("Arquivo de Banco de Dados (.db)")
        filter_db.add_pattern("*.db")
        
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_db)
        dialog.set_filters(filters)
        
        dialog.save(self, None, self.on_export_finish)

    def on_export_finish(self, dialog, result):
        try:
            file = dialog.save_finish(result)
            if file:
                self.export_path = file.get_path()
                self._ask_export_password()
        except GLib.Error as e:
            print(f"Export cancelled or failed: {e}")

    def _ask_export_password(self):
        dlg = Adw.MessageDialog(
            transient_for=self,
            heading="Criptografar Backup?",
            body="Você pode proteger seu backup com uma senha. Se não desejar criptografar, clique em 'Exportar sem Senha'."
        )
        
        entry = Gtk.Entry()
        entry.set_visibility(False)
        entry.set_placeholder_text("Senha opcional")
        entry.set_activates_default(True)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(12)
        box.append(entry)
        dlg.set_extra_child(box)
        
        dlg.add_response("cancel", "Cancelar")
        dlg.add_response("no_pass", "Exportar sem Senha")
        dlg.add_response("with_pass", "Exportar com Senha")
        dlg.set_response_appearance("with_pass", Adw.ResponseAppearance.SUGGESTED)
        dlg.set_default_response("with_pass")
        
        def on_response(d, res):
            path = self.export_path
            if res == "no_pass":
                self._do_export(path, None)
            elif res == "with_pass":
                password = entry.get_text()
                if password:
                    self._do_export(path, password)
                else:
                    self.app.send_notification("Aviso", "Senha não fornecida. Exportando sem criptografia.")
                    self._do_export(path, None)
            d.destroy()
        
        dlg.connect("response", on_response)
        dlg.present()

    def _do_export(self, path, password):
        result = self.logic.db.export_database(path, password)
        if result is True:
            msg = "Backup criptografado salvo" if password else "Backup salvo"
            self.app.send_notification("Exportação Concluída", f"{msg} em: {path}")
        elif result == "CRYPTO_MISSING":
            self.app.send_notification("Erro: Criptografia Indisponível", "A biblioteca 'cryptography' não está instalada. Instale-a ou exporte sem senha.")
        else:
            self.app.send_notification("Erro na Exportação", "Não foi possível salvar o arquivo.")

    def on_import_clicked(self, btn):
        # Warning before import
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading="Importar Banco de Dados?",
            body="Esta ação substituirá TODOS os dados atuais pelos dados do arquivo selecionado. Deseja continuar?"
        )
        dialog.add_response("cancel", "Cancelar")
        dialog.add_response("import", "Continuar")
        dialog.set_response_appearance("import", Adw.ResponseAppearance.SUGGESTED)
        dialog.connect("response", self.on_import_confirm)
        dialog.present()

    def on_import_confirm(self, dialog, response):
        dialog.destroy()
        if response == "import":
            file_dialog = Gtk.FileDialog(title="Selecionar Arquivo de Backup")
            
            filter_db = Gtk.FileFilter()
            filter_db.set_name("Arquivo de Banco de Dados (.db)")
            filter_db.add_pattern("*.db")
            
            filters = Gio.ListStore.new(Gtk.FileFilter)
            filters.append(filter_db)
            file_dialog.set_filters(filters)
            
            file_dialog.open(self, None, self.on_import_finish)

    def on_import_finish(self, dialog, result):
        try:
            file = dialog.open_finish(result)
            if file:
                path = file.get_path()
                self._do_import(path)
        except GLib.Error as e:
            print(f"Import cancelled or failed: {e}")

    def _do_import(self, path, password=None):
        result = self.logic.db.import_database(path, password)
        if result is True:
            self.app.send_notification("Importação Concluída", "Seus dados foram restaurados com sucesso.")
            win = self.app.get_active_window()
            if win and hasattr(win, 'refresh_all_views'):
                win.refresh_all_views()
        elif result == "PASSWORD_REQUIRED":
            self._prompt_import_password(path, "Este backup está protegido por senha. Por favor, insira a senha para continuar.")
        elif result == "INVALID_PASSWORD":
            self._prompt_import_password(path, "Senha incorreta. Tente novamente.")
        elif result == "CRYPTO_MISSING":
            self.app.send_notification("Erro: Criptografia Indisponível", "A biblioteca 'cryptography' não está instalada. Não é possível descriptografar o arquivo.")
        else:
            self.app.send_notification("Erro na Importação", "Falha ao importar o arquivo. Verifique se é um banco de dados válido.")

    def _prompt_import_password(self, path, description):
        dlg = Adw.MessageDialog(
            transient_for=self,
            heading="Senha Requerida",
            body=description
        )
        
        entry = Gtk.Entry()
        entry.set_visibility(False)
        entry.set_placeholder_text("Senha")
        entry.set_activates_default(True)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(12)
        box.append(entry)
        dlg.set_extra_child(box)
        
        dlg.add_response("cancel", "Cancelar")
        dlg.add_response("ok", "OK")
        dlg.set_response_appearance("ok", Adw.ResponseAppearance.SUGGESTED)
        dlg.set_default_response("ok")
        
        def on_response(d, res):
            if res == "ok":
                password = entry.get_text()
                self._do_import(path, password)
            d.destroy()
        
        dlg.connect("response", on_response)
        dlg.present()

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
            # Trigger refresh to update UI immediately
            win = self.app.get_active_window()
            if win and hasattr(win, 'refresh_all_views'):
                win.refresh_all_views()
        dialog.destroy()
