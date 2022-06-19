from random import choice, randint
from re import T
import string
import argparse
from jsbeautifier import beautify
from random import choice

class JSFuzzer:

    def parse_file(self, file, cycles):
        bt_answer = ""
        skip = False
        print(self.get_all_types_functions())
        with open(file, "r") as f:
            statements = f.readlines()
            for cycle in range(cycles):
                for statement in statements:
                    statement = statement.rstrip()
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
        type_of_object = ""
        if isinstance(statement, str):
            if "try" in statement:
                answer += "try{"
            if "loop" in statement:
                loop = statement.split(",")
                loop_var = loop[1]
                if "LENGTH" in statement:
                    loop_count = f"{loop[2]}.length"
                else:
                    loop_count = loop[2]
                answer += self.do_for_loop(loop_var, loop_count)
            if "OP" in statement:
                statement = statement.replace("OP", choice(["===", "==", "!=", "!==", "<", ">", "<=", ">=", "&&", "||"]))
            if "RANDOM_TYPE" in statement:
                statement = statement.replace("RANDOM_TYPE", choice(["''", "[]", "Object", "1", "undefined", "null"]))
            if statement[len(statement) - 1] == ";":
                var = statement.split(",")
                var_name = var[0]
                var_value = var[1]
                answer += self.create_variable(var_name, var_value)
            elif "=" in statement:
                if "MODIFY_ITSELF_ARRAY" in statement:
                    answer += self.change_itself_array(statement)
                else:
                    if "ALL_FUNCTION_CALL" not in statement:
                        answer += self.insert_value_in_variable(statement)
            if "function" in statement:
                function = statement.split(",")
                function_name = function[1]
                argument = function[0] 
                answer += self.create_function(function_name, argument)
            if "close_bracket" in statement:
                answer += "}"
            if "ALL_FUNCTION_CALL" in statement:
                vars = statement.split("=")
                var_name = vars[0]
                split_vars = vars[1].split(",")
                type_of_object = split_vars[0].split("_")[3]
                argument = split_vars[1]
                answer += "var methods = getMethods(" + type_of_object + ");"
                answer += "var rand = Math.floor((Math.random() * methods.length));"
                answer += f"var func = methods[rand];"
                answer += f"{var_name} = {type_of_object}.func({argument});"
            if "strict-mode" in statement:
                answer += '"use-strict";'
            if "catch" in statement:
                answer += "}catch(e){console.log(e);"
            if "call" in statement:
                answer += f"{statement.split(',')[1]};"
            return beautify(answer)


    def return_available_objects(self):
        return ["Object", "Function", "String", "Array"]

    def change_itself_array(self, statement):
        return f"{statement.split('=')[0]} = new Array({randint(1000, 10000)});"

    def call_function(self, function_name):
        return f"{function_name}()"

    def create_function(self, function_name, argument):
        return f"var {function_name} = {argument}" + "{"

    def insert_value_in_variable(self, var):
        split_var = var.split("=", 1)
        return f"{split_var[0]} = {split_var[1]}; "     

    def create_variable(self, var_name, var_value):
        return f"var {var_name} = {var_value}" 

    def return_keywords(self):
        return ["RANDOM_NUMBER", "LENGTH"]

    def do_for_loop(self, var_name, iteration_count):
        return "for(let " + var_name + " = 0;" + var_name + "<=" + iteration_count + ";" + var_name + "++){"

    def fill_identifier(self, y):
        return "".join((choice(string.ascii_letters) for _ in range(y)))
    
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
