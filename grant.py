#!/bin/python
import argparse
import string
from jsbeautifier import beautify
from random import choice, randint

class JSFuzzer:

    def parse_file(self, file):
        parsed_funcs_segment = dict()
        type_of_var = None
        funcs = None
        bt_answer = ""
        var_types = {"Array":"new Array(10000)", "String": "''", "Object":"{}", "ArrayBuffer":"new ArrayBuffer(10000)", "DataView":"new DataView(new ArrayBuffer(10000))", "Boolean":"new Boolean(true)","Map":"new Map()"}
        with open(file, "r") as f:
            statement = f.readline()
            while True:
                    if "!!function_segment_end!!" in statement:
                        break
                    type_of_var, funcs = (self.parse_function_segment(statement))
                    parsed_funcs_segment[type_of_var] = funcs
                    if "InitV" in statement:
                        names, values = (self.parse_init_v_vars(parsed_funcs_segment, var_types))
                    statement = f.readline()
            for statement in f.readlines():
                if "!!statement_segment_end!!" in statement:
                    break
                bt_answer += self.do_parse(statement, names, parsed_funcs_segment)
        print(beautify(bt_answer))

    def parse_init_v_vars(self, parsed_funcs_segment, var_types):
        names = list()
        values = list()
        y = 0
        for i in range(int(parsed_funcs_segment["InitV"][0]) + 1):
            if y >= len(parsed_funcs_segment["InitV"][1].split(";")) - 1:
                y = 0
            else:
                y += 1
            name = f"var{i}"
            value = (parsed_funcs_segment["InitV"][1].split(";")[y].strip())
            print(f"var {name} = {var_types[value]};")
            names.append(name)
            values.append(value)
        return names, values

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
        if "var_str_r" in right_var:
            for _ in range(right_var.count("var_str_r")):
                right_var = right_var.replace("var_str_r",  "'" + "".join(choice(string.ascii_letters) for _ in range(20)) + "'", 1)
        if "regexp" in right_var:
            for _ in range(right_var.count("regexp")):
                right_var = right_var.replace("regexp", '".\+"')
        if "concatenator" in right_var:
            right_var = self.replace_random(right_var, "concatenator", self.return_mutated_arrays())
        if "inddx" in right_var:
            for _ in range(right_var.count("inddx")):
                right_var = right_var.replace("inddx", f"{randint(1, 20)}")
        if "json_string" in right_var:
            for _ in range(right_var.count("json_string")):
                right_var = right_var.replace("json_string", '{"swag":"1"}')
        right_var = right_var.replace(";", ",")
        return right_var

    def do_parse(self, statement, names, parsed_funcs_segment):
        if "!!" in statement:
            return ""
        if "function" in statement:
            type_function = statement.split("=")[1].strip()
            prototype = type_function[type_function.find("@") + 1: type_function.find(".")]
            funcs = self.return_variable_right_type(prototype, parsed_funcs_segment)
            funcs = self.switch_arguments(funcs)
            caller = type_function[type_function.find(".") + 2: type_function.rfind(".") - 1]
            statement = "try{ " + statement.replace(f"@{prototype}.@{caller}@.function", f"@{caller}@.{funcs}") + "}\ncatch(e){}"
        for i in range(0, int(parsed_funcs_segment["InitV"][0])):
            if f"@variable{i}@" in statement:
                statement = statement.replace(f"@variable{i}@", names[i])
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
    args = parser.parse_args()
    jsfuzzer = JSFuzzer()
    jsfuzzer.parse_file(args.file)

if __name__ == "__main__":
    main()
