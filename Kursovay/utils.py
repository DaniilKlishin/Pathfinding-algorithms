# utils.py
import json
import tkinter as tk
from tkinter import filedialog
from typing import List  # Добавьте эту строку
from graph import Graph
from models import AlgorithmStats

def load_graph_from_json(file_path: str):
    """Загружает граф из JSON файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Создаем граф
        directed = data.get('directed', True)
        graph = Graph(directed=directed)
        graph.name = data.get('name', 'Загруженный граф')
        
        # Добавляем узлы
        nodes = data.get('nodes', [])
        for node_data in nodes:
            node_id = node_data['id']
            x = node_data.get('x', 0)
            y = node_data.get('y', 0)
            is_walkable = node_data.get('is_walkable', True)
            graph.add_node(node_id, x, y, is_walkable)
        
        # Добавляем ребра
        edges = data.get('edges', [])
        for edge_data in edges:
            from_node = edge_data['from']
            to_node = edge_data['to']
            weight = edge_data['weight']
            graph.add_edge(from_node, to_node, weight)
        
        return graph, data.get('start'), data.get('goal')
        
    except Exception as e:
        raise ValueError(f"Ошибка загрузки JSON файла: {e}")

def select_json_file() -> str:
    """Открывает диалог выбора JSON файла"""
    root = tk.Tk()
    root.withdraw()  # Скрываем основное окно
    
    file_path = filedialog.askopenfilename(
        title="Выберите JSON файл с графом",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        initialdir="."  # Текущая директория
    )
    
    return file_path

def compare_algorithms(stats_list: List[AlgorithmStats]):
    """Сравнивает статистику алгоритмов и определяет лучший"""
    print("\n" + "="*60)
    print("СРАВНЕНИЕ АЛГОРИТМОВ")
    print("="*60)
    
    # Фильтруем алгоритмы, которые нашли путь
    successful_stats = [s for s in stats_list if s.found_path]
    
    if not successful_stats:
        print("Ни один алгоритм не нашел путь!")
        return
    
    # Выводим статистику каждого алгоритма
    for stats in stats_list:
        print(f"\n{stats}")
    
    # Находим лучший алгоритм по разным критериям
    print("\n" + "-"*60)
    print("ЛУЧШИЙ АЛГОРИТМ ПО КРИТЕРИЯМ:")
    print("-"*60)
    
    # По скорости
    fastest = min(successful_stats, key=lambda x: x.execution_time)
    print(f"✓ Самый быстрый: {fastest.algorithm_name} ({fastest.execution_time:.6f} сек)")
    
    # По эффективности (наименьшее количество посещенных узлов)
    most_efficient = min(successful_stats, key=lambda x: x.visited_nodes)
    print(f"✓ Самый эффективный (посещено узлов): {most_efficient.algorithm_name} ({most_efficient.visited_nodes} узлов)")
    
    # По длине пути (если стоимость разная, может быть разный путь)
    shortest_path = min(successful_stats, key=lambda x: x.path_length)
    print(f"✓ Кратчайший путь: {shortest_path.algorithm_name} ({shortest_path.path_length} шагов)")
    
    # По стоимости пути (может быть разный путь с разной стоимостью)
    cheapest_path = min(successful_stats, key=lambda x: x.path_cost)
    print(f"✓ Самый дешевый путь: {cheapest_path.algorithm_name} ({cheapest_path.path_cost:.2f})")
    
    # Общий рейтинг (комбинация критериев)
    # Веса: время - 30%, эффективность - 30%, длина пути - 20%, стоимость - 20%
    scored_algorithms = []
    
    for stats in successful_stats:
        # Нормализуем значения (чем меньше, тем лучше)
        # Добавляем небольшую константу, чтобы избежать деления на 0
        epsilon = 1e-10
        
        # Время выполнения
        max_time = max(max(s.execution_time for s in successful_stats), epsilon)
        time_score = (stats.execution_time + epsilon) / max_time
        
        # Эффективность (посещенные узлы)
        max_efficiency = max(max(s.visited_nodes for s in successful_stats), 1)
        efficiency_score = (stats.visited_nodes + epsilon) / max_efficiency
        
        # Длина пути
        max_length = max(max(s.path_length for s in successful_stats), 1)
        length_score = (stats.path_length + epsilon) / max_length
        
        # Стоимость пути
        max_cost = max(max(s.path_cost for s in successful_stats), epsilon)
        cost_score = (stats.path_cost + epsilon) / max_cost
        
        # Общий рейтинг
        total_score = (time_score * 0.3 + efficiency_score * 0.3 + 
                      length_score * 0.2 + cost_score * 0.2)
        scored_algorithms.append((stats, total_score))
    
    # Сортируем по общему рейтингу
    scored_algorithms.sort(key=lambda x: x[1])
    best_overall = scored_algorithms[0][0]
    
    print(f"\n{'='*60}")
    print(f"🏆 ЛУЧШИЙ АЛГОРИТМ В ЦЕЛОМ: {best_overall.algorithm_name}")
    print(f"{'='*60}")
    print(f"Обоснование: оптимальное сочетание скорости, эффективности, длины и стоимости пути")
    
    # Выводим детализацию рейтинга
    print(f"\nДетализация рейтинга (чем меньше, тем лучше):")
    for stats, score in scored_algorithms:
        print(f"  {stats.algorithm_name}: {score:.4f}")

def create_sample_json_files():
    """Создает примеры JSON файлов с разными графами"""
    sample_graphs = {
        "simple_graph.json": {
            "name": "Простой граф",
            "directed": False,
            "nodes": [
                {"id": "A", "x": 1, "y": 2},
                {"id": "B", "x": 3, "y": 0},
                {"id": "C", "x": 3, "y": 4},
                {"id": "D", "x": 5, "y": 2},
                {"id": "E", "x": 7, "y": 2}
            ],
            "edges": [
                {"from": "A", "to": "B", "weight": 3},
                {"from": "A", "to": "C", "weight": 2},
                {"from": "B", "to": "D", "weight": 6},
                {"from": "B", "to": "E", "weight": 4},
                {"from": "C", "to": "D", "weight": 1},
                {"from": "C", "to": "E", "weight": 5},
                {"from": "D", "to": "E", "weight": 6}
            ],
            "start": "A",
            "goal": "E"
        },
        
        "complex_directed.json": {
            "name": "Сложный ориентированный граф",
            "directed": True,
            "nodes": [
                {"id": "S", "x": 0, "y": 2, "label": "Старт"},
                {"id": "A", "x": 2, "y": 0},
                {"id": "B", "x": 2, "y": 4},
                {"id": "C", "x": 4, "y": 1},
                {"id": "D", "x": 4, "y": 3},
                {"id": "E", "x": 6, "y": 0},
                {"id": "F", "x": 6, "y": 4},
                {"id": "G", "x": 8, "y": 2, "label": "Цель"}
            ],
            "edges": [
                {"from": "S", "to": "A", "weight": 4},
                {"from": "S", "to": "B", "weight": 3},
                {"from": "A", "to": "C", "weight": 2},
                {"from": "A", "to": "D", "weight": 5},
                {"from": "B", "to": "C", "weight": 6},
                {"from": "B", "to": "D", "weight": 1},
                {"from": "C", "to": "E", "weight": 3},
                {"from": "C", "to": "F", "weight": 4},
                {"from": "D", "to": "E", "weight": 2},
                {"from": "D", "to": "F", "weight": 5},
                {"from": "E", "to": "G", "weight": 7},
                {"from": "F", "to": "G", "weight": 2}
            ],
            "start": "S",
            "goal": "G"
        },
        
        "negative_weights.json": {
            "name": "Граф с отрицательными весами",
            "directed": True,
            "nodes": [
                {"id": "A", "x": 0, "y": 2},
                {"id": "B", "x": 2, "y": 0},
                {"id": "C", "x": 2, "y": 4},
                {"id": "D", "x": 4, "y": 2},
                {"id": "E", "x": 6, "y": 2}
            ],
            "edges": [
                {"from": "A", "to": "B", "weight": 4},
                {"from": "A", "to": "C", "weight": 3},
                {"from": "B", "to": "D", "weight": -2},
                {"from": "C", "to": "B", "weight": 1},
                {"from": "C", "to": "D", "weight": 5},
                {"from": "D", "to": "E", "weight": 3},
                {"from": "E", "to": "C", "weight": -1}
            ],
            "start": "A",
            "goal": "E",
            "description": "Содержит отрицательные веса для тестирования Беллмана-Форда"
        }
    }
    
    for filename, graph_data in sample_graphs.items():
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, indent=2, ensure_ascii=False)
            print(f"Создан файл: {filename}")
        except Exception as e:
            print(f"Ошибка создания {filename}: {e}")

def save_graph_to_json(graph, file_path, start_id=None, goal_id=None):
    """Сохраняет граф в JSON файл"""
    graph_data = {
        "name": graph.name,
        "directed": graph.is_directed,
        "nodes": [],
        "edges": []
    }
    
    if start_id:
        graph_data["start"] = start_id
    if goal_id:
        graph_data["goal"] = goal_id
    
    # Сохраняем узлы
    for node_id, node in graph.nodes.items():
        graph_data["nodes"].append({
            "id": node_id,
            "x": node.x,
            "y": node.y,
            "is_walkable": node.is_walkable
        })
    
    # Сохраняем ребра
    for edge in graph.edges:
        graph_data["edges"].append({
            "from": edge.from_node,
            "to": edge.to_node,
            "weight": edge.weight
        })
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, indent=2, ensure_ascii=False)