import sys
import os
import getpass #to get username for AUTHOR line
import io
from numpy.core.defchararray import isdecimal

from multivitamin.custom import labelsep
from multivitamin.utils.parser import parse_graph
from multivitamin.supp.molecule_dicts import atomic_number_to_element, get_size_by_element


def write_graph(graph, path, out_name):
    if out_name == None:
        out_name = graph.id
    f = open("{}{}{}.graph".format( os.getcwd(), path, out_name ), 'w+')
    f.write("// {}\n".format( graph.newick ))
    f.write("AUTHOR: {}\n".format( getpass.getuser() ))
    f.write("#nodes;{}\n".format( len(graph.nodes) ))
    f.write("#edges;{}\n".format( len(graph.edges) ))
    f.write("Nodes labelled;{}\n".format( graph.nodes_are_labelled) )
    f.write("Edges labelled;{}\n".format(graph.edges_are_labelled) )
    f.write("Directed graph;{}\n".format( graph.is_directed ))

    f.write("\n")

    for node in (graph.nodes):
        mult_id_label = ""
        for id in node.mult_id:
            mult_id_label += id
            mult_id_label += "°"
        mult_id_label = mult_id_label[:-1]

        node.mult_id = mult_id_label # this is only done because the graph is not used any further internally

        if not node.label:
            f.write("{}\n".format( mult_id_label ))
        else:
            label_string = ""
            for el in node.label:
                label_string += el
                label_string += labelsep
            label_string = label_string[:-1]
            f.write("{};{}\n".format( mult_id_label, label_string ))

    f.write("\n")

    if not graph.edges_are_labelled:
        for edge in graph.edges:
            f.write("{};{}\n".format( edge.node1.mult_id, edge.node2.mult_id ))
    else:
        for edge in graph.edges:
            f.write("{};{};{}\n".format( edge.node1.mult_id, edge.node2.mult_id, edge.label ))

    f.close()

    print("Saved graph as {}.graph".format( out_name ))


def write_shorter_graph( graph, path ):
    f = open("{}{}{}.shorter.graph".format( os.getcwd(), path, graph.id ), 'w+')
    f.write("// {}\n".format( graph.newick ))
    f.write("AUTHOR: {}\n".format( getpass.getuser() ))
    f.write("#nodes;{}\n".format( len(graph.nodes) ))
    f.write("#edges;{}\n".format( len(graph.edges) ))
    f.write("Nodes labelled;{}\n".format( graph.nodes_are_labelled) )
    f.write("Edges labelled;{}\n".format(graph.edges_are_labelled) )
    f.write("Directed graph;{}\n".format( graph.is_directed ))

    f.write("\n")

    i = 1
    for node in (graph.nodes):
        node.id = i
        if node.label == []:
            f.write("{}\n".format( node.id ))
        else:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            f.write("{};".format( node.id ))
            label_string = ""
            for el in node.label:
                label_string += el
                label_string += labelsep
            label_string = label_string[:-1]
            f.write("{}\n".format( label_string ))
        i += 1

    f.write("\n")

    if not graph.edges_are_labelled:
        for edge in graph.edges:
            f.write("{};{}\n".format( edge.node1.id, edge.node2.id ))
    else:
        for edge in graph.edges:
            f.write("{};{};{}\n".format( edge.node1.id, edge.node2.id, edge.label ))

    f.close()

    print("Saved graph as {}.shorter.graph".format( graph.id ))


def find_consensus_labelling(graph):
    """
    Takes a graph and returns a dictionary with it's nodes as keys and the appropriate consensus labels as values.
    Iff all node labels can be interpreted as element numbers according to multiVitamin/supp/molecule_dicts.py: atomic_numbers_to_elements, it also translates the labels. 
    """
    
    def classify_scores(score):
        if score is not None:
            if score <= 0.5 :
                return 51
            elif score <= 0.8:
                return 80
            else:
                return 100
        else: 
            return -1
    
    consensus = dict()
    temp_scores = dict()
    is_element_numbered = all(map(lambda node: all(map(lambda l: l in atomic_number_to_element, node.label)),graph.nodes)) # if all labels can be interpreted as element numbers
    for node in graph.nodes:
        consensus[node], temp_scores[node] = __consensus__(node, is_element_numbered)
    scores = {k: classify_scores(v) for k, v in temp_scores.items()}
    return (consensus, scores) 


def __consensus__(node, condition):
    hist = dict()
    node_label_set = map(lambda e: atomic_number_to_element[e], set(node.label)) if condition else set(node.label) # translate element numbers to element symbols if possible, else use normal labels
    for l in node_label_set:
        hist[l] = node.label.count(l)
    hist["-"] = 0
    maxim = max(hist.values())
    cons = list()
    for lab in hist.keys():
        if hist[lab] == maxim:
            cons.append(lab)
    temp_score = hist[cons[0]]/sum(hist.values()) if len(cons) else None
    return ("|".join(cons), temp_score)


def generate_html_vis(graph):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)
    template = open("{}/template.html".format(dir_path), 'r') #make windows compatible
    try:
        vis = open("{}.visualization.html".format( graph.id ), 'w+')
        for line in template.readlines():
            if line.startswith('{DATASET}'):
                vis.write(write_to_json(graph))
            else:
                vis.write(line)
    finally:
        template.close()
        vis.close()
    

def write_to_json( graph ):
    #print(os.getcwd())
    #f = open("{}.json".format( graph.id ), 'w+')
    f = io.StringIO()
    f.write('var dataset = {')
    f.write('\n\t"nodes":[\n')
    sorted_nodes = list(graph.nodes)
    node_num = {sorted_nodes[n]:n for n in range(len(sorted_nodes))}
    consensus_labels, score_dict = find_consensus_labelling(graph)
    b_first = True
    for node in sorted_nodes:
        if not b_first:
            f.write(',\n')
        f.write('\t\t{{"atom": "{0}", "size": {1}, "score": "{0}{2}" }}'.format( consensus_labels[node], get_size_by_element(consensus_labels[node]), score_dict[node]))
        b_first = False
    f.write('\n\t],\n\t"links":[\n')
    b_first = True
    for edge in graph.edges:
        if not b_first:
            f.write(',\n')
        f.write('\t\t{{"source": {}, "target": {}, "bond": 1 }}'.format( node_num[edge.node1], node_num[edge.node2]))
        b_first = False
    f.write('\n\t]\n}')
    ret = f.getvalue()
    f.close()
    return ret
    #create flag to save json to disk
    
    
if __name__ == '__main__':
    try:
        g = parse_graph( sys.argv[1] )
        generate_html_vis(g)
    except Exception as e:
        print("Please provide a graph you want to test the graphwriter with \n \t example: python3 graph_writer.py graph1.graph")
        raise(e)
