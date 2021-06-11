#!/usr/bin/env python
import networkx as nx
import networkx.algorithms as alg
import tyrell.spec as S
from tyrell.interpreter import PostOrderInterpreter
from tyrell.enumerator import SmtEnumerator, RelaxedRandomEnumerator, Enumerator
from tyrell.decider import Example, ExampleDecider, ExampleConstraintDecider, ExampleConstraintPruningDecider
from tyrell.synthesizer import Synthesizer
from tyrell.logger import get_logger
from get_input import *
from tyrell.decider import eval_expr
import matplotlib.pyplot as plt
import time
import numpy as np
from random import randint,choice
logger = get_logger('tyrell')

class Interp(PostOrderInterpreter):
    def eval_num_conn_comp(self,node,args):
        return alg.components.number_connected_components(args[0])
    def eval_num_node_disjoint_paths(self,node,args):
        if args[1] == args[2]:
            return -1
        if not nx.has_path(args[0],int(args[1]),int(args[2])):
            return []
        if G.has_edge(int(args[1]),int(args[2])):
            return -1
        a = alg.connectivity.disjoint_paths.node_disjoint_paths(args[0],int(args[1]),int(args[2]))
        return list(a)
    def eval_num_edge_disjoint_paths(self,node,args):
        if args[1] == args[2]:
            return -1
        if not nx.has_path(args[0],int(args[1]),int(args[2])):
            return []
        a = alg.connectivity.disjoint_paths.edge_disjoint_paths(args[0],int(args[1]),int(args[2]))
        return list(a)
    def eval_maximum_matching(self,node,args):
        return alg.matching.max_weight_matching(args[0],maxcardinality=True)
    def eval_minimum_edge_cut(self,node,args):
        if not nx.is_connected(args[0]):
            return []
        return nx.algorithms.connectivity.cuts.minimum_edge_cut(args[0])
    def eval_max_core(self,node,args):
        return alg.core.k_core(args[0]).nodes
    def eval_shortest_path(self,node,args):
        if not nx.has_path(args[0],int(args[1]),int(args[2])):
            return -1
        return alg.shortest_paths.unweighted.bidirectional_shortest_path(args[0],int(args[1]),int(args[2]))
    def eval_min_cut(self,node,args):
        if args[1] == args[2]:
            return -1
        return nx.algorithms.connectivity.cuts.minimum_edge_cut(args[0],s=int(args[1]),t=int(args[2]))
  
def equal_size(output,ex_output):
    exp_size = ex_output
    if type(ex_output) != int:
        exp_size = len(ex_output)
    if type(output) == int:
        return output == exp_size
    return len(output) == exp_size
def main(examples):
    min_nodes = -1
    min_G = None
    for ex in examples:
        if len(ex[0].nodes) < min_nodes or min_nodes == -1:
            min_nodes = len(ex[0].nodes)
            min_G = ex[0]
    
    dsl = construct_dsl(min_G,file='graph_synth.tyrell')
    #print(dsl)
    example_list = [Example(input=[ex[0]],output=ex[1]) for ex in examples]
    logger.info('Parsing Spec...')
    # TBD: parse the DSL definition file and store it to `spec`
    #spec = S.parse_file('./graph_expander.tyrell')
    spec = S.parse(dsl)
    #spec = S.parse_file('../Trinity/example/morpheus.tyrell')
    logger.info('Parsing succeeded')

    logger.info('Building synthesizer...')

    inter = Interp()
    synthesizer = Synthesizer(
        enumerator=SmtEnumerator(spec, depth=1,loc = 1),
        decider=ExampleConstraintDecider(
            spec=spec, # TBD: provide the spec here
            interpreter=inter, # Question Hole
            examples= example_list, # TBD: provide the example here
            equal_output=equal_size
        )
    )
    logger.info('Synthesizing programs...')

    prog = synthesizer.synthesize()
    if prog is not None:
        logger.info('Solution found: {}'.format(prog))
        #Test = Interp.eval(Interp,prog,args=[G])
        # Test = inter.eval(prog,[Gc])
        # # A,B = nx.bipartite.sets(Test)
        # # print(A)
        # A2 = set()
        # # for i in A:
        # #     if i in G.nodes:
        # #         A2.add(i)
        # # print(G.nodes,type(G.nodes))
        # # print(A2)
        # fig, axes = plt.subplots(nrows=1, ncols=2)
        # axes[0].set_title('Input')
        # axes[1].set_title('Output')
        # # nx.draw_networkx(G,ax=axes[0],pos = nx.drawing.layout.bipartite_layout(G,A2))
        # # nx.draw_networkx(Test,ax=axes[1],pos = nx.drawing.layout.bipartite_layout(Test,A))
        # nx.draw_networkx(G,ax=axes[0])
        # nx.draw_networkx(Test,ax=axes[1])

        
        # plt.show()
        # print(G.edges())
        #return G
    else:
        logger.info('Solution not found!')
    

def gen_random_graph(n):
    G = nx.Graph()
    nodes = np.arange(n)+1
    G.add_nodes_from(nodes)
    all_edges = []
    for i in nodes:
        for j in nodes[i:]:
            all_edges.append((i,j))
    m = randint(n-1, n*(n-1)/2)
    #print(all_edges)
    for i in range(m):
        u,v = choice(all_edges)
        all_edges.remove((u,v))
        G.add_edge(u,v)
    return G

        
    

if __name__ == '__main__':
    #logger.setLevel('DEBUG')
    # s = time.time()
    # main('b',11)
    # e = time.time()
    # print(e-s)
    examples = []
    inter = Interp()
    x = [i for i in range(1,11)]
    y = np.zeros(len(x))
    for j in x:
        for i in range(5):
            G = gen_random_graph(j)
            answer = len(inter.eval_max_core(None,[G]))
            if i == 4:
                answer = -2
            examples.append((G,answer))
            #print(G.nodes)
            s = time.time()
        #print(examples[4])
        main(examples)
        e = time.time()
        print("Trial:",j,"Time:", e-s)
        y[j-1]=e-s

    plt.bar(x,y)
    plt.xlabel("Number Of Nodes")
    plt.ylabel("Time")
    plt.title("Time to Enumerate all programs with 5 examples")
    plt.show()
