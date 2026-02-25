# Ware Programming Language

Ware is a simple, readable programming language designed to look and feel like plain English. Files use the `.ware` extension and are run with the Ware interpreter.

```bash
python3 ware.py myprogram.ware
```

---

## Variables

```
name is "Alice"
age is 25
score is 10 + 5
```

## Constants

Constants can never be changed after being set.

```
constant MAX is 100
constant PI is 3.14159
show MAX
```

---

## Showing Output

```
show "Hello, world!"
show name
show 5 + 3
```

## String Templates (f-strings)

Embed expressions directly inside strings using `f"..."` and `{...}`.

```
name is "Alice"
age is 25
show f"Hello {name}, you are {age} years old!"
show f"Two plus two is {2 + 2}"
```

---

## Reading Input

```
read name
show "You entered: " + name
```

---

## Math

```
x is 10 + 5
x is 10 - 3
x is 4 * 2
x is 10 / 2
x is 17 % 5     // remainder (modulo)
```

**Built-in math functions:**

```
show sqrt(16)
show power(2, 8)
show abs(-5)
show round(3.14159, 2)
show floor(4.9)
show ceil(4.1)
show log(100)
show sin(pi)
show cos(0)
```

---

## Comparisons

```
if x is 10,
    show "x equals 10"
.

if x is not 5,
    show "x is not 5"
.

if x is bigger than 7,
    show "x is bigger than 7"
.

if x is smaller than 20,
    show "x is smaller than 20"
.
```

---

## Logic

```
if x is bigger than 5 and x is smaller than 20,
    show "x is between 5 and 20"
.

if x is 1 or x is 10,
    show "x is 1 or 10"
.

if not x is 0,
    show "x is not zero"
.
```

---

## If / Else

```
if name is "Alice",
    show "Hey Alice!"
else,
    show "Who are you?"
.
```

---

## While Loop

```
count is 1
while count is smaller than 6,
    show count
    count is count + 1
.
```

---

## During Loop

Counter starts at `1`.

```
during i, range(5),
    show i
.
```

---

## Break and Continue

```
during i, range(10),
    if i is 5,
        break
    .
    show i
.
```

---

## Functions

```
function greet which has name,
    show "Hello, " + name + "!"
.

greet("Alice")
```

**Returning a value:**

```
function double which has x,
    return x * 2
.

show double(5)
```

**Multiple return values:**

```
function minmax which has nums,
    return first(sort(nums)), last(sort(nums))
.

lo, hi is minmax([3, 1, 9, 2, 7])
show f"min={lo}  max={hi}"
```

---

## Lists

**Create a list:**

```
fruits is "apple" and "banana" and "cherry"
nums is [10, 20, 30, 40, 50]
```

Lists are **1-indexed** — the first item is at position `1`.

```
show fruits[1]       // apple
fruits[2] is "mango" // update an item
add to fruits, "watermelon"
```

**Built-in list functions:**

```
show size(fruits)
show first(fruits)
show last(fruits)
show reverse(fruits)
show sort([3, 1, 4, 1, 5])
show remove(fruits, 2)    // removes item at position 2
show has(fruits, "apple") // true or false
```

---

## String Functions

```
show length("hello")        // 5
show upper("ware")          // WARE
show lower("WARE")          // ware
show trim("  hello  ")      // hello
show replace("hi world", "world", "ware")
show contains("hello ware", "ware")  // true
show starts("hello", "he")           // true
show ends("hello", "lo")             // true
show slice("hello ware", 7, 10)      // ware
show split("a,b,c", ",")             // [a, b, c]
show join(["a","b","c"], "-")        // a-b-c
show number("42")                    // 42
show text(100)                       // "100"
```

---

## Type Checking

```
show is_number(42)       // true
show is_text("hi")       // true
show is_list([1, 2, 3])  // true
```

---

## Error Handling

Use `try` and `catch` to handle errors gracefully. The `catch` variable holds the error message.

```
try,
    x is number("oops")
catch err,
    show f"Something went wrong: {err}"
.
```

---

## File Reading and Writing

**Read a file:**

```
open "notes.txt" as content
show content
```

**Write to a file:**

```
write("output.txt", "Hello from Ware!")
```

**Append to a file:**

```
append("log.txt", "New line added")
```

---

## Importing Other Files

Split your code across multiple `.ware` files and import them.

```
// utils.ware
function double which has x,
    return x * 2
.
```

```
// main.ware
import "utils.ware"
show double(5)
```

---

## GUI

Build simple graphical windows with built-in GUI commands. Requires Python's `tkinter` to be installed.

```
make window "My App" size 400, 300

make label "Welcome to Ware!"
make textbox userName

make button "Say Hello" on click,
    show f"Hello {userName}!"
.

```

**GUI commands:**

| Command | What it does |
|---|---|
| `make window "Title" size w, h` | Create a window |
| `make label "text"` | Add a text label |
| `textbox varName` | Add a text input box |
| `make button "text" on click, ... .` | Add a clickable button |

---

## Comments

```
// This is a comment
name is "Ware"  // inline comment
```

---

## Booleans

```
flag is true

if flag is true,
    show "flag is on"
.
```

---

## Full Example — Number Guessing Game

```
// Number guessing game

constant SECRET is 7
guess is 0
tries is 0

show "Guess a number between 1 and 10:"

while guess is not SECRET,
    read guess
    tries is tries + 1

    if guess is smaller than SECRET,
        show "Too low! Try again:"
    .

    if guess is bigger than SECRET,
        show "Too high! Try again:"
    .
.

show f"You got it in {tries} tries!"
```

---

## Quick Reference

| Syntax | What it does |
|---|---|
| `x is 5` | Assign variable |
| `constant x is 5` | Assign constant |
| `show x` | Print to screen |
| `show f"Hi {name}"` | Print with template |
| `read x` | Get user input |
| `if ... , ... .` | Conditional |
| `if ... , ... else, ... .` | If / else |
| `while ... , ... .` | While loop |
| `during i, range(n), ... .` | Count loop (1 to n) |
| `function f which has x, ... .` | Define function |
| `return a, b` | Return multiple values |
| `a, b is f()` | Capture multiple returns |
| `x is "a" and "b"` | Create list |
| `x is [1, 2, 3]` | Create list (literal) |
| `x[1]` | Access list item (1-indexed) |
| `x[2] is "val"` | Update list item |
| `add to x, "item"` | Append to list |
| `import "file.ware"` | Import another file |
| `open "file.txt" as x` | Read file into variable |
| `write("file.txt", "text")` | Write to file |
| `append("file.txt", "text")` | Append to file |
| `try, ... catch err, ... .` | Error handling |
| `make window "Title" size w, h` | Create GUI window |
| `make label "text"` | GUI text label |
| `make textbox name` | GUI input box |
| `make button "text" on click, ... .` | GUI button |
| `break` | Exit loop |
| `continue` | Skip to next iteration |
| `// comment` | Comment |
| `true` / `false` | Boolean values |
| `is` / `is not` | Equal / not equal |
| `is bigger than` | Greater than |
| `is smaller than` | Less than |
| `and` / `or` / `not` | Logic operators |
| `+` `-` `*` `/` `%` | Math operators |
