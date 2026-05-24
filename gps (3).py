"""
gps.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP14B
Integrantes:
    - Gonzalo Velasco
    - Jorge León

Descripción:
Código para el funcionamiento de un GPS de la Comunidad de Madrid

"""
import networkx as nx
import osmnx as ox
import pandas as pd
from callejero import *
import math
from grafo_pesado import *

def peso_metros(G, nodo_origen: int, nodo_destino: int)-> int:
    """Función que devuelve la distancia entre dos nodos de un grafo

    Args:
        G (_type_): grafo
        nodo_origen (int): nodo 1
        nodo_destino (int): nodo 2

    Returns:
        int: distancia
    """
    data=G[nodo_origen][nodo_destino]
    return data["length"]

def peso_tiempo(G,nodo_origen,nodo_destino):
    """Función que devuelve cuanto tiempo se tarda en llegar de un nodo a otro en un grafo

    Args:
        G (_type_): grafo
        nodo_origen (_type_): nodo 1
        nodo_destino (_type_): nodo 2

    Returns:
        int: tiempo de un nodo a otro
    """
    data=G[nodo_origen][nodo_destino]
    return data["travel_time_s"] #Devolvemos el valor de "travel_time_s" que calculamos en callejero.py

def peso_semaforo(G,nodo_origen,nodo_destino):
    """Función que devuelve cuanto tiempo se tarda en llegar de un nodo a otro en un grafo teniendo en cuenta la posibilidad de tener que frenar por culpa de una señal vial.

    Args:
        G (_type_): grafo
        nodo_origen (_type_): nodo 1
        nodo_destino (_type_): nodo 2

    Returns:
        _type_: tiempo de un nodo a otro
    """
    p=0.8
    s=30
    data=G[nodo_origen][nodo_destino]
    tiempo=data["travel_time_s"]
    if G.nodes[nodo_destino]["street_count"]>=3:#Comprobamos si es una intersección si tiene tres calles o más
        return tiempo+p*s 
    
    return tiempo #Si no es una intersección devolvemos el tiempo sin añadir nada

def giro_nodos(G, A, B, C):
    margen=1e-8
    # Calculamos dos vectores uno que une A con B y otro que une B con C
    v1x = G.nodes[B]["x"] - G.nodes[A]["x"]
    v1y = G.nodes[B]["y"] - G.nodes[A]["y"]
    v2x = G.nodes[C]["x"] - G.nodes[B]["x"]
    v2y = G.nodes[C]["y"] - G.nodes[B]["y"]

    producto = v1x * v2y - v1y * v2x #Hallamos el producto vectorial

    if producto > margen: #Usamos un pequeño margen porque nada es completamente recto
        return "gira a la izquierda"
    elif producto < -margen:
        return "gira a la derecha"
    else:
        return "sigue recto"

def analisis_camino(G,camino):
    """Función que genera las instrucciones que seguir para llegar al destino

    Args:
        G (_type_): grafo
        camino (_type_): lista de nodos
    """
    contador=0
    total_distancia=0
    lista_nombres=[]
    while contador<len(camino)-1:
        if "name" in G[camino[contador]][camino[contador+1]]:
            lista_nombres.append(G[camino[contador]][camino[contador+1]]["name"])
        else:
            if G[camino[contador]][camino[contador+1]]["highway"]=="motorway_link":
                lista_nombres.append("Desconocido_salida")
            else:
                lista_nombres.append("Desconocido")
                print(G[camino[contador]][camino[contador+1]])
        total_distancia+=G[camino[contador]][camino[contador+1]]["length"]
        contador+=1
    
    
    
    contador2=0
    actual_calle=0
    
    while contador2<len(lista_nombres)-1:
        if lista_nombres[contador2]==lista_nombres[contador2+1]:
            actual_calle+=G_M[camino[contador2]][camino[contador2+1]]["length"]
        else:
            actual_calle+=G_M[camino[contador2]][camino[contador2+1]]["length"]
            if lista_nombres[contador2+1]=="Desconocido_salida" and lista_nombres[contador2]=="Desconocido":
                print(f"Sal de la vía actual en {actual_calle} metros, {giro_nodos(G,camino[contador2],camino[contador2+1],camino[contador2+2])}")
            elif lista_nombres[contador2]=="Desconocido_salida" and lista_nombres[contador2+1]=="Desconocido":
                print(f"Incorporate a la vía en {actual_calle} metros, {giro_nodos(G,camino[contador2],camino[contador2+1],camino[contador2+2])}")
            elif lista_nombres[contador2+1]=="Desconocido_salida":
                print(f"Sal de {lista_nombres[contador2]} en {actual_calle} metros, {giro_nodos(G,camino[contador2],camino[contador2+1],camino[contador2+2])}")
            elif lista_nombres[contador2]=="Desconocido_salida":
                print(f"Continua hasta entrar a {lista_nombres[contador2]} en {actual_calle} metros, {giro_nodos(G,camino[contador2],camino[contador2+1],camino[contador2+2])}")
            elif lista_nombres[contador2+1]=="Desconocido":
                print(f"Continua por {lista_nombres[contador2]} {actual_calle} metros y {giro_nodos(G,camino[contador2],camino[contador2+1],camino[contador2+2])}")
            elif lista_nombres[contador2]=="Desconocido":
                print(f"Continua {actual_calle} metros y {giro_nodos(G,camino[contador2],camino[contador2+1],camino[contador2+2])} en {lista_nombres[contador2+1]}")
            else:
                print(f"Continua por {lista_nombres[contador2]} {actual_calle} metros y {giro_nodos(G,camino[contador2],camino[contador2+1],camino[contador2+2])} en {lista_nombres[contador2+1]}")
            actual_calle=0
        contador2+=1
    print(f"Continua por {lista_nombres[contador2]} {actual_calle} metros y detente")
    print(f"La distancia total es:{total_distancia}")

def nodo_mas_cercano(G,coords_origen:str,coords_destino:str):
    """Función que devuelve los nodos más cercanos a las coordenadas de las direcciones introducidas

    Args:
        G (_type_): grafo
        coords_origen (_type_): coordenadas del origen
        coords_destino (_type_): coordenadas del destino

    Returns:
        tuple(nodo_origen,nodo_destino): los nodos asociados
    """
    error_origen=99999999
    error_destino=9999999
    nodo_origen=0
    nodo_destino=0
    for g,d in G_M.nodes(data=True):
            error_actual_origen=abs(coords_origen[1]-d["x"])+abs(coords_origen[0]-d["y"])
            error_actual_destino=abs(coords_destino[1]-d["x"])+abs(coords_destino[0]-d["y"])
            if error_actual_origen<error_origen:#Buscamos aquellos nodos con menor diferencia con respecto a las coordenadas originales
                nodo_origen=(g,d["x"],d["y"])
                error_origen=error_actual_origen
            if error_actual_destino<error_destino:
                nodo_destino=(g,d["x"],d["y"])
                error_destino=error_actual_destino
    coords_origen=(nodo_origen[1],nodo_origen[2])
    coords_destino=(nodo_destino[1],nodo_destino[2])
    nodo_origen=nodo_origen[0]
    nodo_destino=nodo_destino[0]
    return nodo_origen,nodo_destino

if __name__=="__main__":
    df_direc=carga_callejero()
    G_M=procesa_grafo(carga_grafo())
    origen=" "
    destino=" "
    while True:
        origen=input("Introduzca la dirección de origen:")
        destino=input("Introduzca la dirección de destino:")
        if origen=="" and destino=="": #Si no se introducen coordenadas se termina el programa
            break
        coords_origen=busca_direccion(origen,df_direc)
        coords_destino=busca_direccion(destino,df_direc)
        nodo_origen,nodo_destino=nodo_mas_cercano(G_M,coords_origen,coords_destino)
        
        tipo_peso=input("Quiere el camino mas corto (C), el más rápido(R) o el más rapido teniendo en cuenta semáforos(S)?:")#Elección de función de peso
        if tipo_peso=="C":
            camino=camino_minimo(G_M,peso_metros,nodo_origen,nodo_destino)
        elif tipo_peso=="R":
            camino=camino_minimo(G_M,peso_tiempo,nodo_origen,nodo_destino)
        elif tipo_peso=="S":
            camino=camino_minimo(G_M,peso_semaforo,nodo_origen,nodo_destino)
        
        analisis_camino(G_M,camino)
        
        
        
        aristas_ruta = list(zip(camino[:-1], camino[1:])) #Con zip emparejamos los nodos con su siguiente en la lista formando una lista de aristas que pintaremos de otro color
        pos = {n: (G_M.nodes[n]["x"], G_M.nodes[n]["y"]) for n in G_M.nodes()}
        nx.draw_networkx_edges(G_M, pos, edge_color="gray", width=1, arrows=False)
        nx.draw_networkx_edges(G_M,pos,edgelist=aristas_ruta,edge_color="red",width=3,arrows=False)
        
        plt.axis("equal")
        plt.show()

