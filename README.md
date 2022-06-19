# jsfuzzer
A simple grammar based js fuzzer I'm building
# Usage
Give the file and cycle flags with --file and --cycles respectively. The file ***must*** be written according to the rules:
# Rules
***BEGIN_ONLY*** - Initiates a section of javascript code that is to be printed only once.

***END_ONLY*** - Closes that section.

***function(),name*** - Is converted onto a function declaration in javascript: "var name = function() {"

***try*** - Initiates a try block: "try {"

***catch()*** - Closes the try block with a catch - "catch(e) {}"

***variable_name,value;*** - Initialiazes a variable with name "variable_name" and value "value": "var variable_name = value;"

***variable_name = value*** - Reassigns the variable with name "variable_name" to value "value": "variable_name = value;"

***FCALL*** - variable4,FCALL,Callee.abs(variable4),acos(variable4)...etc - Tells jsfuzzer the next statements will be function calls with argument variable4, assigned to variable4 from the Callee.

***MODIFY_ITSELF_ARRAY*** - variable4 = MODIFY_ITSELF_ARRAY - Initialies a variable to a new Array of random length.

***close_bracket*** - Closes the previously opened bracket. (***Brackets must be closed in order to have valid js. If you use 'function(),name', then you must write close_bracket when the function body is finished. This applies to every instruction which opens brackets except for catch***

***loop,g,length*** - Initialiazes a for loop - "for(let g = 0; g < length; g++) {"

***call,function_name(arguments)*** - Calls the function named 'function_name' with arguments 'arguments'. - "function_name(arguments);"

***return value*** - Returns from the current function body with value.

 
***EXAMPLE:***

```
BEGIN_ONLY
function(),hello_world
return "Hello World"
close_bracket
END_ONLY
```
