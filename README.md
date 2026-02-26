# Ware Language Reference

Ware is a simple, readable programming language designed to feel like plain English.

```
python3 ware.py myprogram.ware     // run a file
python3 ware.py                    // open the interactive REPL
python3 ware.py build myprogram.ware  // build a standalone launcher
```

---

## Variables

```
name is "Alice"
age is 25
price is 9.99
active is true
nothing_yet is nothing
```

Use `constant` for values that should never change:

```
constant MAX_SCORE is 100
constant APP_NAME is "My App"
```

---

## Showing Output

```
show "Hello, world!"
show age
show age + 1
show f"Hello {name}, you are {age} years old!"
```

f-strings let you embed any expression inside `{ }`:

```
x is 10
show f"Double x is {x * 2}"
show f"Name in caps: {upper(name)}"
```

---

## Reading Input

`read` automatically converts numbers — you don't need to convert manually:

```
show "Enter your age:"
read age
show age + 1       // works as a number if you typed one
```

---

## Math

```
show 10 + 5
show 10 - 3
show 4 * 2
show 10 / 3
show 17 % 5        // remainder
show 2 * (3 + 4)
show -x            // negation
```

**Math functions:**

| Function | What it does | Example |
|---|---|---|
| `sqrt(x)` | Square root | `sqrt(16)` → 4 |
| `power(x, n)` | x to the power of n | `power(2, 8)` → 256 |
| `abs(x)` | Absolute value | `abs(-5)` → 5 |
| `round(x, n)` | Round to n decimal places | `round(3.14159, 2)` → 3.14 |
| `floor(x)` | Round down | `floor(4.9)` → 4 |
| `ceil(x)` | Round up | `ceil(4.1)` → 5 |
| `log(x)` | Natural logarithm | `log(100)` |
| `sin(x)` | Sine | `sin(pi)` |
| `cos(x)` | Cosine | `cos(0)` |
| `clamp(x, min, max)` | Keep x between min and max | `clamp(15, 0, 10)` → 10 |
| `to_fixed(x, n)` | Format number to n decimal places as text | `to_fixed(3.14159, 2)` → "3.14" |
| `to_hex(x)` | Convert to hex string | `to_hex(255)` → "ff" |
| `to_bin(x)` | Convert to binary string | `to_bin(10)` → "1010" |
| `random()` | Random decimal between 0 and 1 | `random()` |
| `random_int(a, b)` | Random whole number from a to b | `random_int(1, 6)` |
| `pi` | The value of π | `pi` → 3.14159... |

---

## Strings

**Creating strings:**
```
greeting is "Hello, world!"
empty is ""
```

**Combining strings:**
```
full_name is "Alice" + " " + "Smith"
repeated is "ha" * 3       // "hahaha"
```

**String functions:**

| Function | What it does | Example |
|---|---|---|
| `length(s)` | Number of characters | `length("hello")` → 5 |
| `upper(s)` | All uppercase | `upper("hi")` → "HI" |
| `lower(s)` | All lowercase | `lower("HI")` → "hi" |
| `trim(s)` | Remove whitespace from both ends | `trim("  hi  ")` → "hi" |
| `strip_chars(s, chars)` | Remove specific characters from ends | `strip_chars("***hi***", "*")` → "hi" |
| `replace(s, old, new)` | Replace all occurrences | `replace("hi world", "world", "ware")` |
| `slice(s, from, to)` | Get a section (1-indexed) | `slice("hello", 2, 4)` → "ell" |
| `char_at(s, i)` | Get character at position (1-indexed) | `char_at("hello", 1)` → "h" |
| `find(s, sub)` | Position of substring (0 if not found) | `find("hello", "ll")` → 3 |
| `count(s, sub)` | Count occurrences of substring | `count("hello", "l")` → 2 |
| `repeat(s, n)` | Repeat string n times | `repeat("ha", 3)` → "hahaha" |
| `pad_left(s, n)` | Pad with spaces on the left to width n | `pad_left("42", 6)` → "    42" |
| `pad_left(s, n, c)` | Pad with character c on the left | `pad_left("42", 6, "0")` → "000042" |
| `pad_right(s, n)` | Pad with spaces on the right | `pad_right("hi", 6)` → "hi    " |
| `pad_right(s, n, c)` | Pad with character c on the right | `pad_right("hi", 6, "-")` → "hi----" |
| `split(s, sep)` | Split into a list | `split("a,b,c", ",")` → ["a","b","c"] |
| `join(list, sep)` | Join a list into a string | `join(["a","b","c"], "-")` → "a-b-c" |
| `words(s)` | Split into list of words | `words("one two three")` |
| `lines(s)` | Split into list of lines | `lines("a\nb\nc")` |
| `to_chars(s)` | Split into list of characters | `to_chars("hi")` → ["h","i"] |
| `contains(s, sub)` | Check if string contains substring | `contains("hello", "ell")` → true |
| `starts(s, sub)` | Check if string starts with substring | `starts("hello", "he")` → true |
| `ends(s, sub)` | Check if string ends with substring | `ends("hello", "lo")` → true |

**String checking functions:**

| Function | What it does | Example |
|---|---|---|
| `is_empty(s)` | True if string has no characters | `is_empty("")` → true |
| `is_upper(s)` | True if all letters are uppercase | `is_upper("HI")` → true |
| `is_lower(s)` | True if all letters are lowercase | `is_lower("hi")` → true |
| `is_numeric(s)` | True if string looks like a number | `is_numeric("42")` → true |
| `is_alpha(s)` | True if string contains only letters | `is_alpha("hello")` → true |

**Converting:**

| Function | What it does |
|---|---|
| `number(s)` | Convert text to a number |
| `text(x)` | Convert anything to text |

---

## Booleans

```
active is true
done is false

if active is true,
    show "still going!"
.
```

`and`, `or`, `not` work as expected:

```
if age is bigger than 18 and active is true,
    show "eligible"
.
```

---

## Comparisons

```
x is 7

if x is 10,           // equals
if x is not 10,       // not equals
if x is bigger than 5,
if x is smaller than 10,
```

You can chain comparisons using `and`:

```
if x is bigger than 5 and x is smaller than 10,
    show "between 5 and 10"
.
```

---

## If / Else

```
if score is bigger than 90,
    show "A grade"
else,
    show "Keep trying"
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

## During Loop (count from 1 to n)

```
during i, range(5),
    show i
.
```

---

## For Each Loop

Loop over a list, dictionary keys, or any iterable:

```
fruits is ["apple", "banana", "cherry"]
for each fruit in fruits,
    show fruit
.

scores is {"Alice": 95, "Bob": 87}
for each name in scores,
    show name
.
```

---

## Break and Continue

```
during i, range(10),
    if i is 5,
        break
    .
    if i is 3,
        continue
    .
    show i
.
```

---

## Lists

```
fruits is ["apple", "banana", "cherry"]
nums is [10, 20, 30]
mixed is "hello" and 42 and true
```

Lists are **1-indexed** — the first item is at position 1:

```
show fruits[1]           // "apple"
fruits[2] is "mango"     // update an item
add to fruits, "grape"   // add to end
```

**List functions:**

| Function | What it does |
|---|---|
| `size(list)` | Number of items |
| `length(list)` | Same as size |
| `first(list)` | First item |
| `last(list)` | Last item |
| `is_empty(list)` | True if list has no items |
| `has(list, item)` | True if item is in list |
| `index_of(list, item)` | Position of item (0 if not found) |
| `count_in(list, item)` | How many times item appears |
| `reverse(list)` | New list in reverse order |
| `sort(list)` | New sorted list |
| `remove(list, i)` | New list without item at position i |
| `unique(list)` | New list with duplicates removed |
| `flatten(list)` | Flatten a nested list one level |
| `sum_list(list)` | Sum of all numbers |
| `max_of(list)` | Largest value |
| `min_of(list)` | Smallest value |
| `any_true(list)` | True if any item is true |
| `all_true(list)` | True if all items are true |

---

## Dictionaries

```
person is {"name": "Alice", "age": 25, "city": "London"}

show person["name"]       // "Alice"
person["age"] is 26       // update a value
```

**Dictionary functions:**

| Function | What it does |
|---|---|
| `keys(dict)` | List of all keys |
| `values(dict)` | List of all values |
| `has_key(dict, key)` | True if key exists |
| `is_empty(dict)` | True if dict has no entries |
| `size(dict)` | Number of entries |

---

## Type Checking

```
show type_of("hello")     // text
show type_of(42)          // number
show type_of([1, 2])      // list
show type_of({})          // dict
show type_of(true)        // bool
show type_of(nothing)     // nothing

show is_text("hi")        // true
show is_number(42)        // true
show is_list([1, 2])      // true
show is_dict({})          // true
show is_bool(true)        // true
```

---

## Functions

```
function greet which has name,
    show f"Hello, {name}!"
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

**Default parameter values:**

```
function greet which has name, greeting = "Hello",
    show f"{greeting}, {name}!"
.

greet("Alice")            // Hello, Alice!
greet("Bob", "Hey")       // Hey, Bob!
```

**Multiple return values:**

```
function minmax which has nums,
    return min_of(nums), max_of(nums)
.

lo, hi is minmax([5, 2, 8, 1, 9])
show f"min={lo}  max={hi}"
```

**Zero-parameter functions:**

```
function say_hi which has,
    show "Hi!"
.
```

---

## Closures / Nested Functions

Functions defined inside other functions remember the outer scope:

```
function make_counter which has start,
    count is start
    function increment which has amount = 1,
        count is count + amount
        return count
    .
    return increment
.

counter is make_counter(0)
show counter(1)    // 1
show counter(1)    // 2
show counter(5)    // 7
```

---

## Classes

```
class Animal,
    function init which has name, sound,
        self.name is name
        self.sound is sound
    .
    function speak which has,
        show f"{self.name} says {self.sound}!"
    .
    function rename which has new_name,
        self.name is new_name
    .
.

dog is new Animal("Rex", "woof")
dog.speak()               // Rex says woof!
show dog.name             // Rex
dog.rename("Max")
dog.speak()               // Max says woof!
```

- Use `class Name,` to define a class
- `function init` runs automatically when you use `new`
- Use `self.fieldname` to store and read object data
- Create objects with `new ClassName(args)`
- Call methods with `obj.method(args)`

---

## Error Handling

```
try,
    x is number("oops")
catch err,
    show f"Something went wrong: {err}"
.
```

---

## File Reading and Writing

```
// Read a file into a variable
open "notes.txt" as content
show content

// Write to a file (creates or overwrites)
write("output.txt", "Hello from Ware!")

// Append a line to a file
append("log.txt", "New entry added")
```

---

## Importing Other Files

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

Build simple desktop windows. Requires Python's `tkinter`.

```
make window "My App" size 400, 300

make label "What is your name?"
make textbox userName

make button "Say Hello" on click,
    show f"Hello {userName}!"
.
```

| Command | What it does |
|---|---|
| `make window "Title" size w, h` | Create a window |
| `make label "text"` | Add a text label |
| `make textbox varName` | Add a text input — the variable holds whatever is typed |
| `make button "text" on click, ... .` | Add a clickable button with a body of code |

---

## Variables Inspector

Type `vars` anywhere to see all current variables and their values:

```
name is "Alice"
age is 25
vars
// shows:
//   age = 25
//   name = Alice
```

---

## Comments

```
// This is a comment
name is "Ware"   // inline comment
```

---

## Quick Reference

| Syntax | What it does |
|---|---|
| `x is value` | Assign variable |
| `constant x is value` | Assign constant (can't change) |
| `show x` | Print to screen |
| `show f"Hi {name}"` | Print with template |
| `read x` | Get user input (auto-detects type) |
| `if cond, ... .` | Conditional |
| `if cond, ... else if, ... else, ... .` | If / else if / else |
| `while cond, ... .` | While loop |
| `during i, range(n), ... .` | Count loop (1 to n) |
| `for each x in list, ... .` | Loop over items |
| `function f which has x, ... .` | Define function |
| `function f which has x = 5, ... .` | Function with default param |
| `function f which has, ... .` | Function with no params |
| `return a, b` | Return multiple values |
| `a, b is f()` | Capture multiple returns |
| `x is [1, 2, 3]` | Create list |
| `x[1]` | Access item (1-indexed) |
| `x[1] is val` | Update item |
| `add to x, item` | Append to list |
| `x is {"a": 1}` | Create dictionary |
| `x["key"]` | Access dict value |
| `import "file.ware"` | Import another file |
| `open "file.txt" as x` | Read file |
| `write("file.txt", "text")` | Write file |
| `append("file.txt", "text")` | Append to file |
| `try, ... catch err, ... .` | Error handling |
| `class Name, ... .` | Define a class |
| `new ClassName(args)` | Create an object |
| `obj.method()` | Call a method |
| `self.field is val` | Set object field |
| `make window "T" size w, h` | GUI window |
| `make label "text"` | GUI label |
| `make textbox name` | GUI input box |
| `make button "t" on click, ... .` | GUI button |
| `vars` | Show all variables |
| `break` | Exit loop |
| `continue` | Skip to next iteration |
| `// text` | Comment |
| `true` / `false` / `nothing` | Boolean / null |
| `and` / `or` / `not` | Logic |
| `is` / `is not` | Equal / not equal |
| `is bigger than` | Greater than |
| `is smaller than` | Less than |
| `+` `-` `*` `/` `%` | Math operators |
| `"ha" * 3` | String repeat |

---

## Full Example — Gradebook

```
// Simple gradebook program

constant PASS_MARK is 50

scores is {"Alice": 88, "Bob": 42, "Charlie": 95, "Dana": 67}

passed is 0
failed is 0

for each name in scores,
    grade is scores[name]
    if grade is bigger than PASS_MARK,
        show f"{name}: {grade} — PASS"
        passed is passed + 1
    else,
        show f"{name}: {grade} — FAIL"
        failed is failed + 1
    .
.

total is passed + failed
show f"\n{passed} passed out of {total}"
show f"Pass rate: {to_fixed(passed / total * 100, 1)}%"
```
