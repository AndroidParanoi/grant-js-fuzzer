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
            for cycle in range(cycles):
                for statement in statements:
                    if "ONLY" in statement and cycle != 0:
                        continue
                    statement = statement.strip("ONLY,")
                    bt_answer += self.do_parse(statement)
                print(beautify(bt_answer))  
                bt_answer = ""
    
    def parse_for_loop(self, statement):
        loop = statement.split(",")
        return self.do_for_loop(loop[1], loop[2])

    def parse_for_var(self, statement):
        var = statement.split(" ")
        return  "var " + self.insert_value_in_variable(var[1], " ".join(var[3:])) 

    def parse_for_change_value_var(self, statement):
        var = statement.split(" ", 2)
        var_value = " ".join(var[2:])
        if "MODIFY_ITSELF_ARRAY" in statement:
            var_value = f"new Array({randint(10000,20000)});"
        return self.insert_value_in_variable(var[0], var_value) 

    def parse_for_function(self, statement):
        function = statement.split(" ")
        return self.create_function(function[1], function[3])
    
    def parse_for_fcall(self, statement):
        answer = ""
        split_statement = statement.split("=", 1)  
        var_name = split_statement[0]
        call_args = split_statement[1].split(",")
        libr_call = call_args[1]    
        for function in call_args[2:]:  
            answer += f"{var_name} = {libr_call}.{function};"
        return answer   

    def do_parse(self, statement):
        answer = ""
        if not isinstance(statement, str):
            return ""
        if "try" in statement:
            answer += "try{"
        if "for_loop" in statement:
            answer += self.parse_for_loop(statement)
            return answer
        if "var" in statement and "function" not in statement and "FCALL" not in statement:
            answer += self.parse_for_var(statement)
        if ("var" not in statement) and ("=" in statement) and ("if" not in statement and "else if" not in statement and "else" not in statement) and "FCALL" not in statement and "return" not in statement:
            answer += self.parse_for_change_value_var(statement)
            return answer
        elif "function" in statement and "var" in statement:
            answer += self.parse_for_function(statement)
        if "close_bracket" in statement:
            answer += "}"
        if "FCALL" in statement:
            bak = ""
            if "var " in statement:
                bak = "var "
                statement = statement.replace("var", "")
            answer += bak + self.parse_for_fcall(statement)
            return answer
        if "strict-mode" in statement:
            answer += '"use-strict";'
        if "catch(" in statement:
            answer += statement
            return answer
        if "call" in statement:
            answer += f"{statement.split(',' , 1)[1]};"            
        if "if" in statement or "else if" in statement or "else" in statement:
            answer += statement
        if "return" in statement:
            answer += statement
            return answer
        if re.compile(".+\(.+\)").match(statement) and "var" not in statement:
            answer += statement
        return answer


    def call_function(self, function_name):
        return f"{function_name}()"

    def create_function(self, function_name, argument):
        return f"var {function_name} = {argument}" + "{"

    def insert_value_in_variable(self, var_name, value):
        return f"{var_name} = {value};"     

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
