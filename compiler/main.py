from compiler.parser.grammar import grammar, start
from compiler.parser.parser import Parser, SetArguments, SemanticAnalyzer
from lark import Tree
from generator import Generator, FinalGenerator


def get_classes(tree):
    classes = tree.find_pred(lambda v: isinstance(v, Tree) and v.data in ["classdecl","interfacedecl"])
    final_classes = {}
    for clas in classes:
        final_classes[clas] = clas.children[1].value
    return final_classes


def set_parents(tree):
    if tree.data == 'start':
        tree.parent = None
    for ch in tree.children:
        if isinstance(ch, Tree):
            ch.parent = tree
            set_parents(ch)

parser = Parser(grammar=grammar, start=start, parser="lalr")
tree = parser.parser.parse("int\n_v\n(\n)\n{\n_f\n(\n)\n;\n}\n")
set_parents(tree)
SetArguments().visit(tree)
SemanticAnalyzer(get_classes(tree)).visit(tree)
generator = Generator()
generator.visit(tree)
final_generator = FinalGenerator(generator.code)
final_generator.convert()
code = final_generator.final_code
