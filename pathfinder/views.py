from django.shortcuts import render
from .models import Node, Edge
import heapq  # Для очереди с приоритетами
from .forms import RouteForm



def find_shortest_path(start_name, end_name):
    # Построим граф в виде словаря
    graph = {}
    for edge in Edge.objects.all():
        if edge.from_node.name not in graph:
            graph[edge.from_node.name] = []
        if edge.to_node.name not in graph:
            graph[edge.to_node.name] = []
        graph[edge.from_node.name].append((edge.to_node.name, edge.weight))
        graph[edge.to_node.name].append((edge.from_node.name, edge.weight))

    # Алгоритм Дейкстры
    priority_queue = [(0, start_name, [])]  # (текущая стоимость, текущий узел, маршрут)
    visited = set()

    while priority_queue:
        cost, current_node, path = heapq.heappop(priority_queue)

        if current_node in visited:
            continue
        visited.add(current_node)

        path = path + [current_node]

        if current_node == end_name:
            return path  # Возвращаем маршрут

        for neighbor, weight in graph.get(current_node, []):
            if neighbor not in visited:
                heapq.heappush(priority_queue, (cost + weight, neighbor, path))

    return []  # Если пути нет


def floor_map(request, floor=1):
    nodes = Node.objects.filter(floor=floor)
    edges = Edge.objects.filter(from_node__floor=floor, to_node__floor=floor)

    # Найти маршрут от 'tk' до 'room_151'
    start_node = 'tk'
    end_node = 'room_151'
    path = find_shortest_path(start_node, end_node)

    # Преобразуем маршрут в список узлов
    path_nodes = Node.objects.filter(name__in=path)

    # Определяем конечные узлы только из маршрута
    edge_count = {}
    for edge in edges:
        edge_count[edge.from_node.name] = edge_count.get(edge.from_node.name, 0) + 1
        edge_count[edge.to_node.name] = edge_count.get(edge.to_node.name, 0) + 1

    terminal_nodes_in_path = [
        node for node in path_nodes if edge_count.get(node.name, 0) == 1
    ]

    # Отправляем данные в шаблон
    return render(request, 'pathfinder/floor_map.html', {
        'nodes': terminal_nodes_in_path,  # Только конечные узлы из маршрута
        'edges': edges,
        'path_nodes': path_nodes,  # Узлы на маршруте
        'path_edges': edges.filter(from_node__name__in=path, to_node__name__in=path),  # Рёбра маршрута
        'floor': floor,
    })


