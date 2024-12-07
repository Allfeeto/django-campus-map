from django.shortcuts import render
from .models import Node, Edge
import heapq  # Для очереди с приоритетами
from .forms import RouteForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)


def find_shortest_path(start_name, end_name):
    # Построение графа
    graph = {}

    for edge in Edge.objects.all():
        if edge.from_node.floor == edge.to_node.floor:
            # Рёбра на одном этаже
            if edge.from_node.name not in graph:
                graph[edge.from_node.name] = []
            if edge.to_node.name not in graph:
                graph[edge.to_node.name] = []
            graph[edge.from_node.name].append((edge.to_node.name, edge.weight))
            graph[edge.to_node.name].append((edge.from_node.name, edge.weight))

        elif edge.from_node.floor != edge.to_node.floor:
            # Лестницы или рёбра между этажами
            if edge.from_node.name not in graph:
                graph[edge.from_node.name] = []
            if edge.to_node.name not in graph:
                graph[edge.to_node.name] = []
            graph[edge.from_node.name].append((edge.to_node.name, edge.weight))
            graph[edge.to_node.name].append((edge.from_node.name, edge.weight))

    # Алгоритм Дейкстры
    priority_queue = [(0, start_name, [])]  # (стоимость, текущий узел, путь)
    visited = set()

    while priority_queue:
        cost, current_node, path = heapq.heappop(priority_queue)

        if current_node in visited:
            continue
        visited.add(current_node)

        path = path + [current_node]

        if current_node == end_name:
            return path  # Возвращаем полный маршрут

        for neighbor, weight in graph.get(current_node, []):
            if neighbor not in visited:
                heapq.heappush(priority_queue, (cost + weight, neighbor, path))

    return []  # Если нет пути


def floor_map(request):
    logger.debug("Received request for floor_map with GET data: %s", request.GET)
    floor = request.GET.get('floor', 1)  # Получаем этаж из параметра запроса (по умолчанию первый этаж)
    start_node_name = request.GET.get('start')  # Начальная точка
    end_node_name = request.GET.get('end')    # Конечная точка

    # Получаем все узлы и рёбра для этого этажа
    nodes = Node.objects.filter(floor=floor)
    edges = Edge.objects.filter(from_node__floor=floor, to_node__floor=floor)

    form = RouteForm()
    path_nodes = []
    path_edges = []
    terminal_nodes = []

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = RouteForm(request.POST)
        if form.is_valid():
            start_node = form.cleaned_data['start'].name
            end_node = form.cleaned_data['end'].name

            # Получаем путь
            path = find_shortest_path(start_node, end_node)
            path_nodes = Node.objects.filter(name__in=path)
            path_edges = edges.filter(from_node__name__in=path, to_node__name__in=path)

            terminal_nodes = [
                get_object_or_404(Node, name=start_node),
                get_object_or_404(Node, name=end_node)
            ]

            # Генерация оверлея для маршрута
            path_overlay = render_to_string('pathfinder/_path_overlay.html', {
                'path_edges': path_edges,
                'nodes': terminal_nodes,
            })

            return JsonResponse({'path_overlay': path_overlay})




    elif request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        floor = request.GET.get('floor')
        start_node_name = request.GET.get('start')
        end_node_name = request.GET.get('end')

        if start_node_name and end_node_name:
            try:
                start_node = get_object_or_404(Node, name=start_node_name)
                end_node = get_object_or_404(Node, name=end_node_name)

                path = find_shortest_path(start_node_name, end_node_name)
                path_nodes = Node.objects.filter(name__in=path)
                path_edges = Edge.objects.filter(from_node__name__in=path, to_node__name__in=path)

                terminal_nodes = [start_node, end_node]

                # Генерация оверлея для маршрута
                path_overlay = render_to_string('pathfinder/_path_overlay.html', {
                    'path_edges': path_edges,
                    'nodes': terminal_nodes,
                })

                map_html = render_to_string('pathfinder/_floor_map_part.html', {
                    'nodes': Node.objects.filter(floor=floor),
                    'edges': Edge.objects.filter(from_node__floor=floor, to_node__floor=floor),
                    'path_nodes': path_nodes,
                    'path_edges': path_edges,
                    'floor': floor,
                })
                route_form_html = render_to_string('pathfinder/_route_form.html', {
                    'start_node': start_node_name,
                    'end_node': end_node_name,
                })

                return JsonResponse({
                    'map_html': map_html,
                    'path_overlay': path_overlay,
                    'route_form_html': route_form_html
                })

            except Node.DoesNotExist:
                return JsonResponse({'error': 'One of the nodes does not exist.'}, status=404)
        else:
            # Если начальная и конечная точки не выбраны, то просто переключаем схему на выбранную карту
            map_html = render_to_string('pathfinder/_floor_map_part.html', {
                'nodes': Node.objects.filter(floor=floor),
                'edges': Edge.objects.filter(from_node__floor=floor, to_node__floor=floor),
                'path_nodes': [],
                'path_edges': [],
                'floor': floor,
            })

            return JsonResponse({'map_html': map_html})



    return render(request, 'pathfinder/floor_map.html', {
        'form': form,
        'nodes': terminal_nodes,
        'edges': edges,
        'path_nodes': path_nodes,
        'path_edges': path_edges,
        'floor': floor,
    })







