#!/bin/python
from random import randint
import argparse
import string
from jsbeautifier import beautify
from random import choice

class JSFuzzer:

    def parse_file(self, file):
        parsed_funcs_segment = dict()
        type_of_var = None
        funcs = None
        var_names = dict()
        bt_answer = ""
        with open(file, "r") as f:
            statement = f.readline()
            while True:
                    if "!!function_segment_end!!" in statement:
                        break
                    type_of_var, funcs = (self.parse_function_segment(statement))
                    parsed_funcs_segment[type_of_var] = funcs
                    statement = f.readline()
            while True:
                if "!!end_code_segment!!" in statement:
                    break
                bt_answer += self.do_parse(statement, var_names, parsed_funcs_segment, )
                statement = f.readline()
        print(beautify(bt_answer))
    
    def parse_for_loop(self, statement):
        loop = statement.split(",")
        return self.do_for_loop(loop[1], loop[2], loop[3])

    def replace_random(self, statement, rand, value):
        for _ in range(statement.count(rand)):
            statement = statement.replace(rand, choice(value), 1)
        return statement
    
    def switch_arguments(self, func, count):
        if "object" in func:
            for _ in range(func.count("object")):
                func = func.replace("object", choice(self.return_mutated_arrays()).split("(")[0].strip("new "), 1)
        if "key" in func:
            for _ in range(func.count("key")):
                func = func.replace("key", choice(self.return_random_primitive_value()), 1)
        if "value" in func:
            for _ in range(func.count("value")):
                func = func.replace("value", choice(self.return_random_primitive_value()), 1)
        if "list" in func:
            for _ in range(func.count("list")):
                func = func.replace("list", f"[{choice(self.return_random_primitive_value())}, {choice(self.return_random_primitive_value())}]", 1)
        if "condition" in func:
            for _ in range(func.count("condition")):
                func = func.replace("condition", self.return_condition())
        if "props" in func:
            for _ in range(func.count("props")):
                func = func.replace("props", "{" + f"{choice(self.return_random_primitive_value())}:{choice(self.return_random_primitive_value())}" + "}", 1)
        if "string" in func:
            for _ in range(func.count("string")):
                func = func.replace("string", "'" + "".join(choice(string.ascii_letters) for _ in range(10)) + "'", 1)
        if "regexp" in func:
            for _ in range(func.count("regexp")):
                func = func.replace("regexp", "'" + "".join(choice(string.ascii_letters) for _ in range(10)) + "'", 1)
        if "inddx" in func:
            for _ in range(func.count("index")):
                func = func.replace("inddx", f"{randint(1, 20)}", 1)
        if "arrowfunction" in func:
            count += 1
            if count >= 2:
                return func
            for _ in range(func.count("arrowfunction")):
                func = self.switch_arguments(func, count)
        return func

    def parse_function_calls(self, parsed_funcs_segment, var_names, var_name):
        func = ""
        new_statement = ""
        count = 0 
        var_caller = ""
        if "[" in var_name:
            var_name = var_name.split("[")[0]
        elif "." in var_name:
            var_name = var_name.split(".")[0]
        if "'" in var_names[var_name]:
            var_caller = var_name
            var_get = "String"
        elif "{}" in var_names[var_name]:
            var_caller = "Object"
            var_get = var_caller
        elif "Reflect" in var_names[var_name]:
            var_caller = "Reflect"
            var_get = "Reflect"
        func = choice(parsed_funcs_segment[var_get])
        func = self.switch_arguments(func, count)
        new_statement += f"{var_caller}.{func.replace(';', ',')}"
        return new_statement


    def parse_function_segment(self, statement):
        type_of_var = statement[statement.find(":") + 1:statement.rfind(":")]
        funcs = statement.split("=")[1].strip(" ").split(",")
        return (type_of_var, funcs)

    def do_parse(self, statement, var_names, parsed_funcs_segment, ):
        new_statement = ""
        if not isinstance(statement, str) or statement.startswith("!!"):
            return ""
        if "%rand_string%" in statement:
            for _ in range(statement.count("%rand_string%")):
                statement = statement.replace("%rand_string%", "".join(choice(string.ascii_letters) for _ in range(randint(5,10))), 1)
        if "ARITH" in statement:
            statement = self.replace_random(statement, "ARITH", self.return_random_arith())
        if "MUTATE_OBJECTS" in statement:
            statement = self.replace_random(statement, "MUTATE_OBJECTS", self.return_mutated_objects())
        if "MUTATE_ARRAY" in statement:
            statement = self.replace_random(statement, "MUTATE_ARRAY", self.return_mutated_arrays())
        if "RANDOM_VAR" in statement:
            statement = self.replace_random(statement, "RANDOM_VAR", self.return_random_primitive_value())
        if "OP" in statement:
            statement = self.replace_random(statement, "OP", self.return_random_op())
        if "condition" in statement:
            statement = self.replace_random(statement, "condition", self.return_condition())
        if "$" in statement:
            var_names[statement[statement.find("$") + 1:statement.rfind("$")]] = statement[statement.find("#") + 1:statement.rfind("#")]
            statement = statement.replace("$", '').replace("#", '')
        if "@function@" in statement:
            var_name = statement[statement.find("@") + 1: statement.split("=")[0].rfind("@")]
            new_statement = "try {" + statement.replace("@function@", self.parse_function_calls(parsed_funcs_segment, var_names, var_name)) + "}catch(e){}"
            statement = new_statement.replace("@", "")
        if ";" not in statement and "FCALL" not in statement and "loop" not in statement and "call_it" not in statement:
            return statement
        elif "for_loop" in statement:
            return self.parse_for_loop(statement)
        elif "call_it" in statement:
            return statement.split(",")[1] + ";"
        return statement

    def do_for_loop(self, var_name, loop_count, loop_incr_decre):
        return f"for(let {var_name}; {loop_count}; {loop_incr_decre})" + "{"

    def return_random_primitive_value(self):
        return ["null", "undefined", "true", "false", "1", "''", "{}"]

    def return_random_op(self):
        return ["===", "==", ">=", "<=", "!=", "!==", "<", ">", "&&", "||"]
    
    def return_mutated_arrays(self):
        return  [f"new Array({randint(10000,20000)})", f"Array.of({choice(self.return_random_primitive_value())})", " new Int8Array(8)", "new Uint8Array(8)", "new Int16Array(16)", "new Uint16Array(16)", "new Int32Array(32)", "new Uint32Array(32)", "new Float32Array(32)", "new Float64Array(32)", "new BigInt64Array(32)", "new BigUint64Array(1)"]

    def return_mutated_objects(self):
        return ["Object", "Function", "Number", "AggregateError", "Atomics", " Boolean", " DataView", " Date", "WebAssembly", " Set"]

    def return_condition(self):
        return self.return_random_primitive_value() + self.return_random_op() + self.return_random_primitive_value()

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
