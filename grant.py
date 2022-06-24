#!/bin/python
import argparse
import string
from jsbeautifier import beautify
from random import choice, randint
from re import findall

class JSFuzzer:

    def parse_file(self, file):
        parsed_funcs_segment = dict()
        type_of_var = None
        funcs = None
        var_names = list()
        bt_answer = ""
        var_types = {"Array":"new Array(10000)", "String":"''", "Object":"{}", "Boolean":["true", "false"]}
        with open(file, "r") as f:
            statement = f.readline()
            while True:
                    if "!!function_segment_end!!" in statement:
                        break
                    type_of_var, funcs = (self.parse_function_segment(statement))
                    parsed_funcs_segment[type_of_var] = funcs
                    if "InitV" in statement:
                        var_names.append(self.parse_init_v_vars(parsed_funcs_segment, var_types))
                    statement = f.readline()
            for statement in f.readlines():
                if "!!statement_segment_end!!" in statement:
                    break
                name = var_names[randint(0, len(var_names) - 1 )]
                bt_answer += self.do_parse(statement, list(name), parsed_funcs_segment)
        print(beautify(bt_answer))

    def parse_init_v_vars(self, parsed_funcs_segment, var_types):
        var_names = dict()
        y = 0
        for i in range(1, int(parsed_funcs_segment["InitV"][0]) + 1):
            if y == 4:
                y = 0
            else:
                y += 1
            name = f"var{i}"
            value = parsed_funcs_segment["InitV"][1].split(";")[y].strip()
            if isinstance(var_types[value], list):
                var_value = choice(var_types[value])
            else:
                var_value = var_types[value]
            var_names[name] = var_value
            print(f"var {name} = {var_value};")
        return var_names

    def parse_for_loop(self, statement):
        loop = statement.split(",")
        return self.do_for_loop(loop[1], loop[2], loop[3])

    def replace_random(self, statement, rand, value):
        for _ in range(statement.count(rand)):
            statement = statement.replace(rand, choice(value), 1)
        return statement

    def parse_function_segment(self, statement):
        type_of_var = statement[statement.find(":") + 1:statement.rfind(":")]
        funcs = statement.split("=")[1].strip(" ").split(",")
        return (type_of_var, funcs)
    
    def return_variable_right_type(self, type_var, parsed_funcs_segment):
        return  choice(list(parsed_funcs_segment[type_var]))

    def switch_arguments(self, right_var):
        if "object" in right_var:
            right_var = self.replace_random(right_var, "object", self.return_mutated_objects())
        if "condition" in right_var:
            for _ in range(right_var.count("condition")):
                right_var = right_var.replace("condition", self.return_condition())
        if "primitiveee" in right_var:
            right_var = self.replace_random(right_var, "primitiveee", self.return_random_primitive_value())
        if "propertyy" in right_var:
            for _ in range(right_var.count("propertyy")):
                right_var = right_var.replace("propertyy", "{ '': " + f"{choice(self.return_random_primitive_value())}" + "}")
        if "string" in right_var:
            for _ in range(right_var.count("string")):
                right_var = right_var.replace("string",  "'" + "".join(choice(string.ascii_letters) for _ in range(20)) + "'", 1)
        if "regexp" in right_var:
            for _ in range(right_var.count("regexp")):
                right_var = right_var.replace("regexp", '".\+"')
        if "concatenator" in right_var:
            right_var = self.replace_random(right_var, "concatenator", self.return_mutated_arrays())
        if "inddx" in right_var:
            for _ in range(right_var.count("inddx")):
                right_var = right_var.replace("inddx", f"{randint(1, 20)}")
        right_var = right_var.replace(";", ",")
        return right_var

    def do_parse(self, statement, name, parsed_funcs_segment):
        if "!!" in statement:
            return ""
        if "@variable@" in statement:
            statement = statement.replace("@variable@", choice(name))
        if "@variable2@"in statement:
            statement = statement.replace("@variable2@", choice(name))
        if "function@" in statement:
            type_function = statement.split("=")[1].strip()
            type_function = type_function[type_function.find("@") + 1: type_function.rfind(".")]
            right_var = self.return_variable_right_type(type_function, parsed_funcs_segment)
            right_var = self.switch_arguments(right_var)
            statement = "try{ " + statement.replace("function@", right_var) + "}\ncatch(e){}"
        if "ARITH" in statement:
            statement = self.replace_random(statement, "ARITH", self.return_random_arith())
        return statement.replace("@", "")

    def do_for_loop(self, var_name, loop_count, loop_incr_decre):
        return f"for(let {var_name}; {loop_count}; {loop_incr_decre})" + "{"

    def return_random_primitive_value(self):
        return ["null", "undefined", "true", "false", "1", "''"]

    def return_random_op(self):
        return ["===", "==", ">=", "<=", "!=", "!==", "<", ">", "&&", "||"]
    
    def return_mutated_arrays(self):
        return  [f"new Array({randint(10000,20000)})", f"Array.of({choice(self.return_random_primitive_value())})", " new Int8Array(8)", "new Uint8Array(8)", "new Int16Array(16)", "new Uint16Array(16)", "new Int32Array(32)", "new Uint32Array(32)", "new Float32Array(32)", "new Float64Array(32)", "new BigInt64Array(32)", "new BigUint64Array(1)"]

    def return_mutated_objects(self):
        return ["Function", "Number", "AggregateError", "Atomics", " Boolean", " DataView", " Date", "WebAssembly", " Set"]

    def return_condition(self):
        return choice(self.return_random_primitive_value()) + choice(self.return_random_op()) + choice(self.return_random_primitive_value())

    def return_random_arith(self):
        return ["+", "-", "*", "/"]
    
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, type=str)
    args = parser.parse_args()
    jsfuzzer = JSFuzzer()
    jsfuzzer.parse_file(args.file)

if __name__ == "__main__":
    main()
