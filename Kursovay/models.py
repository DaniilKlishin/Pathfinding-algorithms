# models.py
import math
from typing import Dict, List, Tuple, Set, Optional, Callable

class Node:
    """Представляет узел графа для алгоритмов поиска пути"""
    
    def __init__(self, id: str, x: int, y: int, is_walkable: bool = True):
        self.id = id
        self.x = x
        self.y = y
        self.is_walkable = is_walkable
        
        # Для A* и Дейкстры
        self.g_cost = float('inf')
        self.h_cost = 0
        self.parent = None
        
        # Для визуализации
        self.was_visited = False
        self.is_in_path = False
    
    @property
    def f_cost(self):
        return self.g_cost + self.h_cost
    
    @property
    def name(self):
        return f"{self.id}({self.x},{self.y})"
    
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
    
    def __lt__(self, other):
        if self.f_cost == other.f_cost:
            return self.h_cost < other.h_cost
        return self.f_cost < other.f_cost
    
    def __repr__(self):
        return f"Node{self.name}"

class Edge:
    """Представляет ребро графа"""
    
    def __init__(self, from_node: str, to_node: str, weight: float):
        self.from_node = from_node
        self.to_node = to_node
        self.weight = weight
    
    def __repr__(self):
        return f"{self.from_node}→{self.to_node}({self.weight})"

class AlgorithmStats:
    """Статистика выполнения алгоритма"""
    
    def __init__(self, algorithm_name: str):
        self.algorithm_name = algorithm_name
        self.execution_time = 0.0
        self.visited_nodes = 0
        self.path_length = 0
        self.path_cost = 0.0
        self.found_path = False
        self.has_negative_cycle = False
    
    def __str__(self):
        if not self.found_path:
            if self.has_negative_cycle:
                return f"{self.algorithm_name}: Обнаружен отрицательный цикл"
            return f"{self.algorithm_name}: Путь не найден"
        
        return (f"{self.algorithm_name}:\n"
                f"  Время выполнения: {self.execution_time:.6f} сек\n"
                f"  Посещено узлов: {self.visited_nodes}\n"
                f"  Длина пути: {self.path_length}\n"
                f"  Стоимость пути: {self.path_cost:.2f}")