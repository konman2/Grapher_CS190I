#!/usr/bin/env python
import networkx as nx
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
logger = get_logger('tyrell')

class Interp(PostOrderInterpreter):
    def eval_get_node(self, node, args):
        return int(args[0])
    def eval_plus_node(self,node,args):
        return args[0]+1
    def eval_add_node(self,node,args):
        g = args[0].copy()
        j = 1
        for i in sorted(g.nodes):
            if j != i:
                break
            j+=1
        g.add_node(j)
        return g
    
    def eval_remove_node(self,node, args):
        g = args[0].copy()
        v = args[1]
        if v in g.nodes():
            g.remove_node(v)
        return g
    def eval_add_edge(self,node, args):
        #print(args)
        g = args[0].copy()
        
        u = int(args[1])
        v = int(args[2])
        if v in g.nodes() and u in g.nodes() and u != v:
            g.add_edge(u,v)
        #print(g.edges)
        return g
    def eval_remove_edge(self,node,args):
        #print(args)
        g = args[0].copy()
        u = args[1]
        v = args[2]
        if v in g.nodes() and u in g.nodes() and g.has_edge(u,v):
            g.remove_edge(u,v)
        return g
    def apply_num_edges(self,val):
        return val.number_of_edges()
    def apply_num_nodes(self,val):
        return val.number_of_nodes()


# class ExampleConstraintDecider(ExampleDecider):
#     _imply_map: ImplyMap
#     _assert_handler: AssertionViolationHandler

#     def __init__(self,
#                  spec: TyrellSpec,
#                  interpreter: Interpreter,
#                  examples: List[Example],
#                  equal_output: Callable[[Any, Any], bool]=lambda x, y: x == y):
#         super().__init__(interpreter, examples, equal_output)
#         self._imply_map = self._build_imply_map(spec)
#         self._assert_handler = AssertionViolationHandler(spec, interpreter)
def graph_equal_bipart(G,Gp):
    #print(G.nodes,Gp.nodes,G.edges,Gp.edges)
    if nx.bipartite.is_bipartite(G) and nx.is_connected(G):
        return True
    return False
def graph_equal_tree(G,Gp):
    if nx.is_tree(G):
        return True
    return False
def graph_equal_chordal(G,Gp):
    if nx.algorithms.chordal.is_chordal(G) and nx.is_connected(G):
        return True
    return False
def main(which,add):
    G = get_G(which)
    Gc = G.copy()
    add_nodes(Gc,add)
    dsl = construct_dsl(Gc)
    f = graph_equal_bipart
    max_d = 0
    print(nx.is_bipartite(Gc))
    min_d = len(Gc.nodes)**2
    if which == 'b':
        min_d = len(Gc.nodes)-len(Gc.edges)+1
        max_d = len(Gc.nodes)**2
    if which == 't':
        f = graph_equal_tree
        min_d = len(Gc.nodes)-len(Gc.edges)-1
        max_d = len(Gc.nodes)-len(Gc.edges)-1
    if which == 'c':
        f = graph_equal_chordal
        min_d = len(Gc.nodes)+1
        max_d = len(Gc.nodes)**2
    #print(Interp.eval_add_edge(Interp,node = None,args=[G,12,15]).edges())
    # c = G
    # c.add_node(1)
    # c.remove_node(2)
    # c.remove_node(0)
    logger.info('Parsing Spec...')
    # TBD: parse the DSL definition file and store it to `spec`
    #spec = S.parse_file('./graph_expander.tyrell')
    spec = S.parse(dsl)
    #spec = S.parse_file('../Trinity/example/morpheus.tyrell')
    logger.info('Parsing succeeded')

    logger.info('Building synthesizer...')
    # print(enumerator.next())
    # synthesizer = Synthesizer(
    #     enumerator=RelaxedRandomEnumerator(spec, max_depth=3, min_depth=0, seed=None),
    #     decider=ExampleConstraintDecider(
    #         spec=spec, # TBD: provide the spec here
    #         interpreter=Interp(),
    #         examples= [Example(input=[G], output=Gp)], # TBD: provide the example here
    #         equal_output=graph_equal
    #     )
    # )
    #print(len(Gc.nodes),len(Gc.edges),max_d,min_d)
    inter = Interp()
    synthesizer = Synthesizer(
        enumerator=RelaxedRandomEnumerator(spec, max_depth=max_d, min_depth=min_d, seed=None),
        #enumerator=SmtEnumerator(spec, depth=5,loc = 5),
        decider=ExampleConstraintDecider(
            spec=spec, # TBD: provide the spec here
            interpreter=inter, # Question Hole
            examples= [Example(input=[Gc], output=nx.Graph())], # TBD: provide the example here
            equal_output=f
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
    


if __name__ == '__main__':
    #logger.setLevel('DEBUG')
    # s = time.time()
    # main('b',11)
    # e = time.time()
    # print(e-s)
    x = [i for i in range(1,11)]
    y = np.zeros(len(x))
    num_iter = 10
    for i in range(num_iter):
        for i in x:
            s = time.time()
            main('c',i)
            e = time.time()
            y[i-1]+=(e-s)
            print(i,e-s)
    y/=num_iter
    plt.bar(x,y)
    plt.xlabel('Number of additional nodes')
    plt.ylabel('Time Taken')
    plt.show()