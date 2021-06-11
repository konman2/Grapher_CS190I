#OPTIONS: Maintain-Bipartite, Minimum # of edges == average degree, maintain Tree, Shortest distance from vertex
import networkx as nx
import sys
def construct_dsl(G,file='graph_expander.tyrell'):
    f = open(file).read()
    s = "enum Node {\n"
    for i in sorted(G.nodes):
        s+="\""+str(i)+"\","
    s = s[:-1] + "\n}\n"
    #print(s+f)
    return s+f+"\n"
# f  = sys.argv[0]
# choice = sys.argv[1]
# add_nodes = int(sys.argv[2])
def add_nodes(G,add_nodes):
    m= max(G.nodes())+1
    for n in range(m,m+add_nodes):
        G.add_node(n)
def get_G(which):
    G = nx.Graph()
    G.add_nodes_from([1,2,3,4,5])
    if which == 'b':
        G.add_edge(1,3)
        G.add_edge(2,3)
        G.add_edge(2,4)
    if which == 't':
        G.add_edge(1,3)
        G.add_edge(3,4)
        G.add_edge(2,4)
        G.add_edge(1,5)
    if which == 'c':
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(3,4)
        G.add_edge(4,5)
        G.add_edge(5,1)
        G.add_edge(1,4)
        G.add_edge(1,5)
    return G


