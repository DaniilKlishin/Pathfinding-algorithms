# main.py
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog
import time
from graph import Graph
from utils import load_graph_from_json, create_sample_json_files, compare_algorithms
from demo import create_graph_from_image
from models import AlgorithmStats

class PathFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Path Finder - Алгоритмы поиска пути")
        self.root.geometry("1400x900")
        
        self.graph = None
        self.start_id = 'A'
        self.goal_id = 'E'
        self.last_execution_times = {
            "dijkstra": 0.0,
            "astar": 0.0,
            "bellman_ford": 0.0
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Создаем панель меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Загрузить из JSON", command=self.load_from_json)
        file_menu.add_command(label="Создать примеры JSON", command=self.create_samples)
        file_menu.add_command(label="Сохранить граф в JSON", command=self.save_to_json)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        graph_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Граф", menu=graph_menu)
        graph_menu.add_command(label="Использовать демо-граф", command=self.use_demo_graph)
        graph_menu.add_command(label="Добавить узел", command=self.add_node)
        graph_menu.add_command(label="Удалить узел", command=self.remove_node)
        graph_menu.add_command(label="Добавить ребро", command=self.add_edge)
        graph_menu.add_command(label="Удалить ребро", command=self.remove_edge)
        graph_menu.add_separator()
        graph_menu.add_command(label="Редактировать вес ребра", command=self.edit_edge_weight)
        graph_menu.add_command(label="Изменить координаты узла", command=self.edit_node_coordinates)
        
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка расширения ячеек
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Панель управления графом
        control_frame = ttk.LabelFrame(main_frame, text="Управление графом", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Кнопки управления графом
        ttk.Button(control_frame, text="Добавить узел", command=self.add_node, width=15).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="Удалить узел", command=self.remove_node, width=15).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Добавить ребро", command=self.add_edge, width=15).grid(row=0, column=2, padx=5)
        ttk.Button(control_frame, text="Удалить ребро", command=self.remove_edge, width=15).grid(row=0, column=3, padx=5)
        ttk.Button(control_frame, text="Изменить вес", command=self.edit_edge_weight, width=15).grid(row=0, column=4, padx=5)
        
        # Информация о графе
        info_frame = ttk.LabelFrame(main_frame, text="Информация о графе", padding="10")
        info_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        self.info_text = tk.Text(info_frame, height=4, width=80)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Выбор узлов и таблица ребер
        nodes_frame = ttk.Frame(main_frame)
        nodes_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Выбор узлов
        ttk.Label(nodes_frame, text="Стартовый узел:").grid(row=0, column=0, padx=(0, 10))
        self.start_var = tk.StringVar(value="A")
        self.start_combo = ttk.Combobox(nodes_frame, textvariable=self.start_var, width=10)
        self.start_combo.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(nodes_frame, text="Целевой узел:").grid(row=0, column=2, padx=(0, 10))
        self.goal_var = tk.StringVar(value="E")
        self.goal_combo = ttk.Combobox(nodes_frame, textvariable=self.goal_var, width=10)
        self.goal_combo.grid(row=0, column=3, padx=(0, 20))
        
        # Таблица ребер
        ttk.Label(nodes_frame, text="Ребра графа:").grid(row=0, column=4, padx=(20, 10))
        self.edges_combo = ttk.Combobox(nodes_frame, width=20)
        self.edges_combo.grid(row=0, column=5)
        ttk.Button(nodes_frame, text="Изменить вес", command=self.edit_selected_edge_weight).grid(row=0, column=6, padx=(5, 0))
        
        # Панель времени выполнения
        time_frame = ttk.LabelFrame(main_frame, text="Время выполнения алгоритмов", padding="10")
        time_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Метки для отображения времени
        self.dijkstra_time_var = tk.StringVar(value="Дейкстра: не запускался")
        self.astar_time_var = tk.StringVar(value="A*: не запускался")
        self.bellman_time_var = tk.StringVar(value="Беллман-Форд: не запускался")
        
        ttk.Label(time_frame, textvariable=self.dijkstra_time_var, width=30).grid(row=0, column=0, padx=5)
        ttk.Label(time_frame, textvariable=self.astar_time_var, width=30).grid(row=0, column=1, padx=5)
        ttk.Label(time_frame, textvariable=self.bellman_time_var, width=30).grid(row=0, column=2, padx=5)
        
        # Кнопки алгоритмов
        buttons_frame = ttk.LabelFrame(main_frame, text="Алгоритмы", padding="10")
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        ttk.Button(buttons_frame, text="Запустить Дейкстру", command=self.run_dijkstra, width=20).grid(row=0, column=0, padx=5)
        ttk.Button(buttons_frame, text="Запустить A*", command=self.run_astar, width=20).grid(row=0, column=1, padx=5)
        ttk.Button(buttons_frame, text="Запустить Беллмана-Форда", command=self.run_bellman_ford, width=20).grid(row=0, column=2, padx=5)
        ttk.Button(buttons_frame, text="Сравнить все алгоритмы", command=self.compare_all, width=20).grid(row=0, column=3, padx=5)
        
        # Визуализация графа
        vis_frame = ttk.LabelFrame(main_frame, text="Визуализация графа", padding="10")
        vis_frame.grid(row=5, column=0, columnspan=2, pady=(10, 10), sticky=(tk.W, tk.E, tk.N, tk.S))
        vis_frame.columnconfigure(0, weight=1)
        vis_frame.rowconfigure(0, weight=1)
        
        self.vis_text = scrolledtext.ScrolledText(vis_frame, width=100, height=25)
        self.vis_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Статус бар
        self.status_var = tk.StringVar(value="Готов")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def load_from_json(self):
        file_path = filedialog.askopenfilename(
            title="Выберите JSON файл с графом",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir="."
        )
        
        if file_path:
            try:
                self.graph, start, goal = load_graph_from_json(file_path)
                self.start_id = start if start else 'A'
                self.goal_id = goal if goal else 'E'
                
                self.start_var.set(self.start_id)
                self.goal_var.set(self.goal_id)
                self.update_node_combos()
                self.update_edges_combo()
                
                self.update_info()
                self.visualize_graph("Загруженный граф")
                self.status_var.set(f"Граф загружен из {file_path}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки файла: {e}")
    
    def save_to_json(self):
        if not self.graph:
            messagebox.showwarning("Нет графа", "Сначала создайте или загрузите граф")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Сохранить граф в JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            defaultextension=".json",
            initialdir="."
        )
        
        if file_path:
            try:
                graph_data = {
                    "name": self.graph.name,
                    "directed": self.graph.is_directed,
                    "nodes": [],
                    "edges": [],
                    "start": self.start_var.get(),
                    "goal": self.goal_var.get()
                }
                
                # Сохраняем узлы
                for node_id, node in self.graph.nodes.items():
                    graph_data["nodes"].append({
                        "id": node_id,
                        "x": node.x,
                        "y": node.y,
                        "is_walkable": node.is_walkable
                    })
                
                # Сохраняем ребра
                for edge in self.graph.edges:
                    graph_data["edges"].append({
                        "from": edge.from_node,
                        "to": edge.to_node,
                        "weight": edge.weight
                    })
                
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(graph_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Успех", f"Граф сохранен в {file_path}")
                self.status_var.set(f"Граф сохранен в {file_path}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка сохранения файла: {e}")
    
    def create_samples(self):
        try:
            create_sample_json_files()
            messagebox.showinfo("Успех", "Примеры JSON файлов созданы!")
            self.status_var.set("Примеры JSON файлов созданы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка создания файлов: {e}")
    
    def use_demo_graph(self):
        self.graph = create_graph_from_image()
        self.start_id = 'A'
        self.goal_id = 'E'
        
        self.start_var.set(self.start_id)
        self.goal_var.set(self.goal_id)
        self.update_node_combos()
        self.update_edges_combo()
        
        self.update_info()
        self.visualize_graph("Демонстрационный граф")
        self.status_var.set("Используется демонстрационный граф")
    
    def update_node_combos(self):
        if self.graph:
            nodes = list(self.graph.nodes.keys())
            self.start_combo['values'] = nodes
            self.goal_combo['values'] = nodes
    
    def update_edges_combo(self):
        if self.graph:
            edges_list = []
            for edge in self.graph.edges:
                edges_list.append(f"{edge.from_node} → {edge.to_node} = {edge.weight}")
            self.edges_combo['values'] = edges_list
            if edges_list:
                self.edges_combo.set(edges_list[0])
    
    def update_info(self):
        if self.graph:
            info = f"Название: {self.graph.name}\n"
            info += f"Тип: {'Ориентированный' if self.graph.is_directed else 'Неориентированный'}\n"
            info += f"Количество узлов: {len(self.graph.nodes)}\n"
            info += f"Количество ребер: {len(self.graph.edges)}\n"
            info += f"Узлы: {', '.join(self.graph.nodes.keys())}"
            
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info)
    
    def visualize_graph(self, title=""):
        if self.graph:
            # Перенаправляем вывод в текстовое поле
            import io
            import sys
            
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            try:
                self.graph.visualize(title, self.start_var.get(), self.goal_var.get())
                output = sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout
            
            self.vis_text.delete(1.0, tk.END)
            self.vis_text.insert(1.0, output)
    
    def update_time_labels(self):
        """Обновляет метки времени выполнения"""
        self.dijkstra_time_var.set(f"Дейкстра: {self.last_execution_times['dijkstra']:.6f} сек")
        self.astar_time_var.set(f"A*: {self.last_execution_times['astar']:.6f} сек")
        self.bellman_time_var.set(f"Беллман-Форд: {self.last_execution_times['bellman_ford']:.6f} сек")
    
    def add_node(self):
        if not self.graph:
            messagebox.showwarning("Нет графа", "Сначала создайте или загрузите граф")
            return
        
        # Диалог для ввода данных узла
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить узел")
        dialog.geometry("300x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="ID узла:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        id_entry = ttk.Entry(dialog, width=20)
        id_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Координата X:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        x_entry = ttk.Entry(dialog, width=20)
        x_entry.grid(row=1, column=1, padx=10, pady=10)
        x_entry.insert(0, "0")
        
        ttk.Label(dialog, text="Координата Y:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        y_entry = ttk.Entry(dialog, width=20)
        y_entry.grid(row=2, column=1, padx=10, pady=10)
        y_entry.insert(0, "0")
        
        def add_node_action():
            node_id = id_entry.get().strip()
            if not node_id:
                messagebox.showerror("Ошибка", "Введите ID узла")
                return
            
            if node_id in self.graph.nodes:
                messagebox.showerror("Ошибка", f"Узел с ID '{node_id}' уже существует")
                return
            
            try:
                x = int(x_entry.get())
                y = int(y_entry.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Координаты должны быть целыми числами")
                return
            
            self.graph.add_node(node_id, x, y)
            self.update_node_combos()
            self.update_info()
            self.visualize_graph("Граф с новым узлом")
            self.status_var.set(f"Добавлен узел: {node_id}")
            dialog.destroy()
        
        ttk.Button(dialog, text="Добавить", command=add_node_action).grid(row=3, column=0, columnspan=2, pady=20)
    
    def remove_node(self):
        if not self.graph:
            messagebox.showwarning("Нет графа", "Сначала создайте или загрузите граф")
            return
        
        if not self.graph.nodes:
            messagebox.showwarning("Нет узлов", "В графе нет узлов для удаления")
            return
        
        # Диалог для выбора узла
        node_id = simpledialog.askstring("Удалить узел", 
                                        f"Введите ID узла для удаления:\nДоступные узлы: {', '.join(self.graph.nodes.keys())}")
        
        if node_id and node_id in self.graph.nodes:
            # Удаляем узел и все связанные ребра
            del self.graph.nodes[node_id]
            # Удаляем все ребра, связанные с этим узлом
            self.graph.edges = [edge for edge in self.graph.edges 
                              if edge.from_node != node_id and edge.to_node != node_id]
            
            # Обновляем выбранные узлы если они были удалены
            if self.start_var.get() == node_id:
                if self.graph.nodes:
                    self.start_var.set(list(self.graph.nodes.keys())[0])
                else:
                    self.start_var.set("")
            
            if self.goal_var.get() == node_id:
                if self.graph.nodes:
                    self.goal_var.set(list(self.graph.nodes.keys())[0])
                else:
                    self.goal_var.set("")
            
            self.update_node_combos()
            self.update_edges_combo()
            self.update_info()
            self.visualize_graph("Граф после удаления узла")
            self.status_var.set(f"Удален узел: {node_id}")
    
    def add_edge(self):
        if not self.graph:
            messagebox.showwarning("Нет графа", "Сначала создайте или загрузите граф")
            return
        
        if len(self.graph.nodes) < 2:
            messagebox.showwarning("Мало узлов", "Для добавления ребра нужно минимум 2 узла")
            return
        
        # Диалог для ввода данных ребра
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить ребро")
        dialog.geometry("300x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Из узла:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        from_combo = ttk.Combobox(dialog, width=20, values=list(self.graph.nodes.keys()))
        from_combo.grid(row=0, column=1, padx=10, pady=10)
        if self.graph.nodes:
            from_combo.set(list(self.graph.nodes.keys())[0])
        
        ttk.Label(dialog, text="В узел:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        to_combo = ttk.Combobox(dialog, width=20, values=list(self.graph.nodes.keys()))
        to_combo.grid(row=1, column=1, padx=10, pady=10)
        if self.graph.nodes:
            to_combo.set(list(self.graph.nodes.keys())[0])
        
        ttk.Label(dialog, text="Вес ребра:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        weight_entry = ttk.Entry(dialog, width=20)
        weight_entry.grid(row=2, column=1, padx=10, pady=10)
        weight_entry.insert(0, "1.0")
        
        def add_edge_action():
            from_node = from_combo.get()
            to_node = to_combo.get()
            
            if not from_node or not to_node:
                messagebox.showerror("Ошибка", "Выберите узлы")
                return
            
            if from_node == to_node:
                messagebox.showerror("Ошибка", "Нельзя создать ребро из узла в самого себя")
                return
            
            try:
                weight = float(weight_entry.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Вес должен быть числом")
                return
            
            # Проверяем, существует ли уже такое ребро
            for edge in self.graph.edges:
                if edge.from_node == from_node and edge.to_node == to_node:
                    if messagebox.askyesno("Ребро существует", 
                                         f"Ребро из {from_node} в {to_node} уже существует.\nЗаменить его?"):
                        edge.weight = weight
                        self.update_edges_combo()
                        self.update_info()
                        self.visualize_graph("Граф с обновленным ребром")
                        self.status_var.set(f"Обновлено ребро: {from_node} → {to_node} = {weight}")
                        dialog.destroy()
                        return
                    else:
                        return
            
            self.graph.add_edge(from_node, to_node, weight)
            self.update_edges_combo()
            self.update_info()
            self.visualize_graph("Граф с новым ребром")
            self.status_var.set(f"Добавлено ребро: {from_node} → {to_node} = {weight}")
            dialog.destroy()
        
        ttk.Button(dialog, text="Добавить", command=add_edge_action).grid(row=3, column=0, columnspan=2, pady=20)
    
    def remove_edge(self):
        if not self.graph:
            messagebox.showwarning("Нет графа", "Сначала создайте или загрузите граф")
            return
        
        if not self.graph.edges:
            messagebox.showwarning("Нет ребер", "В графе нет ребер для удаления")
            return
        
        # Диалог для выбора ребра
        edge_str = simpledialog.askstring("Удалить ребро", 
                                         f"Введите ребро для удаления в формате 'из_в':\nПример: A_B\nДоступные ребра:\n" + 
                                         "\n".join([f"{edge.from_node} → {edge.to_node}" for edge in self.graph.edges]))
        
        if edge_str:
            parts = edge_str.split('_')
            if len(parts) == 2:
                from_node, to_node = parts
                from_node = from_node.strip()
                to_node = to_node.strip()
                
                # Ищем ребро для удаления
                for i, edge in enumerate(self.graph.edges):
                    if edge.from_node == from_node and edge.to_node == to_node:
                        del self.graph.edges[i]
                        if not self.graph.is_directed:
                            # Если граф неориентированный, удаляем и обратное ребро
                            for j, rev_edge in enumerate(self.graph.edges):
                                if rev_edge.from_node == to_node and rev_edge.to_node == from_node:
                                    del self.graph.edges[j]
                                    break
                        
                        self.update_edges_combo()
                        self.update_info()
                        self.visualize_graph("Граф после удаления ребра")
                        self.status_var.set(f"Удалено ребро: {from_node} → {to_node}")
                        return
                
                messagebox.showerror("Ошибка", f"Ребро {from_node} → {to_node} не найдено")
    
    def edit_edge_weight(self):
        if not self.graph:
            messagebox.showwarning("Нет графа", "Сначала создайте или загрузите граф")
            return
        
        if not self.graph.edges:
            messagebox.showwarning("Нет ребер", "В графе нет ребер для редактирования")
            return
        
        # Диалог для выбора ребра и нового веса
        dialog = tk.Toplevel(self.root)
        dialog.title("Изменить вес ребра")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Выберите ребро:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        edge_combo = ttk.Combobox(dialog, width=30)
        edge_combo.grid(row=0, column=1, padx=10, pady=10)
        
        # Заполняем список ребер
        edges_list = []
        self.edge_mapping = {}
        for edge in self.graph.edges:
            edge_str = f"{edge.from_node} → {edge.to_node} (текущий вес: {edge.weight})"
            edges_list.append(edge_str)
            self.edge_mapping[edge_str] = edge
        
        edge_combo['values'] = edges_list
        if edges_list:
            edge_combo.set(edges_list[0])
        
        ttk.Label(dialog, text="Новый вес:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        weight_entry = ttk.Entry(dialog, width=30)
        weight_entry.grid(row=1, column=1, padx=10, pady=10)
        weight_entry.insert(0, "1.0")
        
        def edit_weight_action():
            selected_edge_str = edge_combo.get()
            if not selected_edge_str:
                messagebox.showerror("Ошибка", "Выберите ребро")
                return
            
            edge = self.edge_mapping.get(selected_edge_str)
            if not edge:
                messagebox.showerror("Ошибка", "Ребро не найдено")
                return
            
            try:
                new_weight = float(weight_entry.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Вес должен быть числом")
                return
            
            old_weight = edge.weight
            edge.weight = new_weight
            
            # Если граф неориентированный, обновляем и обратное ребро
            if not self.graph.is_directed:
                for rev_edge in self.graph.edges:
                    if rev_edge.from_node == edge.to_node and rev_edge.to_node == edge.from_node:
                        rev_edge.weight = new_weight
                        break
            
            self.update_edges_combo()
            self.update_info()
            self.visualize_graph("Граф с измененным весом ребра")
            self.status_var.set(f"Изменен вес ребра {edge.from_node} → {edge.to_node}: {old_weight} → {new_weight}")
            dialog.destroy()
        
        ttk.Button(dialog, text="Изменить", command=edit_weight_action).grid(row=2, column=0, columnspan=2, pady=20)
    
    def edit_selected_edge_weight(self):
        # Редактировать вес выбранного ребра из комбобокса
        if not self.graph or not self.graph.edges:
            return
        
        selected_edge_str = self.edges_combo.get()
        if not selected_edge_str:
            return
        
        # Извлекаем информацию о ребре из строки
        try:
            # Формат: "A → B = 3"
            parts = selected_edge_str.split('→')
            from_node = parts[0].strip()
            rest = parts[1].split('=')
            to_node = rest[0].strip()
            
            # Находим ребро
            edge = None
            for e in self.graph.edges:
                if e.from_node == from_node and e.to_node == to_node:
                    edge = e
                    break
            
            if edge:
                # Запрашиваем новый вес
                new_weight = simpledialog.askfloat("Изменить вес ребра", 
                                                  f"Введите новый вес для ребра {from_node} → {to_node}:",
                                                  initialvalue=edge.weight,
                                                  minvalue=-1000.0,
                                                  maxvalue=1000.0)
                
                if new_weight is not None:
                    old_weight = edge.weight
                    edge.weight = new_weight
                    
                    # Если граф неориентированный, обновляем и обратное ребро
                    if not self.graph.is_directed:
                        for rev_edge in self.graph.edges:
                            if rev_edge.from_node == to_node and rev_edge.to_node == from_node:
                                rev_edge.weight = new_weight
                                break
                    
                    self.update_edges_combo()
                    self.update_info()
                    self.visualize_graph("Граф с измененным весом ребра")
                    self.status_var.set(f"Изменен вес ребра {from_node} → {to_node}: {old_weight} → {new_weight}")
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обработать ребро: {e}")
    
    def edit_node_coordinates(self):
        if not self.graph:
            messagebox.showwarning("Нет графа", "Сначала создайте или загрузите граф")
            return
        
        if not self.graph.nodes:
            messagebox.showwarning("Нет узлов", "В графе нет узлов для редактирования")
            return
        
        # Диалог для выбора узла и новых координат
        node_id = simpledialog.askstring("Изменить координаты узла", 
                                        f"Введите ID узла для изменения координат:\nДоступные узлы: {', '.join(self.graph.nodes.keys())}")
        
        if node_id and node_id in self.graph.nodes:
            node = self.graph.nodes[node_id]
            
            new_x = simpledialog.askinteger("Новая координата X", 
                                           f"Текущая X: {node.x}\nВведите новую координату X:",
                                           initialvalue=node.x)
            
            new_y = simpledialog.askinteger("Новая координата Y", 
                                           f"Текущая Y: {node.y}\nВведите новую координату Y:",
                                           initialvalue=node.y)
            
            if new_x is not None and new_y is not None:
                node.x = new_x
                node.y = new_y
                
                self.update_info()
                self.visualize_graph("Граф с измененными координатами")
                self.status_var.set(f"Изменены координаты узла {node_id}: ({node.x}, {node.y})")
    
    def run_dijkstra(self):
        if not self.graph:
            messagebox.showwarning("Нет графа", "Сначала загрузите или создайте граф")
            return
        
        start = self.start_var.get()
        goal = self.goal_var.get()
        
        if start not in self.graph.nodes or goal not in self.graph.nodes:
            messagebox.showwarning("Ошибка", "Указанные узлы не существуют в графе!")
            return
        
        self.status_var.set(f"Выполняется алгоритм Дейкстры: {start} → {goal}")
        self.root.update()
        
        try:
            # Используем упрощенную версию для точного измерения времени
            path, cost, exec_time = self.graph.dijkstra_simple(start, goal)
            
            # Сохраняем время выполнения
            self.last_execution_times["dijkstra"] = exec_time
            self.update_time_labels()
            
            # Теперь запускаем полную версию для визуализации
            self.graph.reset_visualization()
            stats, distances, predecessors, visited = self.graph.dijkstra(start, goal)
            
            # Визуализируем результат
            if path:
                for node_id in path:
                    if node_id in self.graph.nodes:
                        self.graph.nodes[node_id].is_in_path = True
                for node in visited:
                    node.was_visited = True
            
            self.visualize_graph("Дейкстра - Результат")
            
            # Показываем результат
            result_text = f"Алгоритм Дейкстры: {start} → {goal}\n"
            if path:
                result_text += f"Путь найден: {' → '.join(path)}\n"
                result_text += f"Стоимость пути: {cost:.1f}\n"
                result_text += f"Посещено узлов: {len(visited)}\n"
                result_text += f"Длина пути: {len(path)} шагов\n"
                result_text += f"Время выполнения: {exec_time:.6f} сек"
            else:
                result_text += "Путь не найден!"
            
            messagebox.showinfo("Результат Дейкстры", result_text)
            self.status_var.set(f"Дейкстра завершен: {start} → {goal} (время: {exec_time:.6f} сек)")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка выполнения алгоритма: {e}")
            self.status_var.set("Ошибка выполнения")
    
    def run_astar(self):
        if not self.graph:
            messagebox.showwarning("Нет графа", "Сначала загрузите или создайте граф")
            return
        
        start = self.start_var.get()
        goal = self.goal_var.get()
        
        if start not in self.graph.nodes or goal not in self.graph.nodes:
            messagebox.showwarning("Ошибка", "Указанные узлы не существуют в графе!")
            return
        
        self.status_var.set(f"Выполняется алгоритм A*: {start} → {goal}")
        self.root.update()
        
        try:
            # Используем упрощенную версию для точного измерения времени
            path, cost, exec_time = self.graph.a_star_simple(start, goal)
            
            # Сохраняем время выполнения
            self.last_execution_times["astar"] = exec_time
            self.update_time_labels()
            
            # Теперь запускаем полную версию для визуализации
            self.graph.reset_visualization()
            stats, full_path, full_cost, visited = self.graph.a_star(start, goal)
            
            # Визуализируем результат
            if full_path:
                self.visualize_graph("A* - Результат")
            
            # Показываем результат
            result_text = f"Алгоритм A*: {start} → {goal}\n"
            if path:
                result_text += f"Путь найден: {' → '.join(path)}\n"
                result_text += f"Стоимость пути: {cost:.1f}\n"
                result_text += f"Посещено узлов: {stats.visited_nodes}\n"
                result_text += f"Длина пути: {len(path)} шагов\n"
                result_text += f"Время выполнения: {exec_time:.6f} сек"
            else:
                result_text += "Путь не найден!"
            
            messagebox.showinfo("Результат A*", result_text)
            self.status_var.set(f"A* завершен: {start} → {goal} (время: {exec_time:.6f} сек)")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка выполнения алгоритма: {e}")
            self.status_var.set("Ошибка выполнения")
    
    def run_astar(self):
        if not self.graph:
            messagebox.showwarning("Нет графа", "Сначала загрузите или создайте граф")
            return
        
        start = self.start_var.get()
        goal = self.goal_var.get()
        
        if start not in self.graph.nodes or goal not in self.graph.nodes:
            messagebox.showwarning("Ошибка", "Указанные узлы не существуют в графе!")
            return
        
        self.status_var.set(f"Выполняется алгоритм A*: {start} → {goal}")
        self.root.update()
        
        try:
            # Запускаем алгоритм A*
            stats, path, cost, visited = self.graph.a_star(start, goal)
            
            # Сохраняем время выполнения
            self.last_execution_times["astar"] = stats.execution_time
            self.update_time_labels()
            
            # Визуализируем результат
            self.visualize_graph("A* - Результат")
            
            # Показываем результат
            result_text = f"Алгоритм A*: {start} → {goal}\n"
            if path:
                result_text += f"Путь найден: {' → '.join(path)}\n"
                result_text += f"Стоимость пути: {cost:.1f}\n"
                result_text += f"Посещено узлов: {len(visited)}\n"
                result_text += f"Длина пути: {len(path)} шагов\n"
                result_text += f"Время выполнения: {stats.execution_time:.6f} сек"
            else:
                result_text += "Путь не найден!"
            
            messagebox.showinfo("Результат A*", result_text)
            self.status_var.set(f"A* завершен: {start} → {goal} (время: {stats.execution_time:.6f} сек)")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка выполнения алгоритма: {e}")
            self.status_var.set("Ошибка выполнения")
    
    def run_bellman_ford(self):
        if not self.graph:
            messagebox.showwarning("Нет графа", "Сначала загрузите или создайте граф")
            return
        
        start = self.start_var.get()
        goal = self.goal_var.get()
        
        if start not in self.graph.nodes or goal not in self.graph.nodes:
            messagebox.showwarning("Ошибка", "Указанные узлы не существуют в графе!")
            return
        
        self.status_var.set(f"Выполняется алгоритм Беллмана-Форда: {start} → {goal}")
        self.root.update()
        
        try:
            # Измеряем время выполнения
            start_time = time.perf_counter()
            stats, distances, predecessors, has_negative_cycle, updated_nodes = self.graph.bellman_ford(start)
            exec_time = time.perf_counter() - start_time
            
            # Сохраняем время выполнения
            self.last_execution_times["bellman_ford"] = exec_time
            self.update_time_labels()
            
            # Проверяем, найден ли путь
            path = []
            if not has_negative_cycle and goal in distances and distances[goal] < float('inf'):
                path = self.graph.reconstruct_path_from_predecessors(predecessors, start, goal)
                if path:
                    # Визуализируем результат
                    self.graph.reset_visualization()
                    for node_id in path:
                        if node_id in self.graph.nodes:
                            self.graph.nodes[node_id].is_in_path = True
                    for node in updated_nodes:
                        node.was_visited = True
            
            self.visualize_graph("Беллман-Форд - Результат")
            
            # Показываем результат
            result_text = f"Алгоритм Беллмана-Форда: {start} → {goal}\n"
            if has_negative_cycle:
                result_text += "Обнаружен отрицательный цикл!\n"
                result_text += f"Время выполнения: {exec_time:.6f} сек"
            elif path:
                result_text += f"Путь найден: {' → '.join(path)}\n"
                result_text += f"Стоимость пути: {distances[goal]:.1f}\n"
                result_text += f"Обновлено узлов: {len(updated_nodes)}\n"
                result_text += f"Длина пути: {len(path)} шагов\n"
                result_text += f"Время выполнения: {exec_time:.6f} сек"
            else:
                result_text += "Путь не найден!"
            
            messagebox.showinfo("Результат Беллмана-Форда", result_text)
            self.status_var.set(f"Беллман-Форд завершен: {start} → {goal} (время: {exec_time:.6f} сек)")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка выполнения алгоритма: {e}")
            self.status_var.set("Ошибка выполнения")
    
    def compare_all(self):
        if not self.graph:
            messagebox.showwarning("Нет графа", "Сначала загрузите или создайте граф")
            return
        
        start = self.start_var.get()
        goal = self.goal_var.get()
        
        if start not in self.graph.nodes or goal not in self.graph.nodes:
            messagebox.showwarning("Ошибка", "Указанные узлы не существуют в графе!")
            return
        
        self.status_var.set(f"Сравнение всех алгоритмов: {start} → {goal}")
        self.root.update()
        
        try:
            # Запускаем сравнение алгоритмов с точным измерением времени
            all_stats = []
            
            # Дейкстра
            path_dijkstra, cost_dijkstra, time_dijkstra = self.graph.dijkstra_simple(start, goal)
            stats_dijkstra = AlgorithmStats("Дейкстра")
            stats_dijkstra.execution_time = time_dijkstra
            stats_dijkstra.found_path = bool(path_dijkstra)
            stats_dijkstra.path_length = len(path_dijkstra) if path_dijkstra else 0
            stats_dijkstra.path_cost = cost_dijkstra if path_dijkstra else 0
            all_stats.append(stats_dijkstra)
            
            # A*
            path_astar, cost_astar, time_astar = self.graph.a_star_simple(start, goal)
            stats_astar = AlgorithmStats("A*")
            stats_astar.execution_time = time_astar
            stats_astar.found_path = bool(path_astar)
            stats_astar.path_length = len(path_astar) if path_astar else 0
            stats_astar.path_cost = cost_astar if path_astar else 0
            all_stats.append(stats_astar)
            
            # Беллман-Форд
            start_time_bf = time.perf_counter()
            stats_bf, distances_bf, predecessors_bf, has_negative_cycle, updated_nodes = self.graph.bellman_ford(start)
            time_bf = time.perf_counter() - start_time_bf
            stats_bf.execution_time = time_bf
            if not has_negative_cycle and goal in distances_bf and distances_bf[goal] < float('inf'):
                path_bf = self.graph.reconstruct_path_from_predecessors(predecessors_bf, start, goal)
                if path_bf:
                    stats_bf.found_path = True
                    stats_bf.path_length = len(path_bf)
                    stats_bf.path_cost = distances_bf[goal]
            all_stats.append(stats_bf)
            
            # Сохраняем время выполнения для отображения
            self.last_execution_times["dijkstra"] = time_dijkstra
            self.last_execution_times["astar"] = time_astar
            self.last_execution_times["bellman_ford"] = time_bf
            self.update_time_labels()
            
            # Перенаправляем вывод compare_algorithms в строку
            import io
            import sys
            
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            try:
                # Сравниваем алгоритмы
                compare_algorithms(all_stats)
                comparison_result = sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout
            
            # Показываем результат сравнения
            comparison_window = tk.Toplevel(self.root)
            comparison_window.title("Сравнение алгоритмов")
            comparison_window.geometry("800x600")
            
            text_widget = scrolledtext.ScrolledText(comparison_window, width=100, height=30)
            text_widget.pack(expand=True, fill='both', padx=10, pady=10)
            text_widget.insert(1.0, comparison_result)
            text_widget.config(state=tk.DISABLED)
            
            # Визуализируем лучший путь
            self.graph.reset_visualization()
            # Визуализируем путь Дейкстры (или первый найденный)
            if path_dijkstra:
                for node_id in path_dijkstra:
                    if node_id in self.graph.nodes:
                        self.graph.nodes[node_id].is_in_path = True
            
            self.visualize_graph("Сравнение алгоритмов - Результат")
            
            self.status_var.set(f"Сравнение завершено: {start} → {goal}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сравнения алгоритмов: {e}")
            self.status_var.set("Ошибка сравнения")

def main():
    root = tk.Tk()
    app = PathFinderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()