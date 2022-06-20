from random import choice, randint
import string
import argparse
from jsbeautifier import beautify
from random import choice

class JSFuzzer:

    def parse_file(self, file, cycles):
        bt_answer = ""
        skip = False
        with open(file, "r") as f:
            statements = f.readlines()
            for cycle in range(cycles):
                for statement in statements:
                    if statement == "BEGIN_ONLY" and cycle != 0:
                        skip = True
                        continue
                    if statement == "END_ONLY" and cycle != 0:
                        skip = False
                    if skip:
                        continue
                    else:
                        bt_answer += self.do_parse(statement)
                print(beautify(bt_answer))  
                bt_answer = ""
                #self.js_run(bt_answer)
                #self.compile_all_report()

    def do_parse(self, statement):
        var_value = ""
        var_name = ""
        loop_count = ""
        loop = ""
        loop_var = ""
        function_name = ""
        answer = ""
        if not isinstance(statement, str):
            return ""
        if "try" in statement:
            answer += "try{"
        if "loop" in statement:
            loop = statement.split(",")
            loop_var = loop[1]
            loop_count = loop[2]
            answer += self.do_for_loop(loop_var, loop_count)
        if "var" in statement and "function" not in statement:
            var = statement.split(" ")
            var_name = var[1]
            var_value = var[3]
            answer += "var "
            answer += self.insert_value_in_variable(var_name, var_value)
        if ("var" not in statement) and ("=" in statement) and ("if" not in statement and "else if" not in statement and "else" not in statement):
            if "FCALL" not in statement:
                var = statement.split(" ")
                var_name = var[0]
                if "}" in statement:
                    var_value = " ".join(var[2:])
                else:
                    var_value = var[2]
                if "MODIFY_ITSELF_ARRAY" in statement:
                    var_value = f"new Array({randint(10000,20000)});"
                answer += self.insert_value_in_variable(var_name, var_value)
        elif "function" in statement and "var" in statement:
            function = statement.split(" ")
            function_name = function[1]
            argument = function[3] 
            answer += self.create_function(function_name, argument)
        if "close_bracket" in statement:
            answer += "}"
        if "FCALL" in statement:
            split_statement = statement.split("=")
            var_name = split_statement[0]
            call_args = split_statement[1].split(",")
            libr_call = call_args[1]
            for function in call_args[2:]:
                answer += f"{var_name} = {libr_call}.{function};"
        if "strict-mode" in statement:
            answer += '"use-strict";'
        if "catch" in statement:
            answer += "}catch(e){console.log(e);}"
        if "call" in statement:
            answer += f"{statement.split(',')[1]};"            
        if "if" in statement or "else if" in statement or "else" in statement:
            answer += statement
        if "return" in statement and "}" not in statement:
            answer += "return"
        return answer

    def return_random_choices(self):
        return [["Object", "Function", "Array", "RegExp", "Datetime"], ["!==", "!==", "==", "===", "<", ">", "<=", ">=", "&&", "||"], ["undefined", "''", "true", "false", "1", "{}", "null", "[]"]]
                
    def return_available_objects(self):
        return ["new Object", "new Function", "new String", "new Array", "new AggregateError", "new AsyncFunction", "new Atomics", "new BigInt64Array", "new BigUint64Array", "new Boolean", "new Dataview", "new Date", "new decodeURI"]

    def call_function(self, function_name):
        return f"{function_name}()"

    def create_function(self, function_name, argument):
        return f"var {function_name} = {argument}" + "{"

    def insert_value_in_variable(self, var_name, value):
        return f"{var_name} = {value}"     

    def do_for_loop(self, var_name, iteration_count):
        return "for(let " + var_name + " = 0;" + var_name + "<=" + iteration_count + ";" + var_name + "++){"
    
    #def js_run(self, func):
        #system("/home/androidparanoid/DynamoRIO-Linux-9.0.1/bin64/drrun -t drcov ")

    def get_all_types_functions(self):
        return """const getMethods = (obj) => {
                  let properties = new Set()
                  let currentObj = obj
                  do {
                    Object.getOwnPropertyNames(currentObj).map(item => properties.add(item))
                  } while ((currentObj = Object.getPrototypeOf(currentObj)))
                  return [...properties.keys()].filter(item => typeof obj[item] === 'function')
                }"""
#    def compile_all_report(self):
#        system("llvm-profdata merge -output=code.profdata *.profraw")
#        system("llvm-cov show /home/androidparanoid/spidermonkey/obj-debug-x86_64-pc-linux-gnu/dist/bin/js -instr-profile=code.profdata /home/androidparanoid/spidermonkey/js/src/**/*.cpp -use-color --format html > /tmp/coverage.html")

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, type=str)
    parser.add_argument("--cycles", required=False, type=int, default=10)
    args = parser.parse_args()
    jsfuzzer = JSFuzzer()
    jsfuzzer.parse_file(args.file, args.cycles)

if __name__ == "__main__":
    main()
