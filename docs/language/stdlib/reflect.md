# Reflect Module

Comptime and runtime type introspection: type IDs, type information, field metadata, and downcasting.

```
use xiom.reflect;
```

## TypeId

### `TypeId`
A unique identifier for a type.

```
pub type TypeId = { id: Int; } derive[Eq, Clone, Hash]
```

### `TypeId.of()`
Returns the `TypeId` for a given type.

```
pub fn TypeId.of[T]() -> TypeId;
```

## Any Interface

### `Any`
The trait for types that support runtime type identification.

```
pub interface Any {
    fn type_id(self) -> TypeId;
}
```

### `Any.type_id(self)`
Returns the `TypeId` of `self`.

## Type Queries

### `type_name()`
Returns the name of type `T` as a string.

```
pub fn type_name[T]() -> Str;
```

### `type_size()`
Returns the size in bytes of type `T`.

```
pub fn type_size[T]() -> Int;
```

### `type_align()`
Returns the alignment in bytes of type `T`.

```
pub fn type_align[T]() -> Int;
```

## Downcasting

### `downcast_ref(value, T)|
Attempts to downcast a `dyn Any` reference to a concrete type `T`. Returns `None` if the type does not match.

```
pub fn downcast_ref[T: Any](value: &dyn Any) -> Option<&T>;
```

### `downcast_mut(value, T)|
Attempts to downcast a `dyn Any` mutable reference to a concrete type `T`. Returns `None` if the type does not match.

```
pub fn downcast_mut[T: Any](value: &mut dyn Any) -> Option<&mut T>;
```

## TypeInfo

### `TypeInfo`
Detailed metadata about a type, including its name, size, alignment, kind, fields, variants, and derives.

```
pub type TypeInfo = {
    name: Str;
    size: Int;
    align: Int;
    kind: Int;
    fields: Vec<FieldInfo>;
    variants: Vec<Str>;
    derives: Vec<Str>;
} derive[Clone]
```

`kind` values: `0` = primitive, `1` = struct, `2` = enum, `3` = interface.

### `FieldInfo`
Metadata about a single field within a struct type.

```
pub type FieldInfo = {
    name: Str;
    type_name: Str;
    offset: Int;
} derive[Clone]
```

### `reflect_type()`
Returns the full `TypeInfo` for type `T`.

```
pub fn reflect_type[T]() -> TypeInfo;
```

### `type_info_by_name(name)|
Looks up a type by name and returns its `TypeInfo`, or `None` if the type is not found.

```
pub fn type_info_by_name(name: Str) -> Option<TypeInfo>;
```

### `all_types()`
Returns `TypeInfo` for all types defined in the current package.

```
pub fn all_types() -> Vec<TypeInfo>;
```
