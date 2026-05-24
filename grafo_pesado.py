"""
grafo`_pesado.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP14B
Integrantes:
    - Gonzalo Velasco
    - Jorge León

Descripción:
Librería para el análisis de grafos pesados.
"""



from typing import List,Tuple,Dict,Callable,Union
import networkx as nx
import sys
import itertools
import heapq #Librería para la creación de colas de prioridad

INFTY=sys.float_info.max #Distincia "infinita" entre nodos de un grafo

"""
En las siguientes funciones, las funciones de peso son funciones que reciben un grafo o digrafo y dos vértices y devuelven un real (su peso)
Por ejemplo, si las aristas del grafo contienen en sus datos un campo llamado 'valor', una posible función de peso sería:

def mi_peso(G:nx.Graph,u:object, v:object):
    return G[u][v]['valor']

y, en tal caso, para calcular Dijkstra con dicho parámetro haríamos

camino=dijkstra(G,mi_peso,origen, destino)


"""


def dijkstra(G:Union[nx.Graph, nx.DiGraph], peso:Union[Callable[[nx.Graph,object,object],float], Callable[[nx.DiGraph,object,object],float]], origen:object)-> Dict[object,object]:
    """ Calcula un Árbol de Caminos Mínimos para el grafo pesado partiendo
    del vértice "origen" usando el algoritmo de Dijkstra. Calcula únicamente
    el árbol de la componente conexa que contiene a "origen".
    
    Args:
        origen (object): vértice del grafo de origen
    Returns:
        Dict[object,object]: Devuelve un diccionario que indica, para cada vértice alcanzable
            desde "origen", qué vértice es su padre en el árbol de caminos mínimos.
    Raises:
        TypeError: Si origen no es "hashable".
    Example:
        Si G.dijksra(1)={2:1, 3:2, 4:1} entonces 1 es padre de 2 y de 4 y 2 es padre de 3.
        En particular, un camino mínimo desde 1 hasta 3 sería 1->2->3.
    """
    #hashabilidad
    try:
        {origen} #esto es porque no puede meter nada que no sea hashable en un set(comprobación fácil)
    except TypeError:
        raise TypeError("Origen debe ser hashable")
    
    padres={}
    visitado={}
    d={}
    contador=itertools.count()
    
    for v in G.nodes :
        padres[v] = None
        visitado[v] = False
        d[v]=INFTY
    d[origen] = 0
    Q=[]
    heapq.heappush(Q,(d[origen],next(contador),origen))
    while Q != []:
        v=heapq.heappop(Q)[2]
        if visitado[v] == False:
            visitado[v] = True
            for x in G.neighbors(v):
                if d[x] > d[v] + peso(G,v,x):
                        d[x] = d[v] + peso(G,v,x)
                        padres[x] = v
                        heapq.heappush(Q,(d[x],next(contador),x))
    
    return padres
    


def camino_minimo(G:Union[nx.Graph, nx.DiGraph], peso:Union[Callable[[nx.Graph,object,object],float], Callable[[nx.DiGraph,object,object],float]] ,origen:object,destino:object)->List[object]:
    """ Calcula el camino mínimo desde el vértice origen hasta el vértice
    destino utilizando el algoritmo de Dijkstra.
    
    Args:
        G (nx.Graph o nx.Digraph): grafo a grado dirigido
        peso (función): función que recibe un grafo o grafo dirigido y dos vértices del mismo y devuelve el peso de la arista que los conecta
        origen (object): vértice del grafo de origen
        destino (object): vértice del grafo de destino
    Returns:
        List[object]: Devuelve una lista con los vértices del grafo por los que pasa
            el camino más corto entre el origen y el destino. El primer elemento de
            la lista es origen y el último destino.
    Example:
        Si dijksra(G,peso,1,4)=[1,5,2,4] entonces el camino más corto en G entre 1 y 4 es 1->5->2->4.
    Raises:
        TypeError: Si origen o destino no son "hashable".
    """
    
    #hashabilidad
    try:
        {origen, destino} #esto es porque no puede meter nada que no sea hashable en un set(comprobación fácil)
    except TypeError:
        raise TypeError("Origen y destino deben ser hashables")

    #ejecutamos nuestro dijkstra
    padres = dijkstra(G, peso, origen)

    #miramo el caso origen == destino
    if origen == destino:
        return [origen]

    #hacemos el camino 1 a 1 desde destino hacia origen
    camino = []
    actual = destino

    # Si el destino no tiene padre(None) y el destino != origen, no existe el camino.
    if padres[actual] is None:
        raise ValueError(f"No existe camino desde {origen} hasta {destino}")

    while actual is not None:
        camino.append(actual)
        if actual == origen: #hemos llegado al destino, nos salimos del while con el break
            break
        actual = padres[actual]

    # Si hemos salido del bucle y no hemos llegado al origen, es inalcanzable.
    if camino[-1] != origen:
        raise ValueError(f"No existe camino desde {origen} hasta {destino}")

    camino.reverse()
    return camino


def prim(G:nx.Graph, peso:Callable[[nx.Graph,object,object],float])-> Dict[object,object]:
    """ Calcula un Árbol Abarcador Mínimo para el grafo pesado
    usando el algoritmo de Prim.
    
    Args: None
    Returns:
        G (nx.Graph): grafo
        peso (función): función que recibe un grafo y dos vértices del grafo y devuelve el peso de la arista que los conecta
        Dict[object,object]: Devuelve un diccionario que indica, para cada vértice del
            grafo, qué vértice es su padre en el árbol abarcador mínimo.
    Raises: None
    Example:
        Si prim(G,peso)={1: None, 2:1, 3:2, 4:1} entonces en un árbol abarcador mínimo tenemos que:
            1 es una raíz (no tiene padre)
            1 es padre de 2 y de 4
            2 es padre de 3
    """
    coste_min={}
    padres={}
    Q=[]
    contador=itertools.count()
    for v in G.nodes:
        padres[v] = None
        coste_min[v] = INFTY
        heapq.heappush(Q,(coste_min[v],next(contador),v))

    while Q != []:
        v=heapq.heappop(Q)[2]
        for x in G.neighbors(v):
            for tupla in Q:
                if x in tupla:
                    if peso(G,v,x) < coste_min[x]:
                        coste_min[x] = peso(G,v,x)
                        padres[x] = v
                        heapq.heappush(Q,(coste_min[x],next(contador),x))
    return padres


def kruskal(G:nx.Graph, peso:Callable[[nx.Graph,object,object],float])-> List[Tuple[object,object]]:
    """ Calcula un Árbol Abarcador Mínimo para el grafo
    usando el algoritmo de Kruskal.
    
    Args:
        G (nx.Graph): grafo
        peso (función): función que recibe un grafo y dos vértices del grafo y devuelve el peso de la arista que los conecta
    Returns:
        List[Tuple[object,object]]: Devuelve una lista [(s1,t1),(s2,t2),...,(sn,tn)]
            de los pares de vértices del grafo que forman las aristas
            del arbol abarcador mínimo.
    Raises: None
    Example:
        En el ejemplo anterior en que prim(G,peso)={1:None, 2:1, 3:2, 4:1} podríamos tener, por ejemplo,
        kruskal(G,peso)=[(1,2),(1,4),(3,2)]
    """
    L=[]
    contador=itertools.count()
    for arista in G.edges:
        
        heapq.heappush(L,(peso(G,arista[0],arista[1]),next(contador),arista))
    C={}
    for v in G.nodes:
        C[v]={v}
    aristas_aam=[]
    while L!=[]:
        a=heapq.heappop(L)[2]
        if C[a[0]]!=C[a[1]]:
            aristas_aam.append(a)
            comp_u = C[a[0]]
            comp_v = C[a[1]]
            nueva = set(comp_u)
            for w in comp_v:
                nueva.add(w)
            for w in nueva:
                C[w] = nueva
    
    return aristas_aam
