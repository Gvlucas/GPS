"""
callejero.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP14B
Integrantes:
    - Gonzalo Velasco
    - Jorge León

Descripción:
Librería con herramientas y clases auxiliares necesarias para la representación de un callejero en un grafo.

"""

import osmnx as ox
import networkx as nx
import pandas as pd
import os
import matplotlib.pyplot as plt
import re

from typing import Tuple

STREET_FILE_NAME="direcciones.csv"

PLACE_NAME = "Madrid, Spain"
MAP_FILE_NAME="madrid.graphml"

MAX_SPEEDS={'living_street': '20','residential': '30','primary_link': '40','unclassified': '40','secondary_link': '40','trunk_link': '40','secondary': '50','tertiary': '50','primary': '50','trunk': '50','tertiary_link':'50','busway': '50','motorway_link': '70','motorway': '100'}


class ServiceNotAvailableError(Exception):
    "Excepción que indica que la navegación no está disponible en este momento"
    pass


class AdressNotFoundError(Exception):
    "Excepción que indica que una dirección buscada no existe en la base de datos"
    pass


############## Parte 2 ##############
def normalizar_nombres(nombres:list,indice:int)-> str:
    
    if indice is not None:
        if len(nombres) <= indice:
            return nombres[-1]#en caso de que la lista de highway sea mayor que la de names, nos quedamos con el último nombre
        return nombres[indice]
    return nombres[0]

def limpiar_aristas(G: nx.DiGraph) -> nx.DiGraph:

    #esto es de la tabla del enunciado
    velocidades_por_defecto = {
        "living_street": 20.0,
        "residential": 30.0,
        "primary_link": 40.0,
        "unclassified": 40.0,
        "secondary_link": 40.0,
        "trunk_link": 40.0,
        "trunk": 50.0,
        "primary": 50.0,
        "secondary": 50.0,
        "tertiary": 50.0,
        "tertiary_link": 50.0,
        "busway": 50.0,
        "motorway_link": 70.0,
        "motorway": 100.0,
    }
    velocidad_defecto = 50.0  #cualquier otro

    for u, v, data in G.edges(data=True): #data es el diccionario con todos los atributos de la arista
        #primero normalizamos los datos del tipo de via(no puede haber más de uno)
        if type(data.get("highway")) == list:
            data["highway"], idx_hw = normalizar_highway(data.get("highway"),velocidades_por_defecto,velocidad_defecto)#uso get para que en caso de que no exista que no de problemas y corte toda la ejecución
        else:
            idx_hw = None
            
        if type(data.get("name")) == list:
            data["name"] = normalizar_nombres(data.get("name"),idx_hw)
        #ahora normalizamos la velocidad máxima
        maxspeed = normalizar_maxspeed(data.get("maxspeed"))

        if data["highway"] in velocidades_por_defecto:
            maxspeed = velocidades_por_defecto[data["highway"]]
        else:
            maxspeed = velocidad_defecto #con esto nos aseguramos que ninguna velocidad este en None
        data["maxspeed"] = maxspeed
        
        if type(data.get("lanes")) == list:
            data["lanes"] = normalizar_lanes(data.get("lanes"))
            
        if type(data.get("reversed")) == list:
            data["reversed"] = True #si nos dicen que una vía es de doble sentido y a la vez no lo es, consideramos que lo es.
            
        #ahora la velocidad efectiva 
        speed_kph = maxspeed

        data["speed_kph"] = speed_kph

        #calculamos el tiempo de recorrido (travel_time_s) con la longitud y la velocidad efectiva
        #este tiempo nos será muy útil
        #la velocidad está en kilómetros por hora y la longitud en metros, por lo que hacemos el cambio de kph a mps y lo tenemos.
        length = data.get("length")
        data["travel_time_s"] = length / (speed_kph * 1000.0 / 3600.0)

    return G

def normalizar_highway(valor:list, velocidades_por_defecto: dict, velocidad_defecto: float):
    # el caso de que haya un error y el valor de highway venga dado por una lista en el diccionario,
    # cogemos el que tenga mayor maxspeed

    if len(valor) == 0:
        return None

    else:
        maximo = 0
        idx = None      #inicializamos el índice y highway a None
        highway = None

        pos = 0         #posición actual de la lista
        for v in valor:
            if v in velocidades_por_defecto:
                if velocidades_por_defecto[v] >= maximo:
                    highway = v
                    maximo = velocidades_por_defecto[v]
                    idx = pos
            else:
                if velocidad_defecto >= maximo:
                    highway = v
                    maximo = velocidad_defecto
                    idx = pos
            pos += 1

        return highway, idx

def normalizar_maxspeed(valor):
    #convertimos maxspeed a float o None
    if valor is None:
        return None

    #si es una lista, nos quedamos con el elemento max
    if type(valor) == list:
        
        if len(valor) == 0:
            return None
        
        valor = float(max(valor))#cogemos la máxima velocidad(imaginate que una calle converge en un autovía o algo, cogemos la mayor para ese tipo de ocasiones)

    #intentamos convertir directamente a float
    try:
        return float(valor)
    except:
        pass

    #si es un str, limpiamos
    #después de analizar el diccionario, solo he encontrado una cadena(str): '50|30', nos quedamos con el mayor(50) y seguimos.
    if type(valor) == str:
        cadena = valor.split("|")
        return float(max(cadena))
    return None

def normalizar_lanes(carriles:list):
    
    if len(carriles) == 0:
        return None
    return max(carriles)#nos quedamos con el mayor como siempre

def latitud_longitud(coord:str):
    total=0
    actual=""
    minutos=True
    segundos=False
    for n in coord:
        if n == "�":
            total+=float(actual)
            actual=""
        elif n == "'" and minutos:
            total+=float(actual)/60
            actual=""
            minutos=False
            segundos=True
        elif n == "'" and segundos:
            total+=float(actual)/3600
            actual=""
            segundos=False
        elif n == "N" or n=="E":
            signo=False
        elif n=="S" or n=="W":
            signo=True
        else:
            actual+=n
    
    if signo:
        total=total*-1
    
    return str(total)

def carga_callejero() -> pd.DataFrame:
    """ Función que carga el callejero de Madrid, lo procesa y devuelve
    un DataFrame con los datos procesados
    
    Args: None
    Returns:
        DataFrame: dataframe con los datos del callejero procesados.
    Raises:
        FileNotFoundError si el fichero csv con las direcciones no existe
    """
    df_direcciones=pd.read_csv("direcciones.csv",sep=";")
    df_direc=pd.DataFrame()
    df_direc["VIA_CLASE"]=df_direcciones["VIA_CLASE"]
    df_direc["VIA_PAR"]=df_direcciones["VIA_PAR"]
    df_direc["VIA_NOMBRE"]=df_direcciones["VIA_NOMBRE"]
    df_direc["NUMERO"]=df_direcciones["NUMERO"]
    df_direc["LATITUD"]=df_direcciones["LATITUD"]
    df_direc["LONGITUD"]=df_direcciones["LONGITUD"]
    
    df_direc["LATITUD"]=df_direc["LATITUD"].apply(latitud_longitud)
    df_direc["LONGITUD"]=df_direc["LONGITUD"].apply(latitud_longitud)
    
    return df_direc





def busca_direccion(direccion:str, callejero:pd.DataFrame) -> Tuple[float,float]:
    """ Función que busca una dirección, dada en el formato
        calle, numero
    en el DataFrame callejero de Madrid y devuelve el par (latitud, longitud) en grados de la
    hubicación geográfica de dicha dirección
    
    Args:
        direccion (str): Nombre completo de la calle con número, en formato "Calle, num"
        callejero (DataFrame): DataFrame con la información de las calles
    Returns:
        Tuple[float,float]: Par de float (latitud,longitud) de la dirección buscada, expresados en grados
    Raises:
        AdressNotFoundError: Si la dirección no existe en la base de datos
    Example:
        busca_direccion("Calle de Alberto Aguilera, 23", data)=(40.42998055555555,-3.7112583333333333)
        busca_direccion("Calle de Alberto Aguilera, 25", data)=(40.43013055555555,-3.7126916666666667)
    """
    
    
    direccion = direccion.upper()
    via_par = callejero["VIA_PAR"].fillna("").astype(str).str.strip()
    if re.fullmatch(r"[A-Z\s]+\s[DE|DEL]+\s[A-Z\s,0-9]+",direccion)!=None:
        dirreciones_df = callejero["VIA_CLASE"].astype(str).str.strip() + " " + via_par + " " + callejero["VIA_NOMBRE"].astype(str).str.strip() + ", " + callejero["NUMERO"].astype(str).str.strip()
    else:
        dirreciones_df = callejero["VIA_CLASE"].astype(str).str.strip() + " " + callejero["VIA_NOMBRE"].astype(str).str.strip() + ", " + callejero["NUMERO"].astype(str).str.strip()
    encontrado = dirreciones_df == direccion
    
    if not encontrado.any():
        raise AdressNotFoundError(f"Dirección no encotrada: {direccion}")
    fila = callejero[encontrado].iloc[0]
    
    return float(fila["LATITUD"]), float(fila["LONGITUD"])


############## Parte 4 ##############


def carga_grafo() -> nx.MultiDiGraph:
    """ Función que recupera el quiver de calles de Madrid de OpenStreetMap.
    Args: None
    Returns:
        nx.MultiDiGraph: Quiver de las calles de Madrid.
    Raises:
        ServiceNotAvailableError: Si no es posible recuperar el grafo de OpenStreetMap.
    """
    if not os.path.isfile("madrid.graphml"):
        grafo_madrid=ox.graph_from_place("Madrid,Spain",network_type="drive")
        #ox.plot_graph(grafo_madrid,node_size=0,edge_linewidth=0.5)
        ox.save_graphml(grafo_madrid,"madrid.graphml")
    else:
        grafo_madrid=ox.load_graphml("madrid.graphml")
        #ox.plot_graph(grafo_madrid,node_size=0,edge_linewidth=0.5)
    return grafo_madrid


    
def procesa_grafo(grafo_madrid:nx.MultiDiGraph)->nx.DiGraph:
    G = ox.convert.to_digraph(grafo_madrid)
    #ahora buscamos los bucles
    bucles = list(nx.selfloop_edges(G))
    G.remove_edges_from(bucles)#quitamos los bucles
    return limpiar_aristas(G) #retornamos el grafo totalmente filtrado

def dibujar_grafo_dirigido(G: nx.DiGraph) -> None:#ahora lo dibujamos
    #construimos un diccionario con clave nodo y valor su coordenada.
    #donde d["x"] es la coordenada X(longitud) y d["y"] es la coordenada Y (latitud)
    pos = {}
    for n, d in G.nodes(data=True):#n siendo el nodo y d siendo el diccionario con sus atributos
        pos[n] = (d["x"], d["y"])
        #esta d nos puede venir muy bien porque contiene el número de calle que convergen a ese nodo y tambien señales de tráfico
        
    #ahora lo dibujamos facilmente gracias al diccionario, que le dice a nx exactamente donde colocar cada nodo
    plt.figure(figsize=(8, 8))
    nx.draw(G,pos=pos,node_size=0,width=0.5,arrows=True,arrowsize=5)
    plt.axis("off")
    plt.show()

if __name__=="__main__":
    grafo=carga_grafo()
    print(grafo.nodes)
    x=grafo.neighbors(13239981545)
    for n in x:
        print(n)
