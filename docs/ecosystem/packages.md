<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# XIOM -- Package Guide

## Creating a Package

```
mypackage/
|-- package.xi          # manifest
|-- src/
|   `-- lib.xi          # library code
|-- bindings/
|   `-- lib.xiom-bind  # FFI binding spec (if C FFI)
`-- tests/
    `-- test.xi         # test suite
```

### package.xi

```xiom
package {
  name: "mypackage"
  version: "0.1.0"
  description: "My XIOM package"
  authors: ["Your Name"]
  deps: {
    "xiom-std": "0.1.0"
  }
}
```

### Publishing

```powershell
# Start registry
python registry/server.py

# Publish
xiom pkg publish

# Install
xiom pkg install mypackage
```

## Package Naming Convention

- `xiom:xyz` -- First-party official packages
- `community:xyz` -- Community packages
- No prefix -- Third-party packages

## FFI Binding Template

Create `bindings/lib.xiom-bind`:

```
library "libname" {
  fn func_name(param: type) -> return_type;
}
```

Generate:
```powershell
xiom ffigen bindings/lib.xiom-bind > src/extern.xi
```
