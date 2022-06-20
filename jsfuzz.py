#!/bin/python
from random import randint
import argparse
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
        loop_var = loop[1]
        loop_count = loop[2]
        return self.do_for_loop(loop_var, loop_count)

    def parse_for_var(self, statement):
        var = statement.split(" ")
        var_name = var[1]
        var_value = " ".join(var[3:])
        return "var " + self.insert_value_in_variable(var_name, var_value)

    def parse_for_change_value_var(self, statement):
        var = statement.split(" ")
        var_name = var[0]
        if "}" in statement:
            var_value = " ".join(var[2:])
        else:
            var_value = var[2]
        if "MODIFY_ITSELF_ARRAY" in statement:
            var_value = f"new Array({randint(10000,20000)});"
        return self.insert_value_in_variable(var_name, var_value)

    def parse_for_function(self, statement):
        function = statement.split(" ")
        function_name = function[1]
        argument = function[3] 
        return self.create_function(function_name, argument)
    
    def parse_for_fcall(self, statement):
        answer = ""
        split_statement = statement.split("=")  
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
        if "loop" in statement:
            answer += self.parse_for_loop(statement)
        if "var" in statement and "function" not in statement:
            answer += self.parse_for_var(statement)
        if ("var" not in statement) and ("=" in statement) and ("if" not in statement and "else if" not in statement and "else" not in statement):
            if "FCALL" not in statement:
                answer += self.parse_for_change_value_var(statement)
        elif "function" in statement and "var" in statement:
            answer += self.parse_for_function(statement)
        if "close_bracket" in statement:
            answer += "}"
        if "FCALL" in statement:
            answer += self.parse_for_fcall(statement)
        if "strict-mode" in statement:
            answer += '"use-strict";'
        if "catch" in statement:
            answer += "}catch(e){console.log(e);}"
        if "call" in statement:
            answer += f"{statement.split(',' , 1)[1]};"            
        if "if" in statement or "else if" in statement or "else" in statement:
            answer += statement
        if "return" in statement and "}" not in statement:
            answer += "return"
        return answer


    def call_function(self, function_name):
        return f"{function_name}()"

    def create_function(self, function_name, argument):
        return f"var {function_name} = {argument}" + "{"

    def insert_value_in_variable(self, var_name, value):
        return f"{var_name} = {value}"     

    def do_for_loop(self, var_name, iteration_count):
        return "for(let " + var_name + " = 0;" + var_name + "<=" + iteration_count + ";" + var_name + "++){"
    
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, type=str)
    parser.add_argument("--cycles", required=False, type=int, default=10)
    args = parser.parse_args()
    jsfuzzer = JSFuzzer()
    jsfuzzer.parse_file(args.file, args.cycles)

if __name__ == "__main__":
    main()
