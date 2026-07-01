# AXIOM — Package Guide

## Creating a Package

```
mypackage/
├── package.ax          # manifest
├── src/
│   └── lib.ax          # library code
├── bindings/
│   └── lib.axiom-bind  # FFI binding spec (if C FFI)
└── tests/
    └── test.ax         # test suite
```

### package.ax

```axiom
package {
  name: "mypackage"
  version: "0.1.0"
  description: "My AXIOM package"
  authors: ["Your Name"]
  deps: {
    "axiom-std": "0.1.0"
  }
}
```

### Publishing

```powershell
# Start registry
python registry/server.py

# Publish
axiom pkg publish

# Install
axiom pkg install mypackage
```

## Package Naming Convention

- `axiom:xyz` — First-party official packages
- `community:xyz` — Community packages
- No prefix — Third-party packages

## FFI Binding Template

Create `bindings/lib.axiom-bind`:

```
library "libname" {
  fn func_name(param: type) -> return_type;
}
```

Generate:
```powershell
axiom ffigen bindings/lib.axiom-bind > src/extern.ax
```
