#!/bin/python

from email.policy import strict
from random import randint
import argparse
import re
import string
from jsbeautifier import beautify
from random import choice

class JSFuzzer:

    def parse_file(self, file, cycles):
        bt_answer = ""
        var_names = dict()
        with open(file, "r") as f:
            statements = f.readlines()
            for cycle in range(cycles + 1):
                for statement in statements:
                    if "ONLY," in statement and cycle != 0:
                        continue
                    statement = statement.strip("ONLY,")
                    bt_answer += self.do_parse(statement, var_names)
                print(beautify(bt_answer))  
                bt_answer = ""
    
    def parse_for_loop(self, statement):
        loop = statement.split(",")
        return self.do_for_loop(loop[1], loop[2], loop[3])

    def replace_random(self, statement, rand, value):
        for _ in range(statement.count(rand)):
            statement = statement.replace(rand, choice(value), 1)
        return statement

    def parse_function_calls(self, var_type, sign_type, var_names, statement):
        new_statement = ""
        for var_name in var_names:
            if var_type not in var_names[var_name]:
                continue
            for function in statement[statement.find(".") + 1:].split("@"):
                if "index" in function:
                    for _ in range(statement.count("index")):
                        function = function.replace("index", f"{randint(1,11)}", 1)
                if "%vars%" in function:
                    function = function.replace("%vars%", var_name)
                new_statement += "try {" + f"{var_name} {sign_type} {var_name}.{function};" + "}catch(e){console.log(e)}"
        return new_statement

    def do_parse(self, statement, var_names):
        if not isinstance(statement, str):
            return ""
        if "%rand_string%" in statement:
            statement = statement.replace("%rand_string%", "".join(choice(string.ascii_letters) for _ in range(randint(5,10))))
        if "$" in statement:
            var_names[statement[statement.find("$") + 1:statement.rfind("$")]] = statement[statement.find("#") + 1:statement.rfind("#")]
            statement = statement.replace("$", '').replace("#", '')
        if "FUNCTION_CALLS" in statement:
            var_type = statement[statement.find("#") + 1:statement.rfind("#")]
            sign_type = re.findall(r".=", statement)[0]
            statement = self.parse_function_calls(var_type, sign_type, var_names, statement)
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
            statement = self.replace_random(statement, "OP", self.return_condition())
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
    parser.add_argument("--cycles", required=False, type=int, default=10)
    args = parser.parse_args()
    jsfuzzer = JSFuzzer()
    jsfuzzer.parse_file(args.file, args.cycles)

if __name__ == "__main__":
    main()
