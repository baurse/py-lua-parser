"""
    ``printers`` module
    ===================

    Contains utilities to render an ast tree to text or html.
"""

from luaparser.astnodes import *
from luaparser.builder import LITERAL_NAMES
from luaparser.utils.visitor import *
from enum import Enum
import xml.etree.cElementTree as ElementTree
from xml.dom import minidom
from textwrap import indent


class Style(Enum):
    PYTHON = 1
    HTML = 2


class PythonStyleVisitor:
    def __init__(self, indent):
        self.indentValue = indent
        self.currentIndent = 0

    @visitor(str)
    def visit(self, node):
        return repr(node)

    @visitor(float)
    def visit(self, node):
        return str(node)

    @visitor(int)
    def visit(self, node):
        return str(node)

    @visitor(Enum)
    def visit(self, node):
        return str(node.name)

    def indent_str(self, newLine=True):
        res = ' ' * self.currentIndent
        if newLine:
            res = '\n' + res
        return res

    def indent(self):
        self.currentIndent += self.indentValue

    def dedent(self):
        self.currentIndent -= self.indentValue

    @staticmethod
    def pretty_count(node, is_list=False):
        res = ''
        if isinstance(node, list):
            item_count = len(node)
            res += '[] ' + str(item_count) + ' '
            if item_count > 1:
                res += 'items'
            else:
                res += 'item'
        elif isinstance(node, Node):
            if is_list:
                return '{} 1 key'
            key_count = len([attr for attr in node.__dict__.keys() if not attr.startswith("_")])
            res += '{} ' + str(key_count) + ' '
            if key_count > 1:
                res += 'keys'
            else:
                res += 'key'
        else:
            res += '[unknow]'
        return res

    @visitor(list)
    def visit(self, obj):
        res = ''
        k = 0
        for itemValue in obj:
            res += self.indent_str() + str(k) + ': ' + self.pretty_count(itemValue, True)
            self.indent()
            res += self.indent_str(False) + self.visit(itemValue)
            self.dedent()
            k += 1
        return res

    @visitor(Node)
    def visit(self, node):
        res = self.indent_str() + node.display_name + ': ' + self.pretty_count(node)

        self.indent()

        # comments
        comments = node.comments
        if comments:
            res += self.indent_str() + 'comments' + ': ' + self.pretty_count(comments)
            k = 0
            self.indent()
            for c in comments:
                res += self.indent_str() + str(k) + ': ' + self.visit(c.s)
                k += 1
            self.dedent()

        for attr, attrValue in node.__dict__.items():
            if not attr.startswith(('_', 'comments', 'trailing_comments')):
                if isinstance(attrValue, Node) or isinstance(attrValue, list):
                    res += self.indent_str() + attr + ': ' + self.pretty_count(attrValue)
                    self.indent()
                    res += self.visit(attrValue)
                    self.dedent()
                else:
                    if attrValue is not None:
                        res += self.indent_str() + attr + ': ' + self.visit(attrValue)
        
        # trailing comments, like at the end of a file, can exist if the node is a chuck
        if type(node) is Chunk:
            trailing_comments = node.trailing_comments
            if trailing_comments:
                res += self.indent_str() + 'trailing_comments' + ': ' + self.pretty_count(trailing_comments)
                k = 0
                self.indent()
                for c in trailing_comments:
                    res += self.indent_str() + str(k) + ': ' + self.visit(c.s)
                    k += 1
                self.dedent()

        self.dedent()
        return res



escape_dict = {
    '\a': r'\a',
    '\b': r'\b',
    '\c': r'\c',
    '\f': r'\f',
    '\n': r'\n',
    '\r': r'\r',
    '\t': r'\t',
    '\v': r'\v',
    '\'': r'\'',
    '\"': r'\"',
    '\0': r'\0',
    '\1': r'\1',
    '\2': r'\2',
    '\3': r'\3',
    '\4': r'\4',
    '\5': r'\5',
    '\6': r'\6',
    '\7': r'\7',
    '\8': r'\8',
    '\9': r'\9'
}

# remove all the apostrophies from the LITERAL_NAMES to make use of the names therein as normal strings
printable_literal_names = [name.replace("'", '') for name in  LITERAL_NAMES]

# this is bad code. What I want is access to the token index in the printer functions below so that I can, e.g., get the
# right string for the addition operator AddOp, i.e. '+' without having an if statement for every possible operator that
# can exist. It would make sense to add this to the node class directly, instead of clumsily getting it from the
# Note that the string name is NOT the same thing as the elements of the Tokens class that's defined in builder
display_name_to_printable_literal_name = {
    'LAndOp' : printable_literal_names[1],
    # 'BREAK' : printable_literal_names[2],
    # 'DO' : printable_literal_names[3],
    # 'ELSETOK' : printable_literal_names[4],
    # 'ELSEIF' : printable_literal_names[5],
    # 'END' : printable_literal_names[6],
    # 'FALSE' : printable_literal_names[7],
    # 'FOR' : printable_literal_names[8],
    # 'FUNCTION' : printable_literal_names[9],
    # 'GOTO' : printable_literal_names[10],
    # 'IFTOK' : printable_literal_names[11],
    # 'IN' : printable_literal_names[12],
    # 'LOCAL' : printable_literal_names[13],
    # 'NIL' : printable_literal_names[14],
    # 'NOT' : printable_literal_names[15],
    'LOrOp' : printable_literal_names[16],
    # 'REPEAT' : printable_literal_names[17],
    # 'RETURN' : printable_literal_names[18],
    # 'THEN' : printable_literal_names[19],
    # 'TRUE' : printable_literal_names[20],
    # 'UNTIL' : printable_literal_names[21],
    # 'WHILE' : printable_literal_names[22],
    # 'Continue' : printable_literal_names[23],
    'AddOp' : printable_literal_names[24],
    'SubOp' : printable_literal_names[25],
    'MultOp' : printable_literal_names[26],
    'FloatDivOp' : printable_literal_names[27],
    'FloorDivOp' : printable_literal_names[28],
    'ModOp' : printable_literal_names[29],
    'ExpoOp' : printable_literal_names[30],
    # 'LENGTH' : printable_literal_names[31],
    'REqOp' : printable_literal_names[32],
    'RNotEqOp' : printable_literal_names[33],
    'RLtEqOp' : printable_literal_names[34],
    'RGtEqOp' : printable_literal_names[35],
    'RLtOp' : printable_literal_names[36],
    'RGtOp' : printable_literal_names[37],
    # 'ASSIGN' : printable_literal_names[38],
    'BAndOp' : printable_literal_names[39],
    'BOrOp' : printable_literal_names[40],
    'BXorOp' : printable_literal_names[41],
    'BShiftROp' : printable_literal_names[42],
    'BShiftLOp' : printable_literal_names[43],
    # 'OPAR' : printable_literal_names[44],
    # 'CPAR' : printable_literal_names[45],
    # 'OBRACE' : printable_literal_names[46],
    # 'CBRACE' : printable_literal_names[47],
    # 'OBRACK' : printable_literal_names[48],
    # 'CBRACK' : printable_literal_names[49],
    # 'COLCOL' : printable_literal_names[50],
    # 'COL' : printable_literal_names[51],
    # 'COMMA' : printable_literal_names[52],
    # 'VARARGS' : printable_literal_names[53],
    'Concat' : printable_literal_names[54],
    # 'DOT' : printable_literal_names[55],
    # 'SEMCOL' : printable_literal_names[56],
    # 'NAME' : printable_literal_names[57],
    # 'NUMBER' : printable_literal_names[58],
    # 'STRING' : printable_literal_names[59],
    # 'COMMENT' : printable_literal_names[60],
    # 'LINE_COMMENT' : printable_literal_names[61],
    # 'SPACE' : printable_literal_names[62],
    # 'NEWLINE' : printable_literal_names[63],
    # 'SHEBANG' : printable_literal_names[64],
    # 'LongBracket' : printable_literal_names[65],
}

def raw(text):
    """Returns a raw string representation of text"""
    new_string = ''
    for char in text:
        try:
            new_string += escape_dict[char]
        except KeyError:
            new_string += char
    return new_string


class HTMLStyleVisitor:
    def __init__(self):
        pass

    def get_xml_string(self, tree):
        xml = self.visit(tree)

        ast = ElementTree.Element("ast")
        doc = ElementTree.SubElement(ast, "doc")
        doc.append(xml)

        return minidom.parseString(ElementTree.tostring(doc)).toprettyxml(indent="   ")

    @visitor(str)
    def visit(self, node):
        if node.startswith('"') and node.endswith('"'):
            node = node[1:-1]
        return node

    @visitor(float)
    def visit(self, node):
        return str(node)

    @visitor(int)
    def visit(self, node):
        return str(node)

    @visitor(list)
    def visit(self, obj):
        xml_nodes = []
        for itemValue in obj:
            xml_nodes.append(self.visit(itemValue))
        return xml_nodes

    @visitor(Enum)
    def visit(self, node):
        return str(node)

    @visitor(Node)
    def visit(self, node):
        xml_node = ElementTree.Element(node.display_name)

        # attributes
        for attr, attrValue in node.__dict__.items():
            if not attr.startswith('_') and attrValue is not None:
                xml_attr = ElementTree.SubElement(xml_node, attr)
                child_node = self.visit(attrValue)
                if type(child_node) is str:
                    xml_attr.text = child_node
                elif type(child_node) is list:
                    xml_attr.extend(child_node)
                else:
                    xml_attr.append(child_node)

        return xml_node


class LuaOutputVisitor:
    def __init__(self, indent_size: int):
        self._indent_size = indent_size
        self._curr_indent = -self._indent_size

    def _up(self):
        self._curr_indent += self._indent_size

    def _down(self):
        self._curr_indent -= self._indent_size

    @visitor(str)
    def visit(self, node) -> str:
        return str(node)

    @visitor(float)
    def visit(self, node) -> str:
        return str(node)

    @visitor(int)
    def visit(self, node) -> str:
        return str(node)

    @visitor(list)
    def visit(self, node: List) -> str:
        if all(isinstance(n, Comment) for n in node):
            separator = '\n'
        else:
            separator = ', '
        # str_to_join = [self.visit(n) for n in node]
        # val = separator.join(str_to_join)
        # return val
        return separator.join([self.visit(n) for n in node])

    @visitor(type(None))
    def visit(self, node) -> str:
        return ""

    @visitor(Chunk)
    def visit(self, node) -> str:
        # the filter statement does not just filter out Nones (which should never be generated) it also filters out 
        # empty strings which might be generated from visiting the comments and trailing comments
        return "\n".join(filter(None, (
            self.visit(node.comments), 
            self.visit(node.body), 
            self.visit(node.trailing_comments)
            )))

    @visitor(Block)
    def visit(self, node: Block) -> str:
        self._up()
        output = []
        if node.comments:
            output.append(self.visit(node.comments))
        for n in node.body:
            if n.comments: output.append(self.visit(n.comments))
            output.append(self.visit(n))
        if node.trailing_comments:
            output.append(self.visit(node.trailing_comments))
        output = '\n'.join(output)
        if self._curr_indent != 0:
            output = indent(output, ' ' * self._indent_size)
        self._down()
        return output

    @visitor(Assign)
    def visit(self, node: Assign) -> str:
        return self.visit(node.targets) + ' = ' + self.visit(node.values)

    @visitor(LocalAssign)
    def visit(self, node: LocalAssign) -> str:
        if node.values:
            return 'local ' + self.visit(node.targets) + ' = ' + self.visit(node.values)
        else:
            return 'local ' + self.visit(node.targets)

    @visitor(While)
    def visit(self, node: While) -> str:
        return 'while ' + self.visit(node.test) + ' do\n' + self.visit(node.body) + '\nend'

    @visitor(Do)
    def visit(self, node: Do) -> str:
        return 'do\n' + self.visit(node.body) + '\nend'

    @visitor(If)
    def visit(self, node: If) -> str:
        output = 'if ' + self.visit(node.test) + ' then\n' + self.visit(node.body) + '\n'
        if node.orelse:
            if isinstance(node.orelse, ElseIf):
                output += self.visit(node.orelse)
            else:
                output += 'else\n' + self.visit(node.orelse) +'\n'
        output += 'end'
        return output

    @visitor(ElseIf)
    def visit(self, node: ElseIf) -> str:
        output = 'elseif ' + self.visit(node.test) + ' then\n' + self.visit(node.body) + '\n'
        if node.orelse:
            if isinstance(node.orelse, ElseIf):
                output += self.visit(node.orelse)
            else:
                output += 'else\n' + self.visit(node.orelse) +'\n'
        return output

    @visitor(Label)
    def visit(self, node: Label) -> str:
        return '::' + self.visit(node.id) + '::'

    @visitor(Goto)
    def visit(self, node: Goto) -> str:
        return 'goto ' + self.visit(node.label)

    @visitor(Break)
    def visit(self, node: Break) -> str:
        return 'break'

    @visitor(Continue)
    def visit(self, node: Break) -> str:
        return 'continue'

    @visitor(Return)
    def visit(self, node: Return) -> str:
        if len(node.values) == 1 and isinstance(node.values[0], Nil):
            return 'return'
        else:
            return 'return ' + self.visit(node.values)

    @visitor(Fornum)
    def visit(self, node: Fornum) -> str:
        output = ' '.join(['for', self.visit(node.target), '=',
                           ', '.join([self.visit(node.start), self.visit(node.stop)])])
        if node.step != 1:
            output += ', ' + self.visit(node.step)
        output += ' do\n' + self.visit(node.body) + '\nend'
        return output

    @visitor(Forin)
    def visit(self, node: Forin) -> str:
        return ' '.join(['for', self.visit(node.targets), 'in',
                         self.visit(node.iter),
                         'do']) + '\n' + self.visit(node.body) + '\nend'

    @visitor(Call)
    def visit(self, node: Call) -> str:
        return self.visit(node.func) + '(' + self.visit(node.args) + ')'

    @visitor(Invoke)
    def visit(self, node: Invoke) -> str:
        return self.visit(node.source) + ':' + self.visit(node.func) + '(' + self.visit(node.args) + ')'

    @visitor(Function)
    def visit(self, node: Function) -> str:
        output = 'function ' + self.visit(node.name) + '(' + self.visit(node.args) + ')'
        body_visit_out = self.visit(node.body)
        if body_visit_out != '': 
            output += '\n' + body_visit_out + '\n' + 'end'
        else: 
            output += ' end'
        return output

    @visitor(LocalFunction)
    def visit(self, node) -> str:
        output = 'local function ' + self.visit(node.name) + '(' + self.visit(node.args) + ')'
        body_visit_out = self.visit(node.body)
        if body_visit_out != '': 
            output += '\n' + body_visit_out + '\n' + 'end'
        else: 
            output += ' end'
        return output
    
    @visitor(AnonymousFunction)
    def visit(self, node: AnonymousFunction) -> str:
        output = 'function' + '(' + self.visit(node.args) + ')'
        body_visit_out = self.visit(node.body)
        if body_visit_out != '': 
            output += '\n' + body_visit_out + '\n' + 'end'
        else: 
            output += ' end'
        return output

    @visitor(Method)
    def visit(self, node: Method) -> str:
        return 'function ' + self.visit(node.source) + ':' + self.visit(node.name) + '(' + self.visit(
            node.args) + ')\n' + self.visit(node.body) + '\nend'

    @visitor(Nil)
    def visit(self, node) -> str:
        return 'nil'

    @visitor(TrueExpr)
    def visit(self, node) -> str:
        return 'true'

    @visitor(FalseExpr)
    def visit(self, node) -> str:
        return 'false'

    @visitor(Number)
    def visit(self, node) -> str:
        return self.visit(node.n)

    @visitor(String)
    def visit(self, node: String) -> str:
        if node.delimiter == StringDelimiter.SINGLE_QUOTE:
            return "'" + self.visit(node.s) + "'"
        elif node.delimiter == StringDelimiter.DOUBLE_QUOTE:
            return '"' + self.visit(node.s) + '"'
        else:
            return '[[' + self.visit(node.s) + ']]'

    @visitor(Table)
    def visit(self, node: Table):
        if node.fields or node.trailing_comments:
            output = '{\n'
            for field in node.fields:
                if field.comments: output += indent(self.visit(field.comments) + '\n', ' ' * self._indent_size)
                output += indent(self.visit(field) + ',\n', ' ' * self._indent_size)
            if node.trailing_comments:
                 output += indent(self.visit(node.trailing_comments) + '\n', ' ' * self._indent_size)
            output += '}'
        else:
            output = '{}'
        return output

    @visitor(Field)
    def visit(self, node: Field):
        key = self.visit(node.key)
        output = ''
        # If the field is treated like an array entry we don't need to print the key as it's redundant.
        if not all([char.isdigit() for char in key]) or node.between_brackets:
            output = '[' if node.between_brackets else ''
            output += key
            output += ']' if node.between_brackets else ''
            output += ' = '
        output += self.visit(node.value)
        return output

    @visitor(Dots)
    def visit(self, node) -> str:
        return '...'

    @visitor(BinaryOp)
    def visit(self, node: BinaryOp) -> str:
        if node.between_parenthesis:
            left_bracket = '('
            right_bracket = ')'
        else:
            left_bracket = ''
            right_bracket = ''     
        operator = display_name_to_printable_literal_name[node.display_name]
        
        output = left_bracket
        output += self.visit(node.left) + ' ' + operator + ' ' + self.visit(node.right)
        output += right_bracket
        return output
    
    @visitor(UMinusOp)
    def visit(self, node) -> str:
        return '-' + self.visit(node.operand)

    @visitor(UBNotOp)
    def visit(self, node) -> str:
        return '~' + self.visit(node.operand)

    @visitor(ULNotOp)
    def visit(self, node) -> str:
        return 'not ' + self.visit(node.operand)

    @visitor(Name)
    def visit(self, node: Name) -> str:
        return self.visit(node.id)

    @visitor(Index)
    def visit(self, node: Index) -> str:
        if node.notation == IndexNotation.DOT:
            return self.visit(node.value) + '.' + self.visit(node.idx)
        else:
            return self.visit(node.value) + '[' + self.visit(node.idx) + ']'

    @visitor(Varargs)
    def visit(self, node) -> str:
        return '...'

    @visitor(Repeat)
    def visit(self, node: Repeat) -> str:
        return 'repeat\n' + self.visit(node.body) + '\nuntil ' + self.visit(node.test)

    @visitor(SemiColon)
    def visit(self, node) -> str:
        return ';'

    @visitor(Comment)
    def visit(self, node: Comment) -> str:
        return node.s
