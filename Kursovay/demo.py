# demo.py
from graph import Graph
from utils import compare_algorithms, load_graph_from_json

def create_graph_from_image():
    """Создает граф на основе предоставленного изображения"""
    graph = Graph(directed=True)
    graph.name = "Граф из изображения"
    
    # Добавляем узлы с координатами для визуализации
    graph.add_node('A', 1, 2)
    graph.add_node('B', 3, 0)
    graph.add_node('C', 3, 4)
    graph.add_node('D', 5, 2)
    graph.add_node('E', 7, 2)
    
    # Добавляем ребра согласно изображению
    graph.add_edge('A', 'B', 3)
    graph.add_edge('A', 'C', 2)
    graph.add_edge('B', 'D', 6)
    graph.add_edge('B', 'E', 4)
    graph.add_edge('C', 'D', 1)
    graph.add_edge('C', 'E', 5)
    graph.add_edge('D', 'E', 6)
    
    return graph

def demonstrate_algorithms_with_stats(graph: Graph, start_id: str, goal_id: str):
    """Демонстрирует все алгоритмы и собирает статистику"""
    all_stats = []
    
    print("="*60)
    print(f"АНАЛИЗ АЛГОРИТМОВ: {start_id} → {goal_id}")
    print("="*60)
    
    # 1. Алгоритм Дейкстры
    print("\n" + "="*30)
    print("АЛГОРИТМ ДЕЙКСТРЫ")
    print("="*30)
    
    # Запуск для статистики (без визуализации для точного времени)
    stats_dijkstra, distances_dijkstra, predecessors_dijkstra, visited_dijkstra = graph.dijkstra(start_id, goal_id)
    all_stats.append(stats_dijkstra)
    
    # Визуализация отдельно
    graph.reset_visualization()
    path_dijkstra = graph.reconstruct_path_from_predecessors(predecessors_dijkstra, start_id, goal_id)
    if path_dijkstra:
        for node_id in path_dijkstra:
            if node_id in graph.nodes:
                graph.nodes[node_id].is_in_path = True
        for node in visited_dijkstra:
            node.was_visited = True
    
    # Финальная визуализация
    graph.visualize("Дейкстра - Результат", start_id, goal_id)
    
    if path_dijkstra:
        print(f"Путь найден: {' → '.join(path_dijkstra)}")
        print(f"Стоимость пути: {distances_dijkstra[goal_id]:.1f}")
        print(f"Посещено узлов: {len(visited_dijkstra)}")
    else:
        print("Путь не найден!")
    
    # 2. Алгоритм A*
    print("\n" + "="*30)
    print("АЛГОРИТМ A*")
    print("="*30)
    
    # Сброс визуализации
    graph.reset_visualization()
    
    # Запуск для статистики
    stats_a_star, path_a_star, cost_a_star, visited_a_star = graph.a_star(start_id, goal_id)
    all_stats.append(stats_a_star)
    
    # Визуализация
    if path_a_star:
        for node_id in path_a_star:
            if node_id in graph.nodes:
                graph.nodes[node_id].is_in_path = True
        for node in visited_a_star:
            node.was_visited = True
    
    # Финальная визуализация
    graph.visualize("A* - Результат", start_id, goal_id)
    
    if path_a_star:
        print(f"Путь найден: {' → '.join(path_a_star)}")
        print(f"Стоимость пути: {cost_a_star:.1f}")
        print(f"Посещено узлов: {len(visited_a_star)}")
    else:
        print("Путь не найден!")
    
    # 3. Алгоритм Беллмана-Форда
    print("\n" + "="*30)
    print("АЛГОРИТМ БЕЛЛМАНА-ФОРДА")
    print("="*30)
    
    # Сброс визуализации
    graph.reset_visualization()
    
    # Запуск для статистики
    stats_bf, distances_bf, predecessors_bf, has_negative_cycle, updated_nodes = graph.bellman_ford(start_id)
    
    # Проверяем, найден ли путь
    if not has_negative_cycle and goal_id in distances_bf and distances_bf[goal_id] < float('inf'):
        path_bf = graph.reconstruct_path_from_predecessors(predecessors_bf, start_id, goal_id)
        if path_bf:
            stats_bf.found_path = True
            stats_bf.path_length = len(path_bf)
            stats_bf.path_cost = distances_bf[goal_id]
            # Визуализация пути
            for node_id in path_bf:
                if node_id in graph.nodes:
                    graph.nodes[node_id].is_in_path = True
            for node in updated_nodes:
                node.was_visited = True
    else:
        path_bf = []
    
    all_stats.append(stats_bf)
    
    # Финальная визуализация
    graph.visualize("Беллман-Форд - Результат", start_id, goal_id)
    
    if not has_negative_cycle and path_bf:
        print(f"Путь найден: {' → '.join(path_bf)}")
        print(f"Стоимость пути: {distances_bf[goal_id]:.1f}")
        print(f"Обновлено узлов: {len(updated_nodes)}")
    elif has_negative_cycle:
        print("Обнаружен отрицательный цикл!")
    else:
        print("Путь не найден!")
    
    # Сравнение алгоритмов
    compare_algorithms(all_stats)
    
    return all_stats