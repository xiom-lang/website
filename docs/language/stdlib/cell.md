# Cell Module

Interior mutability types: `Cell` (for `Copy` types) and `RefCell` (with runtime borrow checking).

```
use axiom.cell;
```

## Cell

### `Cell[T]`
A container that provides interior mutability for `Copy` types through `get` and `set` operations. No runtime borrow checking is needed.

```
pub type Cell[T] = { value: T; }
```

### `Cell.new(value)`
Creates a new `Cell` containing the given value.

```
pub fn Cell.new[T](value: T) -> Cell[T];
```

### `Cell.get(self)`
Returns a copy of the contained value. Only works with `Copy` types.

```
pub fn Cell.get[T](self) -> T;
```

### `Cell.set(self, value)`
Sets the contained value to `value`.

```
pub fn Cell.set[T](self, value: T);
```

### `Cell.replace(self, value)`
Replaces the contained value with `value`, returning the old value.

```
pub fn Cell.replace[T](self, value: T) -> T;
```

### `Cell.swap(self, other)`
Swaps the values of two `Cell` instances.

```
pub fn Cell.swap[T](self, other: &Cell[T]);
```

## RefCell

### `RefCell[T]`
A container that provides interior mutability through runtime borrow checking. Panics if borrowing rules are violated.

```
pub type RefCell[T] = { value: T; borrows: Int; }
```

### `RefCell.new(value)`
Creates a new `RefCell` containing the given value.

```
pub fn RefCell.new[T](value: T) -> RefCell[T];
```

### `RefCell.borrow(self)`
Immutably borrows the value. Panics if the value is already mutably borrowed.

```
pub fn RefCell.borrow[T](self) -> Ref[T];
```

### `RefCell.borrow_mut(self)`
Mutably borrows the value. Panics if the value is already borrowed.

```
pub fn RefCell.borrow_mut[T](self) -> RefMut[T];
```

### `RefCell.try_borrow(self)`
Attempts to immutably borrow the value, returning `None` if it is already mutably borrowed.

```
pub fn RefCell.try_borrow[T](self) -> Option<Ref[T]>;
```

### `RefCell.try_borrow_mut(self)`
Attempts to mutably borrow the value, returning `None` if it is already borrowed.

```
pub fn RefCell.try_borrow_mut[T](self) -> Option<RefMut[T]>;
```

### `RefCell.replace(self, value)`
Replaces the contained value with `value`, returning the old value.

```
pub fn RefCell.replace[T](self, value: T) -> T;
```

## Ref

### `Ref[T]`
An immutable borrow guard for `RefCell`. The borrow is released when the `Ref` is dropped.

```
pub type Ref[T] = { cell: RefCell[T]; }
```

### `Ref.get(self)`
Returns a copy of the borrowed value.

```
pub fn Ref.get[T](self) -> T;
```

## RefMut

### `RefMut[T]`
A mutable borrow guard for `RefCell`. The borrow is released when the `RefMut` is dropped.

```
pub type RefMut[T] = { cell: RefCell[T]; }
```

### `RefMut.get(self)`
Returns a copy of the borrowed value.

```
pub fn RefMut.get[T](self) -> T;
```

### `RefMut.set(self, value)`
Sets the borrowed value to `value`.

```
pub fn RefMut.set[T](self, value: T);
```
