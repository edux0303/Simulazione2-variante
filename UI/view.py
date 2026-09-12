import flet as ft


class View(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        # page stuff
        self._page = page
        self._page.title = "Simulazione - Grafo dei film"
        self._page.horizontal_alignment = 'CENTER'
        self._page.theme_mode = ft.ThemeMode.LIGHT
        # controller (agganciato nel main, dopo la creazione)
        self._controller = None
        # graphical elements
        self._title = None
        self.txt_result = None

    def load_interface(self):
        # title
        self._title = ft.Text("TdP - Grafo dei film (attori in comune)", color="blue", size=24)
        self._page.controls.append(self._title)

        # dropdown degli ANNI (nascono vuoti: li riempie il controller dal DB)
        self._ddanno1 = ft.Dropdown(label="Anno", hint_text="Anno minimo")
        self._ddanno2 = ft.Dropdown(label="Anno", hint_text="Anno massimo")

        self._controller.fillDDsYears()

        self._btnCreaGrafo = ft.ElevatedButton(text="Crea Grafo",
                                               on_click=self._controller.handleCreaGrafo)

        row1 = ft.Row([self._ddanno1, self._ddanno2, self._btnCreaGrafo],
                      alignment=ft.MainAxisAlignment.CENTER,
                      vertical_alignment=ft.CrossAxisAlignment.END)
        self._page.controls.append(row1)

        self._btnCammino = ft.ElevatedButton(text="Trova Cammino",
                                             on_click=self._controller.handleCammino)

        row2 = ft.Row([self._btnCammino],
                      alignment=ft.MainAxisAlignment.CENTER)
        self._page.controls.append(row2)

        # List View where the reply is printed
        self.txt_result = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        self._page.controls.append(self.txt_result)
        self._page.update()

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller

    def set_controller(self, controller):
        self._controller = controller

    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message))
        self._page.dialog = dlg
        dlg.open = True
        self._page.update()

    def update_page(self):
        self._page.update()