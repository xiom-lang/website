# Pattern Matching

XIOM supports structural pattern matching on enums, tuples, and literals via `match`, `if let`, and `while let`.

---

## `match` Expression

The `match` expression is the primary pattern matching construct. It must be exhaustive -- every variant must be covered.

```xiom
match value {
  Some(v) => io.println(v);
  None => io.println("nothing");
}
```

### Multi-line Arms with Braces

When an arm requires multiple statements, use braces:

```xiom
match result {
  Ok(data) => {
    process(data);
    return data.len();
  };
  Err(e) => {
    io.println("error: " + e.message);
    return 0;
  };
}
```

### Match on Integers

```xiom
fn grade(score: Int) -> Str {
  match score {
    0 | 1 | 2 => return "F";
    3 | 4 => return "D";
    5 | 6 => return "C";
    7 | 8 => return "B";
    9 | 10 => return "A";
    _ => return "invalid";
  }
}
```

### Match on Strings

```xiom
fn command(cmd: Str) {
  match cmd {
    "start" => { io.println("starting..."); };
    "stop" => { io.println("stopping..."); };
    "restart" => { io.println("restarting..."); };
    _ => { io.println("unknown command"); };
  }
}
```

---

## Pattern Types

### Literal Patterns

Match exact values: integers, strings, characters, booleans.

```xiom
match x {
  0 => "zero";
  1 => "one";
  _ => "other";
}
```

### Enum Variant Patterns

Match enum constructors, optionally binding inner data.

```xiom
match option {
  Some(v) => v;        // binds `v` to the inner value
  None => default;
}
```

### Struct Patterns

Destructure structs by field:

```xiom
match point {
  Point{x: 0, y: 0} => "origin";
  Point{x, y} => {
    // x and y are bound to the fields
    "somewhere";
  };
}
```

### OR Patterns

Match any of several alternatives with `|`:

```xiom
match code {
  200 | 201 | 204 => "success";
  400 | 404 => "client error";
  500 | 502 | 503 => "server error";
  _ => "unknown";
}
```

### Wildcard Pattern `_`

Matches anything, discarding the value:

```xiom
match result {
  Ok(v) => v;
  _ => default;
}
```

### Binding Pattern `is`

Test if a value matches a pattern without destructuring:

```xiom
if value is Some {
  io.println("value is Some");
}
```

---

## `if let` -- Conditional Destructuring

Binds variables only if the pattern matches:

```xiom
if let Some(v) = maybe_value {
  // `v` is bound here
  io.println(v);
}
```

With else branch:

```xiom
if let Some(user) = find_user(id) {
  io.println("Found: " + user.name);
} else {
  io.println("User not found");
}
```

Nested patterns:

```xiom
if let Ok(Some(data)) = parse_and_lookup() {
  process(data);
}
```

---

## `while let` -- Looping Destructuring

Continues looping while the pattern matches:

```xiom
var iter = make_iterator();
while let Some(item) = iter.next() {
  process(item);
}
```

Example with a channel:

```xiom
while let Ok(msg) = channel.try_recv() {
  handle(msg);
}
```

---

## `?` Operator

The `?` operator is syntactic sugar for `match` with early return on `Err` or `None`:

```xiom
// These are equivalent:
let file = io.read_file(path)?;

// Expands to:
let file = match io.read_file(path) {
  Ok(f) => f;
  Err(e) => return Err(e.into());
};
```

Works with both `Result` and `Option`:

```xiom
fn lookup(key: Str) -> Option[Int] {
  let val = cache.get(&key)?;  // returns None if miss
  return Some(val);
}
```

---

## Exhaustiveness

The compiler checks that `match` expressions cover all possible cases. If a variant is missing, compilation fails with a type error:

```xiom
// ERROR: missing Pattern Green
match color {
  Color.Red => { ... };
  Color.Blue => { ... };
  // Color.Green is not covered!
}
```

Use `_` as a catch-all to satisfy exhaustiveness:

```xiom
match color {
  Color.Red => { ... };
  _ => { ... };          // catches remaining variants
}
```

---

## Guards (Planned)

Pattern guards (`match value { Some(v) if v > 0 => ... }`) are not yet implemented. Use `if` inside the match arm body as a workaround:

```xiom
match value {
  Some(v) => {
    if v > 0 {
      // guarded logic here
    };
  };
  None => {};
}
```

---

## See Also

- [Error Handling](error-handling.md) -- `Result`, `Option`, `?` operator
- [Type System](types.md) -- enum and struct definitions
- [Syntax](syntax.md) -- expression grammar
