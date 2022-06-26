#!/bin/python
import argparse
import string
from jsbeautifier import beautify
from random import choice, randint

class JSFuzzer:

    def parse_file(self, file, cycles):
        parsed_funcs_segment = dict()
        type_of_var = None
        funcs = None
        bt_answer = ""
        var_name_value = dict()
        with open(file, "r") as f:
            statement = f.readline()
            while True:
                    if "!!function_segment_end!!" in statement:
                        break
                    type_of_var, funcs = (self.parse_function_segment(statement))
                    parsed_funcs_segment[type_of_var] = funcs
                    if "InitV" in statement:
                        names = (self.parse_init_v_vars(parsed_funcs_segment))
                    statement = f.readline()
            for statement in f.readlines():
                for cycle in range(cycles):
                    if "ONLY" in statement and cycle != 0:
                        continue
                    new_statement = statement.replace("ONLY,", "")
                    bt_answer += self.do_parse(new_statement, names, parsed_funcs_segment, var_name_value)
        print(beautify(bt_answer))

    def parse_init_v_vars(self, parsed_funcs_segment):
        names = list()
        for i in range(int(parsed_funcs_segment["InitV"][0]) + 1):
            name = f"var{i}"
            print(f"var {name};")
            names.append(name)
        return names

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

    def switch_arguments(self, right_var, var_name_value):
        to_replace = [[],[],[]]
        for var_name in var_name_value:
                if "Object" == var_name_value[var_name]:
                    to_replace[0].append(var_name)
                elif "Array" == var_name_value[var_name]:
                    to_replace[1].append(var_name)
                elif "String" == var_name_value[var_name]:
                    to_replace[2].append(var_name)
        if "object" in right_var:
            for _ in range(right_var.count("object")):
                if len(to_replace[0]) > 0:
                    replac = choice(to_replace[0])
                else:
                    replac = choice(self.return_mutated_objects())
                right_var = right_var.replace("object", replac)
        if "Array" in right_var:
            for _ in range(right_var.count("Array")):
                if len(to_replace[1]) > 0:
                    replac = choice(to_replace[1])
                else:
                    replac = self.return_mutated_arrays()
                right_var = right_var.replace("Array", replac)
        if "list" in right_var:
            for _ in range(right_var.count("list")):
                if len(to_replace[2]) > 0:
                    replac = choice(to_replace[2])
                else:
                    replac = "['" + "".join(choice(string.ascii_letters) for _ in range(20)) + "'" + f"{self.return_random_primitive_value()}]"
                right_var = right_var.replace("list",  replac, 1)
        if "objkey" in right_var:
            for _ in range(right_var.count("objkey")):
                if len(to_replace[0]) > 0 and len(to_replace[1]) > 0 and len(to_replace[2]) > 0:
                    replac = choice(to_replace[0] + to_replace[1] + to_replace[2])
                else:
                    replac = "'" + "".join(choice(string.ascii_letters) for _ in range(20)) + "'"
                right_var = right_var.replace("objkey",  replac, 1)
        if "condition" in right_var:
            for _ in range(right_var.count("condition")):
                right_var = right_var.replace("condition", self.return_condition())
        if "primitiveee" in right_var:
            right_var = self.replace_random(right_var, "primitiveee", self.return_random_primitive_value())
        if "propertyy" in right_var:
            for _ in range(right_var.count("propertyy")):
                if len(to_replace[0]) > 0 and len(to_replace[1]) > 0 and len(to_replace[2]) > 1:
                    string_to_replace = choice(to_replace[2])
                    value_to_replace = choice(to_replace[0] + to_replace[1] + to_replace[2])
                else:
                    string_to_replace = "''"
                    value_to_replace = self.return_random_primitive_value()
                right_var = right_var.replace("propertyy", "{" + f"{string_to_replace}" + " : " + f"{value_to_replace}" + "}")
        if "var_str_r" in right_var:
            for _ in range(right_var.count("var_str_r")):
                if len(to_replace[2]) > 0:
                    replac = var_name
                else:
                    replac = "'" + "".join(choice(string.ascii_letters) for _ in range(20)) + "'"
                right_var = right_var.replace("var_str_r",  replac, 1)
        if "regexp" in right_var:
            for _ in range(right_var.count("regexp")):
                right_var = right_var.replace("regexp", '".\+"')
        if "inddx" in right_var:
            for _ in range(right_var.count("inddx")):
                right_var = right_var.replace("inddx", f"{randint(1, 20)}")
        right_var = right_var.replace(";", ",").replace("|", ":")
        return right_var

    def do_parse(self, statement, names, parsed_funcs_segment, var_name_value):
        if "!!" in statement:
            return ""
        if "function" in statement:
            type_function = statement.split("=")[1].strip()
            prototype = type_function[type_function.find("@") + 1: type_function.find(".")]
            funcs = self.return_variable_right_type(prototype, parsed_funcs_segment)
            funcs = self.switch_arguments(funcs, var_name_value)
            caller = type_function[type_function.find(".") + 2: type_function.rfind(".") - 1]
            statement = "try{ " + statement.replace(f"@{prototype}.@{caller}@.function", f"@{caller}@.{funcs}") + "}\ncatch(e){}"
        for i in range(0, int(parsed_funcs_segment["InitV"][0])):
            if f"@variable{i}@" in statement:
                statement = statement.replace(f"@variable{i}@", names[i])
                value = statement.split("=")[1].strip("\n ")
                if ("{" in value and "}" in value) or value in self.return_mutated_objects():
                    var_name_value[names[i]] = "Object"
                elif "'" in value[0] and "'" in value[len(value) - 1]:
                    var_name_value[names[i]] = "String"
                elif ("[" in value and "]" in value) or ("Array" in value):
                    var_name_value[names[i]] = "Array"
        if "ARITH" in statement:
            statement = self.replace_random(statement, "ARITH", self.return_random_arith())
        if "RANDOM_VAR" in statement:
            statement = self.replace_random(statement, "RANDOM_VAR", self.return_random_primitive_value())
        if "MUTATE_ARRAY" in statement:
            statement = self.replace_random(statement, "MUTATE_ARRAY", self.return_mutated_arrays())
        if "OP" in statement:
            statement = self.replace_random(statement, "OP", self.return_random_op())
        if "MUTATE_OBJECT" in statement:
            statement = self.replace_random(statement, "MUTATE_OBJECT", self.return_mutated_objects())
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
    parser.add_argument("--cycles", required=True, type=int)
    args = parser.parse_args()
    jsfuzzer = JSFuzzer()
    jsfuzzer.parse_file(args.file, args.cycles)

if __name__ == "__main__":
    main()
