from lark import Visitor, Tree

class Generator(Visitor):

    def __init__(self):
        self.code = []
        self.var_count = -1

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
        self.add_label(tree.label)
        self.add_command(tree.children[2].code, '', '')
        self.add_command("beq", tree.children[2].var, "goto", self.index_label(tree.label+1))
        self.add_command(tree.children[4].code, '', '')
        self.add_command("goto", self.index_label(tree.label))
        self.add_label(tree.label+1)
        self.clean(tree)

    def ifstmt(self, tree):
        self.add_command(tree.children[2].code,'','')
        self.add_command("beq",tree.children[2].var, "goto", self.index_label(tree.label))
        self.add_command(tree.children[4].code,'','')
        self.add_label(tree.label)
        if len(tree.children)>4:
            self.add_command(tree.children[6].code,'','')
        self.clean(tree)

    def add_label(self, index):
        self.add_command(self.index_label(index)+":")

    def index_label(self, index):
        return "L"+str(index)

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

    def add_command(self, *args, sep = ' ', end = '\n'):
        for i in range(len(args)):
            self.code = self.code + args[i]
            if i < len(args)-1:
                self.code = self.code + sep
            else:
                self.code = self.code + end

    def set_op(self, v1, v2, op):
        self.add_command(self.next_aux_var(),"=",v1,op,v2)

    def set_var(self, value):
        self.add_command(self.next_aux_var(),"=",value)
