# Ware Programming Language

**Version 4.0** — A clean, readable scripting language with built-in GUI support.

---

## Installation

```bash
python3 ware.py           # interactive REPL
python3 ware.py myapp.ware  # run a file
```

**VS Code extension:** Install `ware-language-2.0.0.vsix`
- `Extensions` panel → `…` menu → `Install from VSIX…`
- Provides: syntax highlighting, Ware Dark theme, 35+ snippets

---

## Syntax Overview

### Variables & Constants

```
name is "Alice"
age is 25
active is true
nothing_val is nothing

constant PI is 3.14159
```

### Strings & F-Strings

```
greeting is "Hello"
show f"Welcome, {name}! You are {age} years old."
show f"PI is approximately {round(PI, 4)}"
```

### Arithmetic & Comparisons

```
result is (10 + 3) * 2 / 5
mod is 17 % 4

if score is bigger than 90,
    show "A grade"
.

if name is not "Bob",
    show "Not Bob"
.
```

---

## Control Flow

### If / Else

```
if temperature is bigger than 30,
    show "It's hot!"
else,
    show "Comfortable."
.
```

### While Loop

```
count is 0
while count is smaller than 5,
    show f"Count: {count}"
    count is count + 1
.
```

### During (counted range)

```
during i, range(10),
    show f"  {i} squared = {i * i}"
.
```

### For Each

```
fruits is ["apple", "banana", "cherry"]
for each fruit in fruits,
    show f"  - {fruit}"
.
```

### Break / Continue

```
during i, range(20),
    if i % 2 is 0,
        continue
    .
    if i is bigger than 9,
        break
    .
    show i
.
```

---

## Functions

```
function greet which has name, greeting = "Hello",
    show f"{greeting}, {name}!"
.

greet("Alice")
greet("Bob", "Hey")
```

### Multiple Return Values

```
function min_max which has nums,
    return min_of(nums), max_of(nums)
.

lo, hi is min_max([3, 1, 4, 1, 5, 9])
show f"Min: {lo}, Max: {hi}"
```

### Closures

```
function make_counter which has start,
    count is start
    function increment which has by = 1,
        count is count + by
        return count
    .
    return increment
.

c is make_counter(0)
show c()    // 1
show c()    // 2
show c(5)   // 7
```

---

## Classes

```
class Animal,
    function init which has name, sound,
        self.name is name
        self.sound is sound
        self.tricks is []
    .
    function speak which has,
        show f"{self.name} says {self.sound}!"
    .
    function learn which has trick,
        add to self.tricks, trick
    .
.

dog is new Animal("Rex", "woof")
dog.speak()
dog.learn("sit")
show dog.tricks
```

---

## Error Handling

```
try,
    result is number("not a number")
catch err,
    show f"Caught: {err}"
.
```

---

## Lists

```
nums is [10, 3, 7, 1, 9]

add to nums, 42
show f"Size: {size(nums)}"
show f"First: {first(nums)}, Last: {last(nums)}"
show f"Sorted: {sort(nums)}"
show f"Sum: {sum_list(nums)}, Max: {max_of(nums)}"
show f"Reversed: {reverse(nums)}"
show nums[2]              // index (1-based)
```

## Dictionaries

```
scores is {"Alice": 95, "Bob": 78, "Charlie": 91}

for each name in scores,
    show f"{name}: {scores[name]}"
.

show has_key(scores, "Alice")
show keys(scores)
show values(scores)
```

---

## GUI

All GUI apps start with `make window`. Widgets are added top-to-bottom. Use `make row` for horizontal layout. Read widget values using the variable name directly.

### Window

```
make window "My App" size 400, 500
```

### Input Widgets

| Statement | Description |
|-----------|-------------|
| `make label "text"` | Static text |
| `make textbox myVar` | Single-line text input |
| `make password myVar` | Password input (masked) |
| `make number_input myVar, 0, 100` | Numeric input with bounds |
| `make multiline myVar` | Multi-line text area |
| `make checkbox myVar "Enable alerts"` | Toggle checkbox |
| `make slider myVar, 0, 100` | Range slider |
| `make dropdown myVar, ["A","B","C"]` | Select dropdown |
| `make color_picker myVar` | Color picker with hex |

### Display Widgets

| Statement | Description |
|-----------|-------------|
| `make progress myVar` | Progress bar (0–100) |
| `make status myVar "Ready"` | Status text line |
| `make badge myVar, "text", "ok"` | Colored pill badge (info/ok/warn/err) |
| `make listbox myVar, items` | Scrollable item list |
| `make table myVar, rows, headers` | Data table |
| `make image "path/to/img.png"` | Display an image |

### Layout

| Statement | Description |
|-----------|-------------|
| `make row, ... .` | Horizontal layout |
| `make column, ... .` | Vertical layout |
| `make separator` | Horizontal divider line |
| `make spacer` | Empty spacing |

### Canvas & Drawing

```
make canvas board, 400, 300

draw board color "#7c6af7"
draw board rect 10, 10, 100, 60
draw board circle 200, 150, 40
draw board line 0, 0, 400, 300
draw board text 50, 50, "Hello!"
draw board clear
```

### Buttons & Dialogs

```
make button "Submit" on click,
    show f"Name: {nameInput}"
    alert f"Hello, {nameInput}!"
.

confirm result, "Are you sure?"
if result is true,
    show "Confirmed!"
.
```

### Updating Widgets Dynamically

```
set myVar value 75          // set value/text
set myVar text "Updated!"
set myVar visible false     // hide/show
set myVar disabled true     // enable/disable
set myVar color "#ff0000"   // text color
set myVar background "#333" // background color
set myVar progress 60       // update progress bar
```

### Full Example

```
make window "Login" size 360, 300
make label "Username"
make textbox username
make label "Password"
make password password
make separator
make row,
    make button "Login" on click,
        if username is "" or password is "",
            alert "Please fill in all fields."
        else,
            show f"Logging in as {username}..."
            alert f"Welcome, {username}!"
        .
    .
    make button "Clear" on click,
        set username value ""
        set password value ""
    .
.
```

---

## Built-in Functions

### Math

| Function | Description |
|----------|-------------|
| `sqrt(x)` | Square root |
| `abs(x)` | Absolute value |
| `round(x, n)` | Round to n decimal places |
| `floor(x)` / `ceil(x)` | Floor / ceiling |
| `power(x, n)` | x to the power n |
| `log(x)` / `sin(x)` / `cos(x)` | Logarithm / trig |
| `clamp(x, min, max)` | Constrain to range |
| `random()` | Random float 0–1 |
| `random_int(a, b)` | Random integer a to b |
| `to_fixed(x, n)` | Format to n decimals |
| `to_hex(x)` / `to_bin(x)` | Convert to hex / binary string |

### Strings

| Function | Description |
|----------|-------------|
| `length(s)` | Character count |
| `upper(s)` / `lower(s)` | Case conversion |
| `trim(s)` | Remove surrounding whitespace |
| `strip_chars(s, chars)` | Remove specific edge characters |
| `replace(s, old, new)` | Replace substring |
| `contains(s, sub)` | True if substring present |
| `starts(s, prefix)` | Starts with test |
| `ends(s, suffix)` | Ends with test |
| `find(s, sub)` | Position of substring (1-based, 0 if not found) |
| `count(s, sub)` | Count occurrences of substring |
| `slice(s, start, end)` | Extract substring (1-based) |
| `char_at(s, i)` | Character at position (1-based) |
| `repeat(s, n)` | Repeat string n times |
| `pad_left(s, n, c)` | Pad to width n with char c |
| `pad_right(s, n, c)` | Pad to width n with char c |
| `split(s, delim)` | Split into list |
| `join(list, sep)` | Join list into string |
| `words(s)` | Split on whitespace |
| `lines(s)` | Split on newlines |
| `to_chars(s)` | Explode into character list |
| `number(s)` | Parse string to number |
| `text(x)` | Convert any value to string |

### String Checks

| Function | Description |
|----------|-------------|
| `is_empty(s)` | True if length 0 |
| `is_upper(s)` / `is_lower(s)` | Case check |
| `is_numeric(s)` | True if string is a valid number |
| `is_alpha(s)` | True if only letters |

### Lists

| Function | Description |
|----------|-------------|
| `size(x)` | Length of list, string, or dict |
| `first(list)` / `last(list)` | First / last element |
| `reverse(list)` | Reversed copy |
| `sort(list)` | Sorted copy |
| `remove(list, i)` | Remove element at index i (1-based) |
| `has(list, item)` | True if item in list |
| `index_of(list, item)` | Position (1-based, 0 if not found) |
| `unique(list)` | Deduplicated copy |
| `flatten(list)` | Flatten one level |
| `sum_list(list)` | Sum of numeric list |
| `max_of(list)` / `min_of(list)` | Maximum / minimum |
| `any_true(list)` / `all_true(list)` | Boolean aggregation |
| `count_in(list, item)` | Count occurrences of item |

### Dictionaries

| Function | Description |
|----------|-------------|
| `keys(dict)` | List of keys |
| `values(dict)` | List of values |
| `has_key(dict, key)` | True if key exists |

### Type Inspection

| Function | Description |
|----------|-------------|
| `type_of(x)` | Returns `"text"`, `"number"`, `"list"`, `"dict"`, `"bool"`, `"object"`, `"nothing"` |
| `is_text(x)` / `is_number(x)` | Type predicates |
| `is_list(x)` / `is_dict(x)` | Type predicates |
| `is_bool(x)` | Boolean type check |

---

## File I/O

```
// Read a file
open "data.txt" as content
show content

// Write / append
write("output.txt", "Hello!\n")
append("log.txt", f"Entry: {message}\n")
```

---

## Constants & Imports

```
constant MAX_SCORE is 100
constant APP_NAME is "My App"

import "utils.ware"
```

---

## Debugging

```
vars    // print all current variables
show type_of(myVar)
```

---

## Quick Reference

```
// Variable          name is value
// Constant          constant NAME is value
// Print             show expr  /  show f"text {var}"
// Input             read varName
// If                if cond, ... .  /  if cond, ... else, ... .
// While             while cond, ... .
// Counted loop      during i, range(n), ... .
// For each          for each x in list, ... .
// Function          function name which has a, b = default, ... .
// Class             class Name, ... .  /  new Name(args)  /  self.field
// Try/catch         try, ... catch err, ... .
// List              [1, 2, 3]   /  add to list, val   /  list[i]
// Dict              {"key": val}   /  dict["key"]
// Break/continue    break  /  continue
// GUI window        make window "Title" size w, h
// GUI widget        make button/textbox/slider/checkbox/...
// Set property      set widgetVar value newVal
// Canvas draw       draw canvasVar rect/circle/line/text/clear/color
// Dialog            alert "msg"  /  confirm result, "msg?"
// File              open "file" as var  /  write(path, text)
```
