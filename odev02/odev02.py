import sys

#airport names
airlines = set()
#connections btw airports
links = []

#reading data from the file
with open("airlines.txt", "r") as a_file:
    for line in a_file:
        stripped_line = line.strip()
        links.append((stripped_line))
        airline = stripped_line.split(",")
        for alname in airline:
            airlines.add(alname)

#using dictionary as a graph
my_graph = {}
for al in airlines:
    my_graph[al] = []

keys = my_graph.keys()

#inserting connections to my graph
for key in keys:

    for link in links:
        a = link.split(",")
        if key in a:
            my_graph[key].extend(a)

#eliminating duplicates
for key in keys:
    my_set = set(my_graph[key])
    my_set.discard(key)
    my_list = list(my_set)
    my_graph[key] = my_list

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

args = sys.argv



def find_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    for node in graph[start]:
        if node not in path:
            newpath = find_path(graph, node, end, path)
            if newpath: return newpath
    return None


# path = find_path(my_graph,"Aria","Avolar")
# print(path)


def find_shortest_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path

    shortest = None
    for node in graph[start]:
        if node not in path:
            newpath = find_shortest_path(graph, node, end, path)
            if newpath:
                if not shortest or len(newpath) < len(shortest):
                    shortest = newpath
    return shortest

print("shortest path")
print(find_shortest_path(my_graph,args[1],args[2]))