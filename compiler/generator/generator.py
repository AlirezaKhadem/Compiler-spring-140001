from lark import Visitor, Tree

class Generator(Visitor):

    def __init__(self):
        self.code = []
        self.var_count = -1
        self.label_count = 0

    def operation(self, v1, v2, op):
        if op not in ["MORQ", "LESQ", "EQUALS"]:
            self.set_op(v1, v2, op)
        else:
            self.set_op(v1, v2, "LESS")
            self.set_op(v1, v2, "MORE")
            self.set_op(self.aux_var(), self.aux_var(-1), "NOR")
            if op == "LESQ":
                self.set_op(self.aux_var(-2), self.aux_var(), "OR")
            elif op == "MORQ":
                self.set_op(self.aux_var(-1), self.aux_var(), "OR")

    def clean(self, tree):
        for ch in tree.children:
            if isinstance(ch, Tree):
                ch.code = None
        tree.code = self.code
        self.code = []

    def whilestmt(self, tree):
        self.add_label()
        self.add_command(tree.children[1].code,"beq",tree.children[1].var,"goto",self.offset_label(1))
        self.add_command(tree.children[4].code)
        self.add_command("goto",self.offset_label())
        self.add_label()
        self.clean(tree)

    def add_label(self):
        self.label_count += 1
        self.add_command(self.offset_label()+":")

    def offset_label(self, offset = 0):
        return "L"+str(self.label_count + offset)

    def expr(self, tree):
        if tree.children[0].data == 'constant':
            self.set_var(tree.children[0].children[0].value)
        elif tree.children[0].data == 'expr':
            self.operation(tree.children[0].var, tree.children[2].var, tree.children[1].type)
        tree.var = self.aux_var()
        self.clean(tree)

    def aux_var(self, offset = 0):
        return "t" + str(self.var_count + offset)

    def next_aux_var(self):
        self.var_count += 1
        return "t" + str(self.var_count)

    def add_command(self, *args):
        for arg in args:
            self.code = self.code + arg + ' '
        self.code[-1] = '\n'

    def set_op(self, v1, v2, op):
        self.add_command(self.next_aux_var(),"=",v1,op,v2)

    def set_var(self, value):
        self.add_command(self.next_aux_var(),"=",value)
