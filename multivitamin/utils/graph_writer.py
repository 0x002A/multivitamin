import sys
import os
import getpass #to get username for AUTHOR line

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


def write_to_json( graph ):
    
#     import mmap
# 
#     with open('example.txt', 'rb', 0) as file, \
#         mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
#         if s.find(b'blabla') != -1:
#             print('true')
    
    f = open("{}{}{}.shorter.graph".format( os.getcwd(), path, graph.id ), 'w+')
    
    f.write('var dataset = {')
    f.write('/t"nodes":[')
    for node in graph.nodes:
        f.write('{"atom": "{}", "size": {}},'.format( node.label, get_size_by_element ))
    # f.write("// {}\n".format( graph.newick ))
    # f.write("AUTHOR: {}\n".format( getpass.getuser() ))
    # f.write("#nodes;{}\n".format( len(graph.nodes) ))
    # f.write("#edges;{}\n".format( len(graph.edges) ))
    # f.write("Nodes labelled;{}\n".format( graph.nodes_are_labelled) )
    # f.write("Edges labelled;{}\n".format(graph.edges_are_labelled) )
    # f.write("Directed graph;{}\n".format( graph.is_directed ))

    # f.write("\n")

    # i = 1
    # for node in (graph.nodes):
    #     node.id = i
    #     if node.label == []:
    #         f.write("{}\n".format( node.id ))
    #     else:
    #         f.write("{};".format( node.id ))
    #         label_string = ""
    #         for el in node.label:
    #             label_string += el
    #             label_string += labelsep
    #         label_string = label_string[:-1]
    #         f.write("{}\n".format( label_string ))
    #     i += 1

    # f.write("\n")

    # if not graph.edges_are_labelled:
    #     for edge in graph.edges:
    #         f.write("{};{}\n".format( edge.node1.id, edge.node2.id ))
    # else:
    #     for edge in graph.edges:
    #         f.write("{};{};{}\n".format( edge.node1.id, edge.node2.id, edge.label ))

    # f.close()




if __name__ == '__main__':
    try:
        g = parse_graph( sys.argv[1] )
        write_graph(g, "./", None)
    except Exception as e:
        print(e)
        print("Please provide a graph you want to test the graphwriter with \n \t example: python3 graph_writer.py graph1.graph")