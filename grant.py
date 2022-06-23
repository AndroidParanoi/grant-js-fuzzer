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
        start = False
        with open(file, "r") as f:
            statements = f.readlines()
            for cycle in range(cycles + 1):
                for statement in statements:
                    if "ONLY," in statement and cycle != 0:
                        continue
                    statement = statement.strip("ONLY,")
                    bt_answer += self.do_parse(statement, start)
                print(beautify(bt_answer))  
                bt_answer = ""
    
    def parse_for_loop(self, statement):
        loop = statement.split(",")
        return self.do_for_loop(loop[1], loop[2], loop[3])

    def do_parse(self, statement, start):
        new_statement = ""
        if not isinstance(statement, str):
            return ""
        if "%" in statement:
            if "%rand_string%" in statement:
                for _ in range(statement.count("%rand_string%")):
                    statement = statement.replace("%rand_string%", "".join(choice(string.ascii_letters) for x in range(20)))
            if "%rand_object%" in statement:
                for _ in range(statement.count("%rand_object%")):
                    statement = statement.replace("%rand_object%", self.return_mutated_objects())
        if "ARITH" in statement:
            for _ in range(statement.count("ARITH")):
                statement = statement.replace("ARITH", self.return_random_arith(), 1)
        if "MUTATE_OBJECTS" in statement:
            for _ in range(statement.count("MUTATE_OBJECTS") + 1):
                statement = statement.replace("MUTATE_OBJECTS", self.return_mutated_objects(), 1)
        if "MUTATE_ARRAY" in statement:
            for _ in range(statement.count("MUTATE_ARRAY") + 1):
                statement = statement.replace("MUTATE_ARRAY", self.return_mutated_arrays(), 1)
        if "RANDOM_VAR" in statement:
            for _ in range(statement.count("RANDOM_VAR") + 1):
                statement = statement.replace("RANDOM_VAR", self.return_random_primitive_value(), 1)
        if "OP" in statement:
            for _ in range(statement.count("OP") + 1):
                statement = statement.replace("OP", self.return_random_op(), 1)
        if "condition" in statement:
            statement = statement.replace("condition", self.return_condition())
        if re.search(r':.|=:', statement):
            funcs_index_start = statement.index(".") + 1
            var_name = statement[statement.index("$") + 1:statement.rindex("$")]
            caller = statement[statement.index("#") + 1:statement.rindex("#")]
            operator = statement[statement.index(":") + 1:statement.rindex(":")]
            for func in statement[funcs_index_start:].split("@"):
                if "index" in func:
                    for _ in range(func.count("index")):
                        func = func.replace("index", f"{randint(1, 20)}")
                if "%" in func:
                    if "%current_var%" in func:
                        func = func.replace("%current_var%", f"{var_name}")
                new_statement += f"{var_name} {operator} {caller}.{func};"
            return "try {" + new_statement + "}catch(e){}"
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
        return choice(["null", "undefined", "true", "false", "1", "''", "{}"])

    def return_random_op(self):
        return choice(["===", "==", ">=", "<=", "!=", "!==", "<", ">", "&&", "||"])
    
    def return_mutated_arrays(self):
        return choice([f"new Array({randint(10000,20000)})", f"Array.of({self.return_random_primitive_value()})", " new Int8Array(8)", "new Uint8Array(8)", "new Int16Array(16)", "new Uint16Array(16)", "new Int32Array(32)", "new Uint32Array(32)", "new Float32Array(32)", "new Float64Array(32)", "new BigInt64Array(32)", "new BigUint64Array(1)"])

    def return_mutated_objects(self):
        return choice(["Object", "Function", "Number", "AggregateError", "Atomics", " Boolean", " DataView", " Date", "WebAssembly", " Set"])

    def return_condition(self):
        return self.return_random_primitive_value() + self.return_random_op() + self.return_random_primitive_value()

    def return_random_arith(self):
        return choice(["+", "-", "*", "/"])
    
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, type=str)
    parser.add_argument("--cycles", required=False, type=int, default=10)
    args = parser.parse_args()
    jsfuzzer = JSFuzzer()
    jsfuzzer.parse_file(args.file, args.cycles)

if __name__ == "__main__":
    main()
