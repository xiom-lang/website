# AXIOM by Example

> Progressive examples from Hello World to production-ready code.
> Every example compiles. Every example is tested. 21 examples ship with the compiler in `examples/`.

---

## 1. Hello World

```axiom
fn main() -> Int {
  return 42;
}
```

Compile and run:

```bash
cargo run -p axiomc -- --run hello.ax
# exit code: 42
```

The `main()` function returns an exit code. No `print` needed for the simplest case.

---

## 2. Variables & Arithmetic

```axiom
fn main() -> Int {
  let x: Int = 10;
  var y: Float64 = 3.14;
  let z = x * 2;            // type inferred: Int
  return x;
}
```

`let` = immutable. `var` = mutable. Type annotations are optional when the compiler can infer.

---

## 3. Functions

```axiom
fn add(a: Int, b: Int) -> Int {
  return a + b;
}

fn greet(name: Str) -> Str {
  return "Hello, " + name + "!";
}

fn main() -> Int {
  let result = add(10, 20);
  return result;   // 30
}
```

Every parameter must have a type annotation. Return type is required (unless void).

---

## 4. Control Flow — Fibonacci

```axiom
fn fib(n: Int) -> Int
  requires: n >= 0
{
  if n <= 1 { return n; }
  return fib(n - 1) + fib(n - 2);
}

fn main() -> Int {
  return fib(10);   // 55
}
```

`if` / `elif` / `else` — note `elif`, not `else if`. Every `return` ends with `;`.

---

## 5. Structs & Methods — 2D Point

```axiom
type Point = {
  x: Float64;
  y: Float64;
} derive[Eq, Clone, Display]

fn distance(a: &Point, b: &Point) -> Float64 {
  let dx = a.x - b.x;
  let dy = a.y - b.y;
  return dx * dx + dy * dy;
}

fn Point.magnitude() -> Float64 {
  // self is implicit — access fields directly
  return x * x + y * y;
}

fn main() -> Int {
  let p1 = Point{ x: 0.0, y: 0.0 };
  let p2 = Point{ x: 3.0, y: 4.0 };
  let d = distance(&p1, &p2);
  let m = p2.magnitude();   // 25.0
  return 0;
}
```

`derive[Eq, Clone, Display]` — the compiler generates `eq()`, `clone()`, and `to_str()` automatically.

---

## 6. Enums & Pattern Matching

```axiom
enum Option { Some(value: Int), None }

fn describe(opt: Option) -> Str {
  match opt {
    Some(v) => "got " + v.to_str(),
    None    => "nothing",
  }
}

fn main() -> Int {
  let a = describe(Some{ value: 42 });
  let b = describe(None);
  return 0;
}
```

Every `match` must cover all variants. Use `_` as a wildcard. Match arms end with `,`.

---

## 7. Error Handling — Result & ?

```axiom
fn divide_safe(a: Float64, b: Float64) -> Result[Float64, Str] {
  if b == 0.0 {
    return Err("division by zero");
  }
  return Ok(a / b);
}

fn compute(x: Float64, y: Float64) -> Result[Float64, Str] {
  let step1 = divide_safe(x, y)?;    // ? propagates error
  let step2 = divide_safe(step1, 2.0)?;
  return Ok(step2);
}

fn main() -> Int {
  match compute(10.0, 2.0) {
    Ok(result) => result.to_str(),
    Err(msg)   => msg,
  };
  return 0;
}
```

`?` returns the error immediately. Only usable inside functions returning `Result` or `Option`.

---

## 8. Contracts — Divide by Zero Prevention

```axiom
fn divide(a: Float64, b: Float64) -> Float64
  requires: b != 0.0
  ensures:  result * b == a
{
  return a / b;
}

type PositiveInt = {
  value: Int;
  invariant: value > 0;
}

fn main() -> Int {
  let x = divide(10.0, 2.0);   // ok
  // let y = divide(10.0, 0.0); // COMPILE ERROR: contract violated
  return 0;
}
```

Contracts are compiler-enforced. `requires` = caller's responsibility. `ensures` = implementation's responsibility. `invariant` = always true after any mutation.

---

## 9. Ownership & Borrowing

```axiom
fn take_ownership(x: Int) -> Int {
  return x + 1;                    // x freed at end of scope
}

fn read_borrow(x: &Int) -> Int {
  return x + 0;                    // caller retains ownership
}

fn main() -> Int {
  let a = take_ownership(41);      // a = 42
  let b = read_borrow(&a);         // borrow — a still valid
  return a + b;                    // 84
}
```

- `&T` = read borrow (multiple allowed)
- `&mut T` = write borrow (exclusive)
- Passing without `&` = move ownership (old binding invalid)
- `.clone()` = explicit deep copy

---

## 10. Generics — Stack

```axiom
type Stack[T] = {
  items: Vec[T];
  capacity: Int;
  invariant: items.len() <= capacity;
  invariant: capacity > 0;
}

fn Stack.new[T](capacity: Int) -> Result[Stack[T], Str]
  requires: capacity > 0
{
  if capacity <= 0 {
    return Err("capacity must be positive");
  }
  return Ok(Stack[T]{ items: Vec[T].new(), capacity: capacity });
}

fn Stack.push[T](value: T) -> Result[Unit, Str]
  requires: items.len() < capacity
  ensures:  result is Ok => items.len() == items.len()@pre + 1
{
  if items.len() >= capacity {
    return Err("stack is full");
  }
  items.push(value);
  return Ok(());
}

fn Stack.pop[T]() -> Option[T] {
  return items.pop();
}

fn main() -> Result[Unit, Str] {
  var s = Stack.new[Int](3)?;
  s.push(10)?;
  s.push(20)?;
  s.push(30)?;

  match s.push(40) {
    Ok(()) => {},
    Err(e) => io.println(e),
  };

  while !s.is_empty() {
    match s.pop() {
      Some(v) => io.println(v.to_str()),
      None    => {},
    };
  }

  return Ok(());
}
```

Generics + contracts + error handling + ownership — all in one program.

---

## 11. Interfaces — Comparable

```axiom
interface Comparable {
  fn compare(other: &Self) -> Int;
}

type Score = { value: Int; }

fn Score.compare(other: &Score) -> Int {
  if value < other.value { return -1; }
  if value > other.value { return  1; }
  return 0;
}

fn max[T: Comparable](a: T, b: T) -> T {
  if a.compare(&b) > 0 { return a; }
  return b;
}

fn main() -> Int {
  let s1 = Score{ value: 10 };
  let s2 = Score{ value: 20 };
  let winner = max(s1, s2);
  return winner.value;   // 20
}
```

No `implements` keyword. A type satisfies an interface by having the right methods.

---

## 12. Sort with Contracts

```axiom
fn sort(items: &mut Vec[Int])
  ensures: items.is_sorted()
{
  // bubble sort for clarity
  let n = items.len();
  var i = 0;
  while i < n {
    var j = 0;
    while j < n - i - 1 {
      if items.get(j).unwrap() > items.get(j + 1).unwrap() {
        let tmp = items.get(j).unwrap();
        items.set(j, items.get(j + 1).unwrap());
        items.set(j + 1, tmp);
      }
      j = j + 1;
    }
    i = i + 1;
  }
}

fn main() -> Int {
  var nums = [4, 1, 3, 2];
  sort(&mut nums);
  // nums is now [1, 2, 3, 4] — verified by contract
  return 0;
}
```

The `ensures: items.is_sorted()` contract is checked after the function returns. If the sort implementation is wrong, the contract violation surfaces immediately.

---

## 13. C FFI — Calling C from AXIOM

```axiom
extern "C" {
  fn printf(format: *UInt8, ...) -> Int32;
  fn malloc(size: UInt) -> *UInt8;
  fn free(ptr: *UInt8);
}

fn log(message: Str) {
  unsafe {
    printf(message);
  }
}

fn main() -> Int {
  log("Hello from AXIOM via C!\n");
  return 0;
}
```

AXIOM has zero-cost C FFI. Wrap C libraries with safe AXIOM interfaces and contracts.

---

## More Examples

21 example programs ship with the compiler in `examples/`:

| Example | What it demonstrates |
|---------|---------------------|
| `demo_float.ax` | Int + Float64 arithmetic |
| `phase1_ownership.ax` | Ownership and borrowing |
| `phase1_contracts.ax` | Runtime contract guards |
| `phase1_derive.ax` | Derive codegen (Eq, Clone, Display, Hash, Ord) |
| `phase1_enum.ax` | Enum pattern matching |
| `phase1_error.ax` | Result/Option error handling |
| `phase1_generics.ax` | Generics monomorphisation |
| `phase1_interface.ax` | Structural interface satisfaction |
| `phase1_modules.ax` | Module system |
| `phase1_async.ax` | Async/spawn/channel |
| `phase1_full.ax` | Comprehensive multi-feature |
| `stress_derive_50field.ax` | 50-field struct derive stress test |
| `stress_borrow_10level.ax` | 10-level nested borrows |
| `stress_generic_5chain.ax` | 5-level generic chain |
| `stress_float_matrix.ax` | Float matrix multiply |

Compile and run any example:

```bash
cargo run -p axiomc -- --run examples/phase1_full.ax
```
