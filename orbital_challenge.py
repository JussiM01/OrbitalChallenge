from math import radians, sin, cos, sqrt
from collections import defaultdict
from heapq import *
import csv
import urllib.request
import codecs

url = 'https://space-fast-track.herokuapp.com/generate'
response = urllib.request.urlopen(url)
file = csv.reader(codecs.iterdecode(response, 'utf-8'))
data = [line for line in file]

seed = ''.join(data[0]).replace('#', '')
satellites = {tuple(node) for node in data[1:21]}
start = tuple(['start'] + data[21][1:3] + [0])
end = tuple(['end'] + data[21][3:5] + [0])
sampleSet = satellites.union({start, end})

def cartesian(position):
    r =  6371 + position[2]
    x = r * cos(radians(position[1])) * sin(radians(90 - position[0]))
    y = r * sin(radians(position[1])) * sin(radians(90 - position[0]))
    z = r * cos(radians(90 - position[0]))
    return (x, y, z)

def stringsToFloats(stringList): return [float(s) for s in stringList]

nodes = {item[0:1] + cartesian(stringsToFloats(item[1:])) for item in sampleSet}

def dot(pointA, pointB): return sum([pointA[i] * pointB[i] for i in range(3)])

def diff(pointA, pointB): return tuple(pointA[i] - pointB[i] for i in range(3))

def normSquared(point): return dot(point, point)

def connected(nodeA, nodeB): # See the comment at the bottom.
    a, b = nodeA[1:], nodeB[1:]
    t = - dot(a, diff(b, a)) / normSquared(diff(b, a))
    dTo2 = ((normSquared(a) * normSquared(diff(b, a)) - dot(a, diff(b, a))**2)
         / normSquared(diff(b, a)))
    if dTo2 > (6371) ** 2: return True
    if t >= 1 or t <= 0: return True 
    return False

def distance(nodeA, nodeB): return sqrt(normSquared(diff(nodeA[1:], nodeB[1:])))

edges = {(nodeA[0], nodeB[0], distance(nodeA, nodeB)) for nodeA in nodes
         for nodeB in nodes if nodeA[0] != nodeB[0] and connected(nodeA, nodeB)}

def dijkstra(edges, first, last):
    graph = defaultdict(list)
    for left, right, dist in edges:
        graph[left].append((dist, right))
    q, visited = [(0, first, ())], set()
    while q:
        (distance, v1, path) = heappop(q)
        if v1 not in visited:
            visited.add(v1)
            path = (v1, path)
            if v1 == last: return (distance, path)
            for dist, v2 in graph.get(v1, ()):
                if v2 not in visited:
                    heappush(q, (distance + dist, v2, path))
    return float('inf')

def shortestPath(edges, f, t):
    solution = dijkstra(edges, f, t)
    if solution == float('inf'): return 'No connecting path found.'
    path = []
    while 1:
        if solution[0] == 'start': break
        path.append(solution[0])
        solution = solution[1]
    return ','.join(path[:1:-1])

print(shortestPath(edges, 'start', 'end'))
print(seed)
