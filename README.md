# GPS
GPS Navigator – Discrete Mathematics Practice 3
A Python-based GPS navigation system built on graph theory, developed for the Mathematical Engineering & AI degree at Universidad Pontificia Comillas (ICAI), course 2025-2026.
Overview
The system builds a weighted directed graph of Madrid's street intersections using OpenStreetMap data (via OSMnx), then finds optimal routes between any two official Madrid addresses using custom implementations of classic graph algorithms.
Features

Parses the official Madrid address database (datos.madrid.es) and converts geographic coordinates from DMS to decimal format
Builds and caches a NetworkX DiGraph of Madrid's road network from OpenStreetMap
Implements Dijkstra, Prim, and Kruskal algorithms from scratch (no NetworkX shortcuts)
Three routing modes: shortest distance, fastest time, and fastest time with traffic light delays modeled probabilistically
Step-by-step navigation instructions with street names, distances, and turn directions (left/right)
Visual route display overlaid on the full city graph

Tech Stack

Python · NetworkX · OSMnx · pandas · matplotlib

Project Structure

grafo_pesado.py — weighted graph algorithms (Dijkstra, Prim, Kruskal, shortest path)

callejero.py — address parsing, coordinate conversion, street data loading

gps.py — main navigation application
