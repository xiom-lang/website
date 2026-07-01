# Memory Model

AXIOM uses **ownership semantics** for memory management. There is no garbage collector. Memory is freed when the owning binding leaves its scope.

The model uses **lexical scope borrowing** — simpler than Rust's lifetime system while providing the same core safety guarantee: use-after-free and double-free are compile errors.

## Ownership Rules

| Rule | Description |
|------|-------------|
| **Single Owner** | Every value has exactly one owner at any time. Assignment moves ownership. |
| **Scope Lifetime** | A value is freed when its owning binding leaves scope. No GC, no manual free. |
| **Read Borrow (`&T`)** | Multiple simultaneous read borrows allowed. No mutation during active read borrows. |
| **Write Borrow (`&mut T`)** | Exactly one write borrow at a time. No other borrows active simultaneously. |
| **Explicit Clone** | Duplicating a value requires `.clone()`. No implicit deep copy. |
| **Move On Call** | Passing a value to a function moves ownership unless the parameter is a borrow. |

## Borrowing

Borrows expire at the end of the block or statement they are created in. You can see when a borrow ends by looking at the braces.

```axiom
fn consume(data: Vec[Int]) { }          // takes ownership
fn read_only(data: &Vec[Int]) { }       // read borrow
fn mutate(data: &mut Vec[Int]) { }      // write borrow

let v = [1, 2, 3]
read_only(&v)        // borrow, v still valid
mutate(&mut v)       // write borrow, v still valid  
consume(v)           // move — v no longer usable here
// read_only(&v)     // COMPILE ERROR: v was moved
```

## What the Model Cannot Handle

Borrows **cannot** be stored in struct fields. Borrows **cannot** be returned from functions. These patterns require owned types or explicit cloning.

This is a constraint, not a bug — it is the design. Patterns that require escaping borrows are solved with owned types instead.

## Clone

Use `.clone()` to explicitly duplicate a value:

```axiom
let a = Vec.new()
a.push(1)

let b = a.clone()    // explicit deep copy
// a is still valid — ownership was not moved

consume(a)           // a is moved
// b is still valid  — it was cloned, not moved
```

Types with `derive[Clone]` get automatic clone implementations. Manual `clone()` methods can be written for types that need custom duplication logic.

## Move Semantics

Passing a value to a function moves ownership:

```axiom
fn take(v: Vec[Int]) {
  // v is owned here — freed at end of scope
}

let data = [1, 2, 3]
take(data)           // ownership moves to take()
// data is no longer valid here
```

Use borrows when you don't need ownership:

```axiom
fn inspect(v: &Vec[Int]) {
  // read-only access — caller retains ownership
}

let data = [1, 2, 3]
inspect(&data)       // borrow — data still valid
inspect(&data)       // can borrow again
```

## Unsafe Blocks

Raw pointer arithmetic and C interop that cannot be verified by the compiler are permitted only inside explicit `unsafe { }` blocks.

```axiom
unsafe {
  let raw: *Int = some_c_function()
  let value = *raw   // dereference — programmer guarantees validity
}
```

The `unsafe` keyword is a declaration that the programmer takes responsibility for memory safety inside that scope. Unsafe blocks are visible in code review and audits. They cannot be hidden.

## Differences from Rust

| | AXIOM | Rust |
|---|-------|------|
| Lifetime annotations | None | Required for non-trivial cases |
| Borrow scope | Lexical (visible by braces) | NLL (non-lexical lifetimes) |
| Borrow in structs | Not allowed | Allowed with lifetime parameters |
| Return borrows | Not allowed | Allowed with lifetime parameters |
| Learning curve | Moderate | Steep |
