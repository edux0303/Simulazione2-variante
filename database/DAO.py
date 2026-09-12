from database.DB_connect import DBConnect
from model.film import Film

"""
L'utente seleziona dai corrispondenti menù a tendina
 un range di anni (campo year della tabella movie).

b. Premendo il pulsante "Crea grafo",
 l'applicazione costruisce un grafo NON orientato 
 ma pesato che rappresenta le relazioni tra film.
  I vertici sono i film usciti nel range di anni definito
   dall'utente. N.B. si consideri come campo del nodo Film anche
la durata (hint: controllare che la durata riportata sia valida
prima di inserire i film nel grafo). Esiste un arco tra due film
 se hanno almeno un attore in comune. Il peso è pari al numero di attori in comune.

c. Costruito il grafo, l'applicazione visualizza il numero di vertici e archi e i 5 archi di peso maggiore. Si visualizzi anche il numero delle componenti connesse e la componente connessa maggiore.


2
Trovare un cammino semplice di lunghezza massima
tale che ogni arco attraversato abbia peso maggiore
 o uguale a una soglia scelta dall'utente."
"""

class DAO():
    def __init__(self):
        pass


    @staticmethod
    def getYears():
        cnx = DBConnect.get_connection()
        if cnx is None:
            return None
        result = []
        cursor = cnx.cursor(dictionary=True)
        query = """SELECT DISTINCT m.year AS anno
                   FROM movie m
                   WHERE m.year IS NOT NULL
                   ORDER BY anno ASC"""
        try:
            cursor.execute(query)
            for row in cursor:
                result.append(row["anno"])
        except Exception as e:
            print(f"Errore in getYears: {e}")
            result = None
        finally:
            cursor.close()
            cnx.close()
        return result

    @staticmethod
    def getNodi(annoMin, annoMax):
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            return result
        cursor = cnx.cursor(dictionary=True)
        query = """SELECT m.id, m.title, m.year, m.duration AS durata
                   FROM movie m
                   WHERE m.year BETWEEN %s AND %s
                     AND m.duration IS NOT NULL
                     AND m.duration > 0"""
        try:
            cursor.execute(query, (annoMin, annoMax))
            for row in cursor:
                result.append(Film(**row))
        except Exception as e:
            print(f"Errore in getNodi: {e}")
        finally:
            cursor.close()
            cnx.close()
        return result

    @staticmethod
    def getEdges(annoMin, annoMax):
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            return result
        cursor = cnx.cursor(dictionary=True)
        query = """SELECT rm1.movie_id AS f1, rm2.movie_id AS f2,
                          COUNT(*) AS peso
                   FROM role_mapping rm1, role_mapping rm2, movie m1, movie m2
                   WHERE rm1.name_id = rm2.name_id
                     AND rm1.movie_id < rm2.movie_id
                     AND rm1.movie_id = m1.id
                     AND rm2.movie_id = m2.id
                     AND m1.year BETWEEN %s AND %s
                     AND m2.year BETWEEN %s AND %s
                   GROUP BY rm1.movie_id, rm2.movie_id"""
        try:
            cursor.execute(query, (annoMin, annoMax, annoMin, annoMax))
            for row in cursor:
                result.append(row)
        except Exception as e:
            print(f"Errore in getEdges: {e}")
        finally:
            cursor.close()
            cnx.close()
        return result
