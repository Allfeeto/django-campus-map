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
    form = RouteForm()

    path_nodes = []
    path_edges = []
    terminal_nodes = []

    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            start_node = form.cleaned_data['start'].name
            end_node = form.cleaned_data['end'].name

            # Найти маршрут
            path = find_shortest_path(start_node, end_node)
            path_nodes = Node.objects.filter(name__in=path)
            path_edges = edges.filter(from_node__name__in=path, to_node__name__in=path)

            # Добавляем только начальный и конечный узлы маршрута
            terminal_nodes = [
                Node.objects.get(name=start_node),
                Node.objects.get(name=end_node)
            ]

    return render(request, 'pathfinder/floor_map.html', {
        'form': form,  # Форма для выбора начальной и конечной точки
        'nodes': terminal_nodes,  # Только начальный и конечный узлы
        'edges': edges,
        'path_nodes': path_nodes,
        'path_edges': path_edges,
        'floor': floor,
    })



