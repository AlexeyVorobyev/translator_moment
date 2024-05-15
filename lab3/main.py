import ast
import re
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
        args = ",".join([arg.arg for arg in node.args.args])
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
        return " [ " + elts + " ] "
    elif isinstance(node, ast.Dict):
        keys = [convert_to_rpn(key) for key in node.keys]
        values = [convert_to_rpn(value) for value in node.values]
        key_value_pairs = [k + ": " + v for k, v in zip(keys, values)]
        pairs_str = ", ".join(key_value_pairs)
        return " { " + pairs_str + " } "
    elif isinstance(node, ast.Attribute):
        value = convert_to_rpn(node.value)
        attr = node.attr
        return value + attr + " "
    elif isinstance(node, ast.Num):
        return str(node.n) + " "
    elif isinstance(node, ast.Call):
        args = [convert_to_rpn(arg) for arg in node.args]
        return node.func.id + " " + "".join(args) + str(len(node.args)) + "Ф "
    elif isinstance(node, ast.Expr):
        return convert_to_rpn(node.value)
    elif isinstance(node, ast.If):
        test = convert_to_rpn(node.test)
        body = " ".join([convert_to_rpn(n) for n in node.body])
        if len(node.orelse) == 0:
            return test + "M1_УПЛ " + body + "М1 "
        orelse = " ".join([convert_to_rpn(n) for n in node.orelse])
        return test + "M1_УПЛ " + body + "М2_БП_М1 " + orelse + "М2 "
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
        return test + "M1_УПЛ " + body + "М2_БП_М1 " + orelse + "М2 "
    else:
        print(node)
        return ""


def python_to_rpn(source_code):
    tree = ast.parse(source_code)
    rpn_expression = ""
    for node in tree.body:
        rpn_expression += convert_to_rpn(node)

    return rpn_expression.strip().replace('  ', ' ')


def rpn_to_java(source_code):
    result = ""

    word_buffer: list[str] = source_code.replace('\n', '').split(" ")

    currentTabulation = 8

    try:
        while (word_buffer.index('[')):
            start = word_buffer.index('[')
            end = word_buffer.index(']')
            arr = word_buffer[start + 1:end]
            print(arr)
            res = """new ArrayList<Unknown<?>>(){{
            $1
            }}""".replace(
                '$1',
                str.join("\n" + " " * (currentTabulation + 4),
                         ["add(Unknown($1));".replace("$1", item.replace(',', '')) for item in arr])
            )
            word_buffer = word_buffer[0:start] + [res] + word_buffer[end + 1: len(word_buffer)]
    except:
        pass

    unaryOperators = ['return', 'not', 'is']

    print(word_buffer)

    stack = []

    userFuncStack = []

    pythonFuncs = {
        'print': 'System.out.println'
    }

    for word in word_buffer:
        print(stack)

        if word == '=':
            tmp = (" " * currentTabulation + "$3 $1 = $2;\n"
                   .replace('$2', stack.pop())
                   .replace('$1', stack.pop())
                   )

            if tmp.find("new ArrayList<Unknown<?>>") != -1:
                tmp = tmp.replace('$3', "ArrayList<Unknown<?>>")
            else:
                tmp = tmp.replace('$3', "Unknown<?>")

            result += tmp
        elif word in ["+", "-", "/", "*", "**", "==", "!=", ">=", "<=", "<", ">"]:
            stack.append(("$1 $3 $2"
                          .replace('$2', stack.pop())
                          .replace('$1', stack.pop())
                          .replace('$3', word)
                          ))
        elif word == "M1_УПЛ":
            result += (" " * currentTabulation + "if ($1) {\n"
                       .replace('$1', stack.pop())
                       )
            currentTabulation += 4
        elif re.search("^[0-9]+Ф$", word):
            tmp = "("
            amount = int(re.compile("[0-9]+").search(word).group(0))

            print(stack,amount)

            stack_reversed = []
            for i in range(0, amount):
                stack_reversed.append(stack.pop())

            for i in range(0, amount):
                tmp += "$1,".replace("$1", stack_reversed.pop())
            funcName = stack.pop()
            if funcName in userFuncStack:
                funcName += '.call'

            stack.append((funcName + tmp + ")").replace(',)', ')'))
        elif word == "М2_БП_М1":
            if (len(stack)):
                result += " " * currentTabulation + stack.pop() + ";\n"
            currentTabulation -= 4
            result += " " * currentTabulation + "}\n" + " " * currentTabulation + "else {\n"
            currentTabulation += 4
        elif word == 'АЭМ':
            stack.append(("$1[$2]"
                          .replace('$2', stack.pop())
                          .replace('$1', stack.pop())
                          ))
        elif word == "М2":
            if (len(stack)):
                result += " " * currentTabulation + stack.pop() + ";\n"
            currentTabulation -= 4
            result += " " * currentTabulation + "}\n"
        elif word == "НФ":
            func = stack.pop()
            funcName = func.split('(')[0]
            userFuncStack.append(funcName)
            funcArgs = str.join(", ", ["Unknown<?> $1".replace("$1", arg) for arg in
                                       ("(" + func.split('(')[1]).replace('(', "").split(",")])
            tmp = " " * currentTabulation + """static class $3 {
$1""".replace("$3", funcName)
            currentTabulation += 4
            tmp = tmp.replace("$1", " " * currentTabulation + "public static Unknown<?> call(" + funcArgs + "{\n")
            currentTabulation += 4
            result += tmp
        elif word == 'КФ':
            if (len(stack)):
                result += " " * currentTabulation + stack.pop() + ";\n"
            currentTabulation -= 4
            result += " " * currentTabulation + "}\n"
            currentTabulation -= 4
            result += " " * currentTabulation + "}mark\n"
        elif word in unaryOperators:
            result += (" " * currentTabulation + "$1 $2;\n"
                       .replace('$2', stack.pop())
                       .replace('$1', word)
                       )
        else:
            stack.append(word)

    if (len(stack)):
        result += " " * currentTabulation + stack.pop() + ";"


    for funcKey in pythonFuncs.keys():
        result = result.replace(funcKey, pythonFuncs.get(funcKey))

    print(stack)
    funcie = None

    if (re.search('static class[\s\S]*}mark', result)):
        funcie = re.search('static class[\s\S]*}mark', result).group(0).replace('mark', ';\n')

        funcieToRepl = re.search('static class[\s\S]*}mark', result).group(0).split('};')

    x= """
    import java.util.ArrayList;
    
    $2
public class Program {
    class Unknown<T> {
        private T ref;

        public Unknown(T ref) {
            this.ref = ref;
        }
        
        public T get() {
            return ref;
        }
        
        public void set(T a) {
            this.ref = a;
        }
    };
    
    public static void main(String []args)
    {
$1
    }
}""".replace("$1", result)

    if (funcie):
        x = x.replace("$2", funcie)
        for a in funcieToRepl:
            x = x.replace(a, '')
    else:
        x = x.replace("$2", "")

    return x


def prog():
    f = open('./resources/python.txt', 'r')
    input_sequence = f.read()
    f.close()

    out_seq = python_to_rpn(input_sequence)

    # файл, содержащий обратную польскую запись
    f = open('gen/rpn.txt', 'w')
    f.write(out_seq)
    f.close()


def prog2():
    f = open('./gen/rpn.txt', 'r')
    input_sequence = f.read()
    f.close()

    out_seq = rpn_to_java(input_sequence)

    # файл, содержащий обратную польскую запись
    f = open('gen/res.txt', 'w')
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


def clicked2():
    write_txt(opzstext.get("1.0", "end"), 'gen/rpn.txt')

    restext.delete("1.0", END)

    prog2()

    f1 = open('gen/res.txt', 'r')
    text = f1.read()
    restext.insert("1.0", text)
    f1.close()


window = Tk()
window.title("LR3")

f1 = open('resources/python.txt', 'r')
text = f1.read()

f2 = open('gen/rpn.txt', 'r')
text2 = f2.read()

f3 = open('gen/res.txt', 'r')
text3 = f3.read()

window.geometry('1840x640')

codetxt = st.ScrolledText(window, font=("Arial", 18))
codetxt.insert("1.0", text)
codetxt.place(x=20, y=20, width=400, height=600)

opzstext = st.ScrolledText(window, font=("Arial", 18))
opzstext.place(x=720, y=20, width=400, height=600)
opzstext.insert("1.0", text2)

restext = st.ScrolledText(window, font=("Arial", 18))
restext.place(x=1420, y=20, width=400, height=600)
restext.insert("1.0", text3)

btngo = Button(window, text="Выполнить \n преобразование", command=clicked, font=("Arial", 20))
btngo.place(x=510 + 150 - 100 - 90, y=10 + 300 - 40, width=200, height=80)

btngo2 = Button(window, text="Выполнить \n преобразование", command=clicked2, font=("Arial", 20))
btngo2.place(x=510 + 350 - 100 - 90 + 500, y=10 + 300 - 40, width=200, height=80)

window.mainloop()
