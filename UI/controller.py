import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

    def fillDDsYears(self):
        anni = self._model.getYears()
        if not anni:
            self._view.create_alert("Errore nel caricamento degli anni dal database")
            return
        for a in anni:
            self._view._ddanno1.options.append(ft.dropdown.Option(str(a)))
            self._view._ddanno2.options.append(ft.dropdown.Option(str(a)))

    def handleCreaGrafo(self, e):
        # --- 1. lettura e validazione input ---
        v1 = self._view._ddanno1.value
        v2 = self._view._ddanno2.value
        if v1 is None or v2 is None:
            self._view.create_alert("Selezionare entrambi gli anni")
            return
        try:
            annoMin = int(v1)
            annoMax = int(v2)
        except ValueError:
            self._view.create_alert("Valori degli anni non validi")
            return
        if annoMin > annoMax:
            self._view.create_alert("Il primo anno deve essere minore o uguale al secondo")
            return

        # --- 2. delega al model ---
        self._model.buildGraph(annoMin, annoMax)

        # --- 3. stampa dei risultati ---
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text("Grafo correttamente creato:"))
        self._view.txt_result.controls.append(ft.Text(f"Numero di nodi: {self._model.getNumNodi()}"))
        self._view.txt_result.controls.append(ft.Text(f"Numero di archi: {self._model.getNumArchi()}"))

        self._view.txt_result.controls.append(ft.Text("Top 5 archi:"))
        for f1, f2, peso in self._model.getTop5Archi():
            self._view.txt_result.controls.append(ft.Text(f"{f1.title} -> {f2.title} : {peso}"))

        self._view.txt_result.controls.append(
            ft.Text(f"Il grafo ha {self._model.getNumComponenti()} componenti connesse"))
        maxComp = self._model.getMaxComponente()
        self._view.txt_result.controls.append(
            ft.Text(f"La più grande componente connessa è lunga {len(maxComp)}:"))
        for film in maxComp:
            self._view.txt_result.controls.append(ft.Text(str(film)))

        # --- 4. statistiche extra (senza input) ---
        gradoMax = self._model.getNodoGradoMax()
        if gradoMax is not None:
            film, grado = gradoMax
            self._view.txt_result.controls.append(
                ft.Text(f"Film con più collegamenti: {film.title} ({grado} film collegati)"))

        gradoPesatoMax = self._model.getNodoGradoPesatoMax()
        if gradoPesatoMax is not None:
            film, gp = gradoPesatoMax
            self._view.txt_result.controls.append(
                ft.Text(f"Film che condivide più attori: {film.title} ({gp} attori in totale)"))

        self._view.txt_result.controls.append(
            ft.Text(f"Peso totale del grafo: {self._model.getPesoTotale()}"))

        self._view.txt_result.controls.append(
            ft.Text(f"Nodi isolati: {self._model.getNumIsolati()}"))

        self._view.txt_result.controls.append(ft.Text("Top 5 film per grado:"))
        for film, grado in self._model.getTop5Gradi():
            self._view.txt_result.controls.append(ft.Text(f"{film.title}: {grado}"))

        comp, peso = self._model.getComponentePesoMax()
        self._view.txt_result.controls.append(
            ft.Text(f"Componente di peso massimo: {len(comp)} film, peso {peso}"))

        self._view.update_page()

    def handleCammino(self, e):
        if self._model.getNumNodi() == 0:
            self._view.create_alert("Creare prima il grafo")
            return

        cammino = self._model.getCamminoMax()
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(
            ft.Text(f"Il cammino più lungo ha {len(cammino)} film:"))
        for film in cammino:
            self._view.txt_result.controls.append(
                ft.Text(f"{film.title} ({film.year}) - durata {film.durata} min"))
        self._view.update_page()