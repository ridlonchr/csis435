import pycparser # the C parser written in Python
import sys # so we can access command-line args
import pprint # so we can pretty-print our output

class SymbolTableBuilder(pycparser.c_ast.NodeVisitor):
    """
        This subclass of NodeVisitor builds the symbol table.
        Still a work-in-progress.
    """
    def __init__(self):
        """
            We use two main instance variables, values and path.
            Values is used to serve as a dict of the symbol names,
                with the values either being the nodes that those symbols correspond to,
                or a dict representing a subscope
            the path is used to indicate the current scope that we're working with.
            
            about_to_see_scope_name is used when we encounter something, like a function declaration,
            that indicates that the next declaration will be the name of a new scope
        """
        self.values = {}
        self.path = []
        self.about_to_see_scope_name = False
        
        self.types = {}
        
        self.visiting_arguments = False
        
    def __getitem__(self,name):
    	"""
    		we override [] so that we can access whatever symbols are at the current scope
    	"""
        current_node = self.values
        for elem in self.path:
            current_node = current_node[elem]
        return current_node[name]
    def current_node(self):
    	"""
    	"""
        current_node = self.values
        for elem in self.path:
            current_node = current_node[elem]
        return current_node
    def __setitem__(self,name,value):
    	"""
    		we override [] so that we can access/set whatever symbols are at the current scope
    	"""
        current_node = self.values
        for elem in self.path:
            current_node = current_node[elem]
        current_node[name] = value
    def visit_Decl(self,node):
    	"""
    		this gets called, as part of the visitor design pattern,
    			whenever a Decl is encountered in the parse tree
    		Here we want to handle it accordingly in order to ensure that we either put it in the table,
    			or create a new scope with this being the name of that
    	'"""
        if self.about_to_see_scope_name:
            self[node.name] = {}
            self.path.append(node.name)
            self.about_to_see_scope_name = False
            self["..."] = []
            self.path.append("...")
            self.visiting_arguments = True
            self.generic_visit(node)
            d = dict(node.children()[0][1].children())
            return_type = d["type"]
            self.visiting_arguments = False
            del self.path[-1]
            #return_type.children()
            self["return"] = return_type
        elif self.visiting_arguments:
        	self.current_node().append((node.name,node))
        else:
            self[node.name] = node
    def visit_FuncDef(self,node):
    	"""
    		this gets called, as part of the visitor design pattern,
    			whenever a FuncDef is encountered in the parse tree
    		Here we want to have it signal that we're going to be starting a new scope with the next Decl
    	"""
        self.about_to_see_scope_name = True
        self.generic_visit(node)
        del self.path[-1]
        
    def visit_Typedef(self,node):
    	self.types[node.name] = node
    	self.generic_visit(node)

if __name__ == "__main__":
    if len(sys.argv) > 1:    # optionally support passing in some code as a command-line argument
        code_to_parse = sys.argv[1]
    else: # this can not handle the typedef and struct below correctly. Need to work on it.
        code_to_parse = """
typedef struct foobar {
	int f;
	int b;
	struct foobar * fb;
} foobar;
int q[100];
foobar w[100];
int z;
int foo(int a, int b) {
    int x;
    int y;
    return (x+y);
};
int bar(int c, int d) {
	int y;
	int z;
};
test() {};

"""

    cparser = pycparser.c_parser.CParser()
    parsed_code = cparser.parse(code_to_parse)
    parsed_code.show()
    dv = SymbolTableBuilder()
    dv.visit(parsed_code)
    pprint.pprint(dv.values)
    pprint.pprint(dv.types)
