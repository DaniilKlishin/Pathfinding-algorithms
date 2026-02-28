# graph.py
import heapq
import math
import time
from typing import Dict, List, Tuple, Set, Callable, Optional
from models import Node, Edge, AlgorithmStats

class Graph:
    """Представляет граф для всех алгоритмов"""
    
    def __init__(self, directed: bool = True):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.is_directed = directed
        self.name = "Граф"
    
    def add_node(self, node_id: str, x: int, y: int, is_walkable: bool = True):
        """Добавляет узел в граф"""
        self.nodes[node_id] = Node(node_id, x, y, is_walkable)
    
    def add_edge(self, from_node: str, to_node: str, weight: float):
        """Добавляет ребро в граф"""
        self.edges.append(Edge(from_node, to_node, weight))
        if not self.is_directed:
            self.edges.append(Edge(to_node, from_node, weight))
    
    def get_neighbors(self, node_id: str) -> List[Tuple[str, float]]:
        """Возвращает список соседей и весов ребер"""
        neighbors = []
        for edge in self.edges:
            if edge.from_node == node_id:
                neighbors.append((edge.to_node, edge.weight))
        return neighbors
    
    def get_edge(self, from_node: str, to_node: str) -> Optional[Edge]:
        """Возвращает ребро между двумя узлами, если оно существует"""
        for edge in self.edges:
            if edge.from_node == from_node and edge.to_node == to_node:
                return edge
        return None
    
    def dijkstra(self, start_id: str, goal_id: str) -> Tuple[AlgorithmStats, Dict[str, float], Dict[str, str], Set[Node]]:
        """Алгоритм Дейкстры"""
        stats = AlgorithmStats("Дейкстра")
        start_time = time.perf_counter()  # Более точное измерение времени
        
        self.reset_visualization()
        visited = set()
        distances = {}
        predecessors = {}
        
        # Инициализация
        for node_id in self.nodes.keys():
            distances[node_id] = 0 if node_id == start_id else float('inf')
            predecessors[node_id] = None
        
        priority_queue = []
        heapq.heappush(priority_queue, (0, start_id))
        
        while priority_queue:
            current_distance, current_node_id = heapq.heappop(priority_queue)
            current_node = self.nodes[current_node_id]
            
            if current_node in visited:
                continue
                
            visited.add(current_node)
            current_node.was_visited = True
            
            if current_node_id == goal_id:
                break
            
            for neighbor_id, weight in self.get_neighbors(current_node_id):
                if neighbor_id not in self.nodes or self.nodes[neighbor_id] in visited:
                    continue
                
                new_distance = current_distance + weight
                if new_distance < distances[neighbor_id]:
                    distances[neighbor_id] = new_distance
                    predecessors[neighbor_id] = current_node_id
                    heapq.heappush(priority_queue, (new_distance, neighbor_id))
        
        # Собираем статистику
        stats.execution_time = time.perf_counter() - start_time
        stats.visited_nodes = len(visited)
        
        # Восстанавливаем путь
        if distances[goal_id] < float('inf'):
            path = self._reconstruct_path_from_predecessors(predecessors, start_id, goal_id)
            if path:
                stats.found_path = True
                stats.path_length = len(path)
                stats.path_cost = distances[goal_id]
        
        return stats, distances, predecessors, visited
    
    def bellman_ford(self, start_id: str) -> Tuple[AlgorithmStats, Dict[str, float], Dict[str, str], bool, Set[Node]]:
        """Алгоритм Беллмана-Форда"""
        stats = AlgorithmStats("Беллман-Форд")
        start_time = time.perf_counter()  # Более точное измерение времени
        
        self.reset_visualization()
        updated_nodes = set()
        distances = {}
        predecessors = {}
        
        # Инициализация
        for node_id in self.nodes.keys():
            distances[node_id] = 0 if node_id == start_id else float('inf')
            predecessors[node_id] = None
        
        # Релаксация ребер |V| - 1 раз
        for i in range(len(self.nodes) - 1):
            updated = False
            
            for edge in self.edges:
                if (distances[edge.from_node] != float('inf') and 
                    distances[edge.from_node] + edge.weight < distances[edge.to_node]):
                    
                    distances[edge.to_node] = distances[edge.from_node] + edge.weight
                    predecessors[edge.to_node] = edge.from_node
                    updated = True
                    
                    if edge.to_node in self.nodes:
                        updated_nodes.add(self.nodes[edge.to_node])
            
            if not updated:
                break
        
        # Проверка на отрицательные циклы
        has_negative_cycle = False
        for edge in self.edges:
            if (distances[edge.from_node] != float('inf') and 
                distances[edge.from_node] + edge.weight < distances[edge.to_node]):
                has_negative_cycle = True
                break
        
        # Собираем статистику
        stats.execution_time = time.perf_counter() - start_time
        stats.visited_nodes = len(updated_nodes)
        stats.has_negative_cycle = has_negative_cycle
        
        return stats, distances, predecessors, has_negative_cycle, updated_nodes
    
    def a_star(self, start_id: str, goal_id: str, 
               heuristic: Callable[[Node, Node], float] = None) -> Tuple[AlgorithmStats, List[str], float, Set[Node]]:
        """Алгоритм A*"""
        if heuristic is None:
            # Эвристика - евклидово расстояние между координатами
            heuristic = lambda a, b: math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)
        
        stats = AlgorithmStats("A*")
        start_time = time.perf_counter()  # Более точное измерение времени
        
        self.reset_visualization()
        start = self.nodes[start_id]
        goal = self.nodes[goal_id]
        visited = set()
        
        open_set = []
        closed_set = set()
        
        # Инициализация
        for node in self.nodes.values():
            node.g_cost = float('inf')
            node.parent = None
        
        start.g_cost = 0
        start.h_cost = heuristic(start, goal)
        heapq.heappush(open_set, start)
        
        while open_set:
            current = heapq.heappop(open_set)
            
            if current.id == goal_id:
                path = self._reconstruct_path(current)
                self._mark_path(path)
                
                # Собираем статистику
                stats.execution_time = time.perf_counter() - start_time
                stats.visited_nodes = len(visited)
                stats.found_path = True
                stats.path_length = len(path)
                stats.path_cost = current.g_cost
                return stats, path, current.g_cost, visited
            
            closed_set.add(current.id)
            visited.add(current)
            current.was_visited = True
            
            for neighbor_id, weight in self.get_neighbors(current.id):
                if neighbor_id in closed_set:
                    continue
                
                neighbor = self.nodes[neighbor_id]
                
                tentative_g_cost = current.g_cost + weight
                
                if tentative_g_cost < neighbor.g_cost:
                    neighbor.parent = current
                    neighbor.g_cost = tentative_g_cost
                    neighbor.h_cost = heuristic(neighbor, goal)
                    
                    # Проверяем, находится ли сосед в open_set
                    in_open_set = any(node.id == neighbor_id for node in open_set)
                    if not in_open_set:
                        heapq.heappush(open_set, neighbor)
        
        # Если путь не найден
        stats.execution_time = time.perf_counter() - start_time
        stats.visited_nodes = len(visited)
        return stats, None, float('inf'), visited
    
    # Добавим отдельные методы для тестирования скорости без сбора статистики
    def dijkstra_simple(self, start_id: str, goal_id: str) -> Tuple[List[str], float, float]:
        """Упрощенная версия Дейкстры для точного измерения времени"""
        start_time = time.perf_counter()
        
        distances = {}
        predecessors = {}
        visited = set()
        
        # Инициализация
        for node_id in self.nodes.keys():
            distances[node_id] = 0 if node_id == start_id else float('inf')
            predecessors[node_id] = None
        
        priority_queue = []
        heapq.heappush(priority_queue, (0, start_id))
        
        while priority_queue:
            current_distance, current_node_id = heapq.heappop(priority_queue)
            current_node = self.nodes[current_node_id]
            
            if current_node in visited:
                continue
                
            visited.add(current_node)
            
            if current_node_id == goal_id:
                break
            
            for neighbor_id, weight in self.get_neighbors(current_node_id):
                if neighbor_id not in self.nodes or self.nodes[neighbor_id] in visited:
                    continue
                
                new_distance = current_distance + weight
                if new_distance < distances[neighbor_id]:
                    distances[neighbor_id] = new_distance
                    predecessors[neighbor_id] = current_node_id
                    heapq.heappush(priority_queue, (new_distance, neighbor_id))
        
        execution_time = time.perf_counter() - start_time
        
        # Восстанавливаем путь
        path = []
        if distances.get(goal_id, float('inf')) < float('inf'):
            current = goal_id
            while current is not None:
                path.insert(0, current)
                current = predecessors.get(current)
        
        cost = distances.get(goal_id, float('inf'))
        return path, cost, execution_time
    
    def a_star_simple(self, start_id: str, goal_id: str) -> Tuple[List[str], float, float]:
        """Упрощенная версия A* для точного измерения времени"""
        start_time = time.perf_counter()
        
        heuristic = lambda a, b: math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)
        
        start = self.nodes[start_id]
        goal = self.nodes[goal_id]
        
        open_set = []
        closed_set = set()
        
        # Инициализация
        for node in self.nodes.values():
            node.g_cost = float('inf')
            node.parent = None
        
        start.g_cost = 0
        start.h_cost = heuristic(start, goal)
        heapq.heappush(open_set, start)
        
        while open_set:
            current = heapq.heappop(open_set)
            
            if current.id == goal_id:
                # Восстанавливаем путь
                path = []
                while current is not None:
                    path.insert(0, current.id)
                    current = current.parent
                
                execution_time = time.perf_counter() - start_time
                return path, start.g_cost, execution_time
            
            closed_set.add(current.id)
            
            for neighbor_id, weight in self.get_neighbors(current.id):
                if neighbor_id in closed_set:
                    continue
                
                neighbor = self.nodes[neighbor_id]
                
                tentative_g_cost = current.g_cost + weight
                
                if tentative_g_cost < neighbor.g_cost:
                    neighbor.parent = current
                    neighbor.g_cost = tentative_g_cost
                    neighbor.h_cost = heuristic(neighbor, goal)
                    
                    in_open_set = any(node.id == neighbor_id for node in open_set)
                    if not in_open_set:
                        heapq.heappush(open_set, neighbor)
        
        execution_time = time.perf_counter() - start_time
        return [], float('inf'), execution_time
    
    def _reconstruct_path(self, end_node: Node) -> List[str]:
        path = []
        current = end_node
        
        while current is not None:
            path.append(current.id)
            current.is_in_path = True
            current = current.parent
        
        path.reverse()
        return path
    
    def _mark_path(self, path: List[str]):
        if not path:
            return
        
        for node_id in path:
            if node_id in self.nodes:
                self.nodes[node_id].is_in_path = True
    
    def _reconstruct_path_from_predecessors(self, predecessors: Dict[str, str], 
                                         start_id: str, end_id: str) -> List[str]:
        if predecessors.get(end_id) is None and start_id != end_id:
            return []
        
        path = []
        current = end_id
        
        while current is not None:
            path.insert(0, current)
            if current in self.nodes:
                self.nodes[current].is_in_path = True
            current = predecessors.get(current)
        
        return path
    
    def reconstruct_path_from_predecessors(self, predecessors: Dict[str, str], 
                                         start_id: str, end_id: str) -> List[str]:
        return self._reconstruct_path_from_predecessors(predecessors, start_id, end_id)
    
    def reset_visualization(self):
        """Сбрасывает визуализацию всех узлов"""
        for node in self.nodes.values():
            node.was_visited = False
            node.is_in_path = False
            node.g_cost = float('inf')
            node.h_cost = 0
            node.parent = None
    
    def visualize(self, title: str = None, start_id: str = None, goal_id: str = None):
        """Визуализирует граф в консоли"""
        if title:
            print(f"\n{title}:")
        
        # Создаем матрицу для визуализации
        max_x = max(node.x for node in self.nodes.values()) + 1
        max_y = max(node.y for node in self.nodes.values()) + 1
        
        grid = [[' ' for _ in range(max_x)] for _ in range(max_y)]
        
        # Размещаем узлы
        for node in self.nodes.values():
            symbol = node.id
            if start_id and node.id == start_id:
                symbol = f"[{node.id}]"  # Старт
            elif goal_id and node.id == goal_id:
                symbol = f"({node.id})"  # Цель
            elif node.is_in_path:
                symbol = f"*{node.id}*"  # Путь
            elif node.was_visited:
                symbol = f"_{node.id}_"  # Посещенный
            
            if 0 <= node.y < max_y and 0 <= node.x < max_x:
                grid[node.y][node.x] = symbol
        
        # Выводим сетку
        for row in grid:
            print(' '.join(row))
        
        # Выводим информацию о ребрах
        print("\nРебра графа:")
        for edge in self.edges:
            print(f"  {edge.from_node} → {edge.to_node} (вес: {edge.weight})")
        
        print("\nЛегенда: [S] - старт, (G) - цель, *N* - путь, _N_ - посещенный")