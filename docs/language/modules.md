# Module System

## Declaring Modules

A module is a named namespace. Every source file begins with a module declaration. A module hierarchy corresponds to the directory structure.

```xiom
module math.vector

// Everything declared here is in the math.vector namespace.
```

## Importing

```xiom
use math.vector              // imports the module — access as vector.Vec3
use math.vector.Vec3         // imports one type — access as Vec3
use math.vector.Vec3 as V3   // alias — access as V3
use math.vector.*            // imports all public symbols (discouraged)
```

## Visibility

All declarations are private to their module by default. The `pub` keyword makes a declaration visible to other modules. There is no `protected` or `friend` visibility.

```xiom
pub type Vec3 = {
  x: Float32;
  y: Float32;
  z: Float32;
} derive[Eq, Clone, Display]

fn internal_helper() {  // private to this module
  // ...
}
```

## Method Declarations

Methods on a type are declared using the `TypeName.methodName` syntax. The receiver (`self`) is synthesized implicitly by the compiler — it does not appear in the parameter list.

```xiom
pub fn Vec3.dot(other: &Vec3) -> Float32 {
  return x * other.x + y * other.y + z * other.z;
  // self is implicit — fields accessed directly
}

pub fn Vec3.set_x(value: Float32) {
  x = value;   // self is &mut Vec3 — field mutation detected
}
```

The compiler infers the receiver type:
- Methods that do not mutate fields get `self: &Self` (read borrow)
- Methods that mutate fields get `self: &mut Self` (write borrow)
- If a field is mutated anywhere in the method body, the receiver is `&mut Self`

## Method Dispatch

Methods can be called on any value of the type:

```xiom
let v = Vec3{ x: 1.0, y: 2.0, z: 3.0 };
let d = v.dot(&other);
```

Methods are dispatched structurally — any type with matching method signatures satisfies the interface, regardless of module boundaries.

## Package Manifest

Packages are defined by a `package.xi` manifest file at the project root. Dependencies are resolved at build time. Version pinning uses semantic versioning.

```xiom
// package.xi
package {
  name:    "myproject"
  version: "1.0.0"
  deps: {
    "xiom-std": "0.4.*"
    "xiom-net":  "0.2.1"
  }
}
```

## Package Manager

The package manager resolves dependencies from the [XIOM package registry](https://gitea.example.com/xiom-lang/registry):

```bash
xiom get xiom-std     # fetch and compile a dependency
xiom build             # build the current package
xiom run               # build and run
```

For the full ecosystem, see the [Ecosystem page](https://xiom-lang.org/ecosystem.html).

## File Organization

```
myproject/
├── package.xi              # package manifest
├── src/
│   ├── main.xi             # entry point
│   └── lib.xi              # library code
└── deps/                   # resolved dependencies (generated)
```

## Standard Library

The standard library ships with the compiler in `stdlib/xiom/`. 40 modules covering core types, I/O, collections, text, math, concurrency, networking, memory, system, utilities, crypto, and testing.

For the full stdlib reference with every type, function, and signature, see the [Standard Library Reference](stdlib.md).

### Quick Index

| Category | Modules |
|----------|---------|
| **Foundation** | `core`, `error`, `char` |
| **I/O** | `io`, `path` |
| **Data Structures** | `collections`, `array` |
| **Text** | `string`, `encoding` |
| **Numeric** | `math`, `num`, `cmp` |
| **Concurrency** | `async`, `thread`, `sync` |
| **Network** | `net` |
| **Memory** | `mem`, `ptr`, `alloc`, `rc` |
| **System** | `os`, `env`, `time` |
| **Utilities** | `iter`, `convert`, `cell`, `fmt`, `hash` |
| **Performance** | `simd` |
| **Security** | `crypto`, `compress`, `rand`, `regex` |
| **Tooling** | `test`, `bench`, `log`, `contracts`, `serialize`, `reflect` |
| **Interop** | `ffi` |

### Importing

```xiom
use xiom.collections     // import the module
use xiom.collections.Vec  // import one type
use xiom.io               // import I/O functions
```
