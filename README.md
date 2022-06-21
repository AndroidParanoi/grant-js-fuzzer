# grant
A simple grammar based js fuzzer I'm building
# Usage
Give the file and cycle flags with --file and --cycles respectively. The file ***must*** be written according to the rules:
# Rules
***ONLY,*** - Insert before a statement to print it once

***var name = function()*** - Is converted onto a function declaration in javascript: "var name = function() {"

***try {*** - Initiates a try block: "try {"

***}catch(e){do_stuff;}*** - Closes the try block with a catch - "catch(e) {do_stuff;}"

***var variable_name = value;*** - Initialiazes a variable with name "variable_name" and value "value": "var variable_name = value;"

***variable_name = value;*** - Reassigns the variable with name "variable_name" to value "value": "variable_name = value;"

***FCALL*** - variable4,FCALL,Callee.abs(variable4),acos(variable4)...etc - Tells jsfuzzer the next statements will be function calls with argument variable4, assigned to variable4 from the Caller.

***}*** - Closes the previously opened bracket. (***Brackets must be closed in order to have valid js. If you use 'var name = function()', then you must write close_bracket when the function body is finished. This applies to every instruction which opens brackets except for catch***

***for_loop,i=0,i<=1000*** - Initialiazes a for loop - "for(let g = 0; g < length; g++) {"

***call,function_name(arguments)*** - Calls the function named 'function_name' with arguments 'arguments'. - "function_name(arguments);"

***return value*** - Returns from the current function body with value.

***IF(condition){*** - Prints the if statement - "if(''===''){do_stuff}"

 
***EXAMPLE:***

```
ONLY,var swag = function() {
ONLY,    try {
ONLY,        var arr = new Array(10000);
ONLY,        var str = '';
ONLY,        var n = 1;
ONLY,        var unde = undefined;
ONLY,        var nu = null;
ONLY,        var obj = {};
ONLY,        var constr = '';
ONLY,        var d = new Date();
ONLY,        for_loop,i=0,i<=10000
ONLY,            arr[i] = FCALL,arr,toString(),join((nu && constr)),pop(),push(str == n),shift(),unshift()
ONLY,            arr[arr.length] = FCALL,arr,sort().concat(arr)
ONLY,            arr[arr.length - 1] = FCALL,d,getTime(),getFullYear(),getMonth()
ONLY,            if(true){
ONLY,                console.log(1);
ONLY,                n = FCALL,Math,round(arr[i])
ONLY,                n = FCALL,Math,abs(n) + n
ONLY,                arr[n] = 0;
ONLY,                obj = FCALL,Object,values(obj) + obj,keys(obj) + obj
ONLY,            }
ONLY,        }
ONLY,    }catch(e){console.log(e);}
ONLY,}
ONLY,call,swag()
```

***GENERATED CODE:***

```
var swag = function() {
    try {
        var arr = new Array(10000);
        var str = '';
        var n = 1;
        var unde = undefined;
        var nu = null;
        var obj = {};
        var constr = '';
        var d = new Date();
        for (let i = 0; i <= 10000; i++) {
            arr[i] = arr.toString();
            arr[i] = arr.join((nu && constr));
            arr[i] = arr.pop();
            arr[i] = arr.push(str == n);
            arr[i] = arr.shift();
            arr[i] = arr.unshift();
            arr[arr.length] = arr.sort().concat(arr);
            arr[arr.length - 1] = d.getTime();
            arr[arr.length - 1] = d.getFullYear();
            arr[arr.length - 1] = d.getMonth();
            if (true) {
                console.log(1);
                n = Math.round(arr[i]);
                n = Math.abs(n) + n;
                arr[n] = 0;
                obj = Object.values(obj) + obj;
                obj = Object.keys(obj) + obj;
            }
        }
    } catch (e) {
        console.log(e);
    }
}
swag();

```
