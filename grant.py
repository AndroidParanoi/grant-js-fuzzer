#!/bin/python

from random import randint
import argparse
from jsbeautifier import beautify
from random import choice

class JSFuzzer:

    def parse_file(self, file, cycles):
        bt_answer = ""
        with open(file, "r") as f:
            statements = f.readlines()
            for cycle in range(cycles + 1):
                for statement in statements:
                    if "ONLY," in statement and cycle != 0:
                        continue
                    statement = statement.strip("ONLY,")
                    bt_answer += self.do_parse(statement)
                print(beautify(bt_answer))  
                bt_answer = ""
    
    def parse_for_loop(self, statement):
        loop = statement.split(",")
        return self.do_for_loop(loop[1], loop[2], loop[3])

    
    def parse_for_fcall(self, statement):
        answer = ""
        split_statement = statement.split("=", 1)  
        var_name = split_statement[0]
        call_args = split_statement[1].split(",")
        libr_call = call_args[1]    
        for function in call_args[2:]:  
            answer += f"{var_name} = {libr_call}.{function.replace(';', ',')};"
        return answer   

    def do_parse(self, statement):
        if not isinstance(statement, str):
            return ""
        if "CREATE_ARRAY" in statement:
            statement = statement.replace("CREATE_ARRAY", f"new Array({randint(20000,30000)})")
        elif "CREATE_ARRAY_OF" in statement:
            statement = statement.replace("CREATE_ARRAY_OF", f"Array.of({choice(self.return_random_primitive_value())})")
        elif "MUTATE_ARRAY" in statement:
            statement = statement.replace("MUTATE_ARRAY", self.return_mutated_arrays())
        if "RANDOM_VAR" in statement:
            statement = statement.replace("RANDOM_VAR", self.return_random_primitive_value())
        if "OP" in statement:
            statement = statement.replace("OP", self.return_random_op())
        if "condition" in statement:
            statement = statement.replace("condition", self.return_condition())
        if ";" not in statement and "FCALL" not in statement and "loop" not in statement and "call" not in statement:
            return statement
        elif "FCALL" in statement:
            return self.parse_for_fcall(statement)
        elif "for_loop" in statement:
            return self.parse_for_loop(statement)
        elif "call" in statement:
            return statement.split(",")[1] + ";"
        return statement

    def do_for_loop(self, var_name, loop_count, loop_incr_decre):
        return f"for(let {var_name}; {loop_count}; {loop_incr_decre})" + "{"

    def return_random_primitive_value(self):
        return choice(["null", "undefined", "true", "false", "1", "''", "{}"])

    def return_random_op(self):
        return choice(["===", "==", ">=", "<=", "!=", "!==", "<", ">", "&&", "||"])
    
    def return_mutated_arrays(self):
        return choice([f"new Array({randint(10000,20000)})", f"Array.of({self.return_random_primitive_value()})"])

    def return_condition(self):
        return self.return_random_primitive_value() + self.return_random_op() + self.return_random_primitive_value()
    
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, type=str)
    parser.add_argument("--cycles", required=False, type=int, default=10)
    args = parser.parse_args()
    jsfuzzer = JSFuzzer()
    jsfuzzer.parse_file(args.file, args.cycles)

if __name__ == "__main__":
    main()
