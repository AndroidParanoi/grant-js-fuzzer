# grant
A simple grammar based js fuzzer I'm building
# Usage
Give the file and cycle flags with --file and --cycles respectively. The file ***must*** be written according to the rules:
# Rules
***ONLY,*** - Insert before a statement to print it once

***var name = function()*** - Is converted onto a function declaration in javascript: "var name = function() {"

***try*** - Initiates a try block: "try {"

***catch()*** - Closes the try block with a catch - "catch(e) {}"

***var variable_name = value;*** - Initialiazes a variable with name "variable_name" and value "value": "var variable_name = value;"

***variable_name = value;*** - Reassigns the variable with name "variable_name" to value "value": "variable_name = value;"

***FCALL*** - variable4,FCALL,Callee.abs(variable4),acos(variable4)...etc - Tells jsfuzzer the next statements will be function calls with argument variable4, assigned to variable4 from the Callee.

***MODIFY_ITSELF_ARRAY*** - variable4 = MODIFY_ITSELF_ARRAY - Initialies a variable to a new Array of random length.

***close_bracket*** - Closes the previously opened bracket. (***Brackets must be closed in order to have valid js. If you use 'function(),name', then you must write close_bracket when the function body is finished. This applies to every instruction which opens brackets except for catch***

***loop,g,length*** - Initialiazes a for loop - "for(let g = 0; g < length; g++) {"

***call,function_name(arguments)*** - Calls the function named 'function_name' with arguments 'arguments'. - "function_name(arguments);"

***return value*** - Returns from the current function body with value.

 
***EXAMPLE:***

```
ONLY,var swag2 = function(argument)
ONLY,try
ONLY,loop,i,argument.length
ONLY,
ONLY,argument[i] = i
ONLY,close_bracket
ONLY,catch()
ONLY,close_bracket
ONLY,loop,i,100
ONLY,if(i === i){
ONLY,i = 1.1
ONLY,call,swag2(i)
ONLY,close_bracket
ONLY,close_bracket
ONLY,var swag3 = function(argument1,argument2)
ONLY,try
ONLY,loop,i,argument1.length + argument2
ONLY,argument1[length] = true && argument2[length]
ONLY,close_bracket
ONLY,catch()
ONLY,close_bracket
ONLY,loop,i,100
ONLY,if(i === i){
ONLY,var t = i
ONLY,t = FCALL,Math,sin(i)
ONLY,i = t
ONLY,call,swag3(i, t)
ONLY,close_bracket
ONLY,close_bracket
```

***GENERATED CODE:***

```
var swag2 = function(argument) {
    try {
        for (let i = 0; i <= argument.length; i++) {
            argument[i] = i
        }
    } catch (e) {
        console.log(e);
    }
}
for (let i = 0; i <= 100; i++) {
    if (i === i) {
        i = 1.1
        swag2(i);
    }
}
var swag3 = function(argument1, argument2) {
    try {
        for (let i = 0; i <= argument1.length + argument2; i++) {
            argument1[length] = true && argument2[length]
        }
    } catch (e) {
        console.log(e);
    }
}
for (let i = 0; i <= 100; i++) {
    if (i === i) {
        var t = i
        t = Math.sin(i);
        i = t
        swag3(i, t);
    }
}


```
