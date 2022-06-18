import datetime
from os import stat
from random import choice, randint
import string
from subprocess import Popen, PIPE
import argparse
from jsbeautifier import beautify

class JSFuzzer:

    def parse_file(self, file):
        answer = ""
        var_value = ""
        var_name = ""
        loop_count = ""
        loop = ""
        loop_var = ""
        function_name = ""
        with open(file, "r") as f:
            answer = self.get_all_types_functions()
            statements = f.readlines()
            for statement in statements:
                statement = statement.rstrip()
                if isinstance(statement, str):
                    if "loop" in statement:
                        loop = statement.split(",")
                        loop_var = loop[1]
                        if "LENGTH" in statement:
                            loop_count = f"{loop[2]}.length"
                        else:
                            loop_count = loop[2]
                        answer += self.do_for_loop(loop_var, loop_count)
                    if statement[len(statement) - 1] == ";":
                        var = statement.split(",")
                        var_name = var[0]
                        if var[1] == "RANDOM_NUMBER":
                            rand_values = var[2].split("-")
                            var_value = randint(rand_values[0], rand_values[1])
                        else:
                            var_value = var[1]
                        answer += self.create_variable(var_name, var_value)
                    elif "=" in statement:
                        if "MODIFY_ITSELF_ARRAY" in statement:
                            answer += self.change_itself_array(statement)
                        else:
                            if "ALL_FUNCTION_CALL" not in statement:
                                answer += self.insert_value_in_variable(statement)
                    if "function" in statement:
                        function_name = statement.split(",")[1]
                        answer += self.create_function(function_name)
                    if "close_bracket" in statement:
                        answer += "}"
                    if f"{function_name}()" in statement:
                        answer += self.call_function(function_name)
                    if "ALL_FUNCTION_CALL" in statement:
                        var_name = statement.split("=")[0]
                        answer += "var methods = getMethods(" + var_name + ");"
                        answer += "var rand = Math.floor((Math.random() * methods.length));"
                        answer += var_name + ".methods[rand]();"
            bt_answer = (beautify(answer))
            print(bt_answer)
            self.js_run(bt_answer)

    def change_itself_array(self, statement):
        return f"{statement.split('=')[0]} = new Array({randint(20000, 30000)});"

    def call_function(self, function_name):
        return f"{function_name}()"

    def create_function(self, function_name):
        return f"var {function_name} = function()" + "{"

    def insert_value_in_variable(self, var):
        split_var = var.split("=")
        return f"{split_var[0]} = {split_var[1]}; "     

    def create_variable(self, var_name, var_value):
        return f"var {var_name} = {var_value}" 

    def return_keywords(self):
        return ["RANDOM_NUMBER", "LENGTH"]

    def do_for_loop(self, var_name, iteration_count):
        return "for(let " + var_name + ";" + var_name + "<=" + iteration_count + ";" + var_name + "++){"

    def fill_identifier(self, y):
        return "".join((choice(string.ascii_letters) for _ in range(y)))
    
    def js_run(self, func):
        proc = Popen("/home/androidparanoid/spidermonkey/obj-debug-x86_64-pc-linux-gnu/dist/bin/js", stdin=PIPE, universal_newlines=True, shell=True)
        proc.communicate(func)

    def get_all_types_functions(self):
        return """const getMethods = (obj) => {
                  let properties = new Set()
                  let currentObj = obj
                  do {
                    Object.getOwnPropertyNames(currentObj).map(item => properties.add(item))
                  } while ((currentObj = Object.getPrototypeOf(currentObj)))
                  return [...properties.keys()].filter(item => typeof obj[item] === 'function')
                }"""
    #def compile_all_report(self):
        #system("llvm-profdata merge -output=code.profdata *.profraw")
        #system("llvm-cov show /home/androidparanoid/spidermonkey/obj-debug-x86_64-pc-linux-gnu/dist/bin/js -instr-profile=code.profdata /home/androidparanoid/spidermonkey/js/src*.cpp -filename-equivalence -use-color --format html > /tmp/coverage.html")
    
    #def write_to_file_write(self, func):
        #with open("/home/androidparanoid/spidermonkey/obj-debug-x86_64-pc-linux-gnu/dist/bin/index.js", "w") as f:
            #f.write(func)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, type=str)
    parser.add_argument("--cycles", required=False, type=int, default=10)
    args = parser.parse_args()
    jsfuzzer = JSFuzzer()
    now_t = datetime.datetime.now().minute
    jsfuzzer.parse_file(args.file)
    now_t_2 = datetime.datetime.now().minute
    if (now_t_2 - now_t) >= 5:
        return

if __name__ == "__main__":
    main()
