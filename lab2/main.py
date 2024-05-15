import ast
from _ast import Module, AST
from tkinter import *
import tkinter.scrolledtext as st

binaryOperationNameToSymbol = {
    'Mult': '*',
    'Add': '+',
    'Sub': '-',
    'Div': '/',
    'FloorDiv': '//',
    'Mod': '%',
    'Pow': '**',
}

compareEqNameToSymbol = {
    'Lt': '<',
    'LtE': '<=',
    'Gt': '>',
    'GtE': '>=',
    'Eq': '==',
    'NotEq': '!=',
}

compareBoolNameToSymbol = {
    'And': 'and',
    'Or': 'or',
}

compareUnaryNameToSymbol = {
    'Not': 'not',
}

compareAugAssignNameToSymbol = {
    'Add': '+=',
    'Sub': '-=',
    'Mult': '*=',
    'Div': '/=',
    'MatMult': '**='
}



def calcTreeNodes(node: AST | Module, result=0) -> int:
    if isinstance(node, list):
        return result + sum([calcTreeNodes(node, 0) for node in node])
    elif hasattr(node, 'left'):
        return result + calcTreeNodes(node.left, 0) + calcTreeNodes(node.right, 0)
    elif hasattr(node, 'values'):
        return result + sum([calcTreeNodes(node, 0) for node in node.values])
    else:
        return result + 1


def convert_to_rpn(node):
    if isinstance(node, ast.BinOp):
        left = convert_to_rpn(node.left)
        right = convert_to_rpn(node.right)
        return left + right + binaryOperationNameToSymbol.get(node.op.__class__.__name__) + " "
    elif isinstance(node, ast.Num):
        return str(node.n) + " "
    elif isinstance(node, ast.Expr):
        return convert_to_rpn(node.value)
    elif isinstance(node, ast.FunctionDef):
        args = ", ".join([arg.arg for arg in node.args.args])
        body = " ".join([convert_to_rpn(n) for n in node.body])
        return node.name + "(" + args + ") " + "НФ " + body + "КФ "
    elif isinstance(node, ast.Assign):
        target = convert_to_rpn(node.targets[0])
        value = convert_to_rpn(node.value)
        return target + value + "= "
    elif isinstance(node, ast.Compare):
        left = convert_to_rpn(node.left)
        ops = " ".join([compareEqNameToSymbol.get(op.__class__.__name__) for op in node.ops])
        comparators = " ".join([convert_to_rpn(comp) for comp in node.comparators])
        return left + comparators + ops + " "
    elif isinstance(node, ast.Return):
        value = convert_to_rpn(node.value)
        return value + "return "
    elif isinstance(node, ast.Yield):
        value = convert_to_rpn(node.value)
        return value + "yield "
    elif isinstance(node, ast.AugAssign):
        target = convert_to_rpn(node.target)
        value = convert_to_rpn(node.value)
        return target + value + compareAugAssignNameToSymbol.get(node.op.__class__.__name__) + " "
    elif isinstance(node, ast.For):
        target = convert_to_rpn(node.target)
        print(node.target)
        iter = convert_to_rpn(node.iter)
        body = " ".join([convert_to_rpn(n) for n in node.body])
        return target + iter + "in " + "НИЦ " + body + "КИЦ "
    elif isinstance(node, ast.While):
        test = convert_to_rpn(node.test)
        body = " ".join([convert_to_rpn(n) for n in node.body])
        return test + "НУЦ " + body + "КУЦ "
    elif isinstance(node, ast.List):
        elts = ", ".join([convert_to_rpn(elt).strip() for elt in node.elts])
        return "[" + elts + "] "
    elif isinstance(node, ast.Dict):
        keys = [convert_to_rpn(key) for key in node.keys]
        values = [convert_to_rpn(value) for value in node.values]
        key_value_pairs = [k + ": " + v for k, v in zip(keys, values)]
        pairs_str = ", ".join(key_value_pairs)
        return "{ " + pairs_str + "} "
    elif isinstance(node, ast.Attribute):
        value = convert_to_rpn(node.value)
        attr = node.attr
        return value + attr + " "
    elif isinstance(node, ast.Num):
        return str(node.n) + " "
    elif isinstance(node, ast.Call):
        args = [convert_to_rpn(arg) for arg in node.args]
        return node.func.id + " " + "".join(args) + str(calcTreeNodes(node.args)) + "Ф "
    elif isinstance(node, ast.Expr):
        return convert_to_rpn(node.value)
    elif isinstance(node, ast.If):
        test = convert_to_rpn(node.test)
        body = " ".join([convert_to_rpn(n) for n in node.body])
        if len(node.orelse) == 0:
            return test + "M1 УПЛ " + body + "М1 "
        orelse = " ".join([convert_to_rpn(n) for n in node.orelse])
        return test + "M1 УПЛ " + body + "М2 БП М1 " + orelse + "М2 "
    elif isinstance(node, ast.Subscript):
        value = convert_to_rpn(node.value)
        slice_value = convert_to_rpn(node.slice)
        return value + slice_value + "АЭМ "
    elif isinstance(node, ast.Slice):
        lower = convert_to_rpn(node.lower) if node.lower is not None else ""
        upper = convert_to_rpn(node.upper) if node.upper is not None else ""
        step = convert_to_rpn(node.step) if node.step is not None else ""
        return lower + upper + step + "SLICE "
    elif isinstance(node, ast.UnaryOp):
        operand = convert_to_rpn(node.operand)
        return operand + compareUnaryNameToSymbol.get(node.op.__class__.__name__) + " "
    elif isinstance(node, ast.Name):
        return node.id + " "
    elif isinstance(node, ast.BoolOp):
        if len(node.values) == 2:
            left = convert_to_rpn(node.values[0])
            right = convert_to_rpn(node.values[1])
            return left + right + compareBoolNameToSymbol.get(node.op.__class__.__name__) + " "
        else:
            print(node.op, node.values)
    elif isinstance(node, ast.Constant):
        return node.value + " "
    elif isinstance(node, ast.IfExp):
        test = convert_to_rpn(node.test)
        body = convert_to_rpn(node.body)
        orelse = convert_to_rpn(node.orelse)
        return test + "M1 УПЛ " + body + "М2 БП М1 " + orelse + "М2 "
    else:
        print(node)
        return ""


def python_to_rpn(source_code):
    tree = ast.parse(source_code)
    rpn_expression = ""
    for node in tree.body:
        rpn_expression += convert_to_rpn(node)

    return rpn_expression.strip().replace('  ', ' ')


def prog():
    f = open('./resources/python.txt', 'r')
    input_sequence = f.read()
    f.close()

    out_seq = python_to_rpn(input_sequence)

    # файл, содержащий обратную польскую запись
    f = open('gen/rpn.txt', 'w')
    f.write(out_seq)
    f.close()


def write_txt(data, to):
    with open(to, 'w') as file:
        file.write(data)


def clicked():
    write_txt(codetxt.get("1.0", "end"), 'resources/python.txt')

    opzstext.delete("1.0", END)

    prog()

    f1 = open('gen/rpn.txt', 'r')
    text = f1.read()
    opzstext.insert("1.0", text)
    f1.close()


window = Tk()
window.title("LR2")

f1 = open('resources/python.txt', 'r')
text = f1.read()

window.geometry('1340x640')

codetxt = st.ScrolledText(window, font=("Arial", 18))
codetxt.insert("1.0", text)
codetxt.place(x=20, y=20, width=500, height=600)

opzstext = st.ScrolledText(window, font=("Arial", 18))
opzstext.place(x=820, y=20, width=500, height=600)

btngo = Button(window, text="Выполнить \n преобразование", command=clicked, font=("Arial", 20))
btngo.place(x=510 + 150 - 100, y=10 + 300 - 40, width=200, height=80)

window.mainloop()
