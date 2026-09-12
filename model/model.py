import networkx as nx

from database.DAO import DAO


class Model:
    def __init__(self):
        self._grafo = nx.Graph()   # NON orientato (consegna) e pesato
        self._nodi = []            # lista di oggetti Film
        self._idMap = {}           # id film -> oggetto Film
        self._camminoBest = []     # risultato della ricorsione del punto 2

    def getYears(self):
        """Passa-carte verso il DAO per i dropdown degli anni."""
        return DAO.getYears()

    # ------------------------------------------------------------------
    # PUNTO 1b - costruzione del grafo
    # ------------------------------------------------------------------
    def buildGraph(self, annoMin, annoMax):
        self._grafo.clear()

        # --- NODI ---
        self._nodi = DAO.getNodi(annoMin, annoMax)
        self._idMap = {f.id: f for f in self._nodi}
        self._grafo.add_nodes_from(self._nodi)

        # --- ARCHI ---
        # getEdges restituisce UNA riga per arco, peso gia' contato dal COUNT:
        # niente dizionario pesi, niente pulizia stringhe
        for row in DAO.getEdges(annoMin, annoMax):
            if row["f1"] in self._idMap and row["f2"] in self._idMap:
                self._grafo.add_edge(self._idMap[row["f1"]],
                                     self._idMap[row["f2"]],
                                     weight=row["peso"])

    # ------------------------------------------------------------------
    # PUNTO 1c - statistiche (INVARIATE: lavorano sul grafo, non sul tipo dei nodi)
    # ------------------------------------------------------------------
    def getNumNodi(self):
        return len(self._grafo.nodes)

    def getNumArchi(self):
        return len(self._grafo.edges)

    def getTop5Archi(self):
        archi = sorted(self._grafo.edges(data=True),
                       key=lambda e: e[2]["weight"],
                       reverse=True)
        result = []
        for f1, f2, dati in archi[:5]:
            result.append((f1, f2, dati["weight"]))
        return result

    def getNumComponenti(self):
        return nx.number_connected_components(self._grafo)

    def getMaxComponente(self):
        if self.getNumNodi() == 0:
            return []
        return list(max(nx.connected_components(self._grafo), key=len))
    # ------------------------------------------------------------------
    # STATISTICHE EXTRA (possibili richieste alternative del punto 1c)
    # ------------------------------------------------------------------
    def getNodoGradoMax(self):
        """Il film con piu' film collegati. Restituisce (Film, grado) o None."""
        if self.getNumNodi() == 0:
            return None   # max() su sequenza vuota -> ValueError: va prevenuto
        return max(self._grafo.degree, key=lambda x: x[1])

    def getTop5Gradi(self):
        """I 5 nodi di grado massimo, come coppie (Film, grado)."""
        gradi = sorted(self._grafo.degree, key=lambda x: x[1], reverse=True)
        return gradi[:5]

    def getNodoGradoPesatoMax(self):
        """Il film che condivide piu' attori complessivamente (somma dei
        pesi dei suoi archi). Restituisce (Film, gradoPesato) o None."""
        if self.getNumNodi() == 0:
            return None
        return max(self._grafo.degree(weight="weight"), key=lambda x: x[1])

    def getPesoTotale(self):
        """Somma dei pesi di tutti gli archi del grafo."""
        return self._grafo.size(weight="weight")

    def getVicini(self, film):
        """I vicini del film dato, ordinati per peso dell'arco decrescente.
        Restituisce coppie (Film, pesoArco)."""
        if film not in self._grafo:
            return []   # film non nel grafo (o grafo non creato)
        vicini = []
        for v in self._grafo.neighbors(film):
            vicini.append((v, self._grafo[film][v]["weight"]))
        vicini.sort(key=lambda x: x[1], reverse=True)
        return vicini

    def getNumIsolati(self):
        """Quanti film non hanno nessun arco."""
        return len(list(nx.isolates(self._grafo)))

    def getDensita(self):
        return nx.density(self._grafo)

    def getArchiSopraSoglia(self, soglia):
        """Numero di archi con peso >= soglia."""
        return sum(1 for _, _, d in self._grafo.edges(data=True)
                   if d["weight"] >= soglia)

    def getComponenteDiFilm(self, film):
        """La componente connessa che contiene il film dato, come lista."""
        if film not in self._grafo:
            return []
        return list(nx.node_connected_component(self._grafo, film))

    def getComponentePesoMax(self):
        """La componente connessa il cui peso interno (somma dei pesi degli
        archi) e' massimo. Restituisce (listaFilm, pesoTotale)."""
        if self.getNumNodi() == 0:
            return [], 0
        bestComp = []
        bestPeso = -1
        for comp in nx.connected_components(self._grafo):
            peso = self._grafo.subgraph(comp).size(weight="weight")
            if peso > bestPeso:
                bestPeso = peso
                bestComp = list(comp)
        return bestComp, bestPeso
    # ------------------------------------------------------------------
    # PUNTO 2 - cammino semplice max con DURATA strettamente CRESCENTE
    # ------------------------------------------------------------------
    def getCamminoMax(self):
        self._camminoBest = []
        for nodo in self._grafo.nodes:
            self._ricorsione([nodo])
        return self._camminoBest

    def _ricorsione(self, parziale):
        if len(parziale) > len(self._camminoBest):
            self._camminoBest = list(parziale)   # copia!

        for vicino in self._grafo.neighbors(parziale[-1]):
            if vicino not in parziale and vicino.durata > parziale[-1].durata:
                parziale.append(vicino)
                self._ricorsione(parziale)
                parziale.pop()

    # ------------------------------------------------------------------
    # PUNTO 2 (variante sexies) - cammino tra due film che MASSIMIZZA
    # la somma dei pesi degli archi attraversati
    # ------------------------------------------------------------------
    def getCamminoMaxPeso(self, partenza, arrivo):
        self._camminoBest = []
        self._pesoBest = -1          # -1 = "nessun cammino trovato ancora"
        self._arrivo = arrivo
        self._ricorsionePeso([partenza], 0)
        return self._camminoBest, self._pesoBest

    def _ricorsionePeso(self, parziale, pesoTot):
        # salvo SOLO se sono arrivato a destinazione: un parziale
        # che non termina in 'arrivo' non e' una soluzione, per quanto pesante
        if parziale[-1] == self._arrivo:
            if pesoTot > self._pesoBest:
                self._pesoBest = pesoTot
                self._camminoBest = list(parziale)
            return   # oltre l'arrivo non ha senso proseguire

        for vicino in self._grafo.neighbors(parziale[-1]):
            if vicino not in parziale:
                pesoArco = self._grafo[parziale[-1]][vicino]["weight"]
                parziale.append(vicino)
                self._ricorsionePeso(parziale, pesoTot + pesoArco)
                parziale.pop()

    # ------------------------------------------------------------------
    # PUNTO 2 (variante ter) - cammino semplice massimo con pesi degli
    # archi strettamente crescenti lungo il percorso
    # ------------------------------------------------------------------
    def getCamminoPesiCrescenti(self):
        self._camminoBest = []
        for nodo in self._grafo.nodes:
            self._ricorsionePesi([nodo], -1)   # -1: il primo arco e' sempre ammesso
        return self._camminoBest

    def _ricorsionePesi(self, parziale, pesoPrec):
        # ogni parziale e' una soluzione valida: salvo se batte il record
        if len(parziale) > len(self._camminoBest):
            self._camminoBest = list(parziale)

        for vicino in self._grafo.neighbors(parziale[-1]):
            if vicino not in parziale:
                pesoArco = self._grafo[parziale[-1]][vicino]["weight"]
                if pesoArco > pesoPrec:          # il vincolo della consegna
                    parziale.append(vicino)
                    self._ricorsionePesi(parziale, pesoArco)
                    parziale.pop()