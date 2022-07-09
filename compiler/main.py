from compiler.parser.grammar import grammar, start
from compiler.parser.parser import Parser, SetArguments, SemanticAnalyzer
from lark import Tree


def get_classes(tree):
    classes = tree.find_pred(lambda v: isinstance(v, Tree) and v.data in ["classdecl","interfacedecl"])
    final_classes = {}
    for clas in classes:
        parents = []
        for i in range(clas.children):
            if not isinstance(clas.children[i], Tree) and clas.children[i].type == 'EXTENDS':
                parents.append(clas.children[i+1].value)
            elif isinstance(clas.children[i], Tree) and clas.data == 'implements':
                idents = tree.find_pred(lambda v: v.type == 'IDENT')
                for v in idents:
                    parents.append(v.value)
        final_classes[clas.children[1]] = (clas, parents)
    return final_classes


def set_parents(tree):
    if tree.data == 'start':
        tree.parent = None
    for ch in tree.children:
        if isinstance(ch, Tree):
            ch.parent = tree
            set_parents(ch)

parser = Parser(grammar=grammar, start=start, parser="lalr")
tree = parser.parser.parse("class\n_A\nextends\n_B\n{\n}\nclass\n_B\n{\n}\n")
set_parents(tree)
SetArguments.visit_topdown(tree)