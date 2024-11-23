from django.db import models


class Node(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Название узла
    x = models.IntegerField()  # X-координата
    y = models.IntegerField()  # Y-координата
    floor = models.IntegerField()  # Этаж

    def __str__(self):
        return self.name

class Edge(models.Model):
    from_node = models.ForeignKey(Node, related_name='out_edges', on_delete=models.CASCADE)  # Узел-источник
    to_node = models.ForeignKey(Node, related_name='in_edges', on_delete=models.CASCADE)  # Узел-цель
    weight = models.FloatField(default=1.0)  # Вес ребра

    def __str__(self):
        return f"{self.from_node} -> {self.to_node}"
