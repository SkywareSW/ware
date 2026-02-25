```bash
python3 ware.py myprogram.ware
```

---

## Variables

Assign a value to a variable using `is`.

```
name is "Alice"
age is 25
score is 10 + 5
```

---

## Showing Output

Use `show` to print anything to the screen.

```
show "Hello, world!"
show name
show 5 + 3
```

---

## Reading Input

Use `read` to get input from the user and store it in a variable.

```
read name
show "You entered: " + name
```

---

## Math

Ware supports the four basic math operations.

```
x is 10 + 5
x is 10 - 3
x is 4 * 2
x is 10 / 2
show x
```

---

## Comparisons

Use `is` to compare two values for equality. Use `is not`, `is bigger than`, and `is smaller than` for other comparisons.

```
x is 10

if x is 10,
    show "x equals 10"
end

if x is not 5,
    show "x is not 5"
end

if x is bigger than 7,
    show "x is bigger than 7"
end

if x is smaller than 20,
    show "x is smaller than 20"
end
```

---

## Logic

Combine conditions with `and`, `or`, and `not`.

```
if x is bigger than 5 and x is smaller than 20,
    show "x is between 5 and 20"
end

if x is 1 or x is 10,
    show "x is 1 or 10"
end

if not x is 0,
    show "x is not zero"
end
```

---

## If / Else

```
name is "Alice"

if name is "Alice",
    show "Hey Alice!"
else,
    show "Who are you?"
end
```

---

## While Loop

Repeats a block as long as a condition is true.

```
count is 1

while count is smaller than 6,
    show count
    count is count + 1
end
```

---

## During Loop

Repeats a block a set number of times. The counter starts at `1`.

```
during i, range(5),
    show i
end
```

This prints `1` through `5`.

---

## Break and Continue

Use `break` to exit a loop early, and `continue` to skip to the next iteration.

```
during i, range(10),
    if i is 5,
        break
    end
    show i
end
```

```
during i, range(5),
    if i is 3,
        continue
    end
    show i
end
```

---

## Functions

Define a function with `function`, give it a name, and list its parameters after `which has`. Call it by name with arguments in parentheses.

```
function greet which has name,
    show "Hello, " + name + "!"
end

greet("Alice")
greet("Bob")
```

Functions can also return a value using `return`.

```
function add which has a, b,
    return a + b
end

result is add(3, 4)
show result
```

---

## Lists

Create a list by chaining values with `and`. Lists are **1-indexed** — the first item is at position `1`.

```
fruits is "apple" and "banana" and "cherry"

show fruits[1]
show fruits[2]
show fruits[3]
```

Add a new item to a list with `add to`.

```
add to fruits, "watermelon"
show fruits[4]
```

---

## Comments

Use `//` for comments. Anything after `//` on a line is ignored.

```
// This is a comment
name is "Ware"  // this is also a comment
```

---

## Booleans

The two boolean values are `true` and `false`.

```
flag is true

if flag is true,
    show "flag is on"
end
```

---

## Full Example

A number guessing game written in Ware:

```
// Number guessing game

secret is 7
guess is 0
tries is 0

show "Guess a number between 1 and 10:"

while guess is not secret,
    read guess
    tries is tries + 1

    if guess is smaller than secret,
        show "Too low! Try again:"
    end

    if guess is bigger than secret,
        show "Too high! Try again:"
    end
end

show "You got it in " + tries + " tries!"
```

---

## Quick Reference

| Syntax | What it does |
|---|---|
| `x is 5` | Assign variable |
| `show x` | Print to screen |
| `read x` | Get user input |
| `if ... , ... end` | Conditional |
| `if ... , ... else, ... end` | If / else |
| `while ... , ... end` | While loop |
| `during i, range(n), ... end` | Count loop (1 to n) |
| `function f which has x, ... end` | Define function |
| `f(x)` | Call function |
| `return x` | Return from function |
| `x is "a" and "b" and "c"` | Create list |
| `x[1]` | Access list item (1-indexed) |
| `add to x, "item"` | Append to list |
| `break` | Exit loop |
| `continue` | Skip to next iteration |
| `// comment` | Comment |
| `true` / `false` | Boolean values |
| `is` | Equals |
| `is not` | Not equals |
| `is bigger than` | Greater than |
| `is smaller than` | Less than |
| `and` / `or` / `not` | Logic operators |
| `+` `-` `*` `/` | Math operators |
