#!/bin/python

from random import randint
import argparse
import re
from jsbeautifier import beautify

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
        return self.do_for_loop(loop[1], loop[2])

    
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
        answer = ""
        if not isinstance(statement, str):
            return ""
        if ";" not in statement and "FCALL" not in statement and "loop" not in statement and "call" not in statement:
            return statement
        if "FCALL" in statement:
            return self.parse_for_fcall(statement)
        elif "for_loop" in statement:
            return self.parse_for_loop(statement)
        if "call" in statement:
            return statement.split(",")[1] + ";"
        return statement

    def do_for_loop(self, var_name, loop_count):
        return f"for(let {var_name}; {loop_count}; {var_name.split('=')[0]}++)" + "{"
    
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, type=str)
    parser.add_argument("--cycles", required=False, type=int, default=10)
    args = parser.parse_args()
    jsfuzzer = JSFuzzer()
    jsfuzzer.parse_file(args.file, args.cycles)

if __name__ == "__main__":
    main()
