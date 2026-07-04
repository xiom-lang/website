# Collections Library

The `collections` module provides general-purpose data structures: dynamic arrays, hash maps, hash sets, linked lists, queues, stacks, double-ended queues, sorted maps, sorted sets, and slice utilities.

```
use xiom.collections;
```

---

## Vec

A contiguous growable array type, backed by a heap-allocated buffer with length and capacity tracking. `Vec` provides amortized O(1) push, O(1) pop, and O(1) index access.

```xiom
type Vec[T] = {
  data: *T;
  len: Int;
  cap: Int;
}
```

### `Vec.new()`
Creates a new, empty `Vec` with no initial allocation.

```xiom
fn Vec.new[T]() -> Vec[T];
```

### `Vec.with_capacity(cap)`
Creates a new, empty `Vec` pre-allocated with space for at least `cap` elements.

```xiom
fn Vec.with_capacity[T](cap: Int) -> Vec[T];
```

### `Vec.push(value)`
Appends a value to the end of the vector, growing the backing buffer if necessary.

```xiom
fn Vec.push[T](value: T);
```

### `Vec.pop()`
Removes and returns the last element. Returns `None` if the vector is empty.

```xiom
fn Vec.pop[T]() -> Option[T];
```

### `Vec.get(index)`
Returns a reference to the element at `index`, or `None` if the index is out of bounds.

```xiom
fn Vec.get[T](index: Int) -> Option[&T];
```

### `Vec.len()`
Returns the number of elements in the vector.

```xiom
fn Vec.len[T]() -> Int;
```

### `Vec.is_empty()`
Returns true if the vector contains no elements.

```xiom
fn Vec.is_empty[T]() -> Bool;
```

### `Vec.clear()`
Removes all elements from the vector; the backing buffer is not freed.

```xiom
fn Vec.clear[T]();
```

### `Vec.insert(index, value)`
Inserts `value` at position `index`, shifting all subsequent elements to the right.

```xiom
fn Vec.insert[T](index: Int, value: T);
```

### `Vec.remove(index)`
Removes and returns the element at position `index`, shifting all subsequent elements to the left. Returns `None` if the index is out of bounds.

```xiom
fn Vec.remove[T](index: Int) -> Option[T];
```

### `Vec.first()`
Returns a reference to the first element, or `None` if the vector is empty.

```xiom
fn Vec.first[T]() -> Option[&T];
```

### `Vec.last()`
Returns a reference to the last element, or `None` if the vector is empty.

```xiom
fn Vec.last[T]() -> Option[&T];
```

### `Vec.set(index, value)`
Overwrites the element at `index` with `value`. Panics if the index is out of bounds.

```xiom
fn Vec.set[T](index: Int, value: T);
```

---

## Map

A hash map from keys of type `K` to values of type `V`. Provides average O(1) insert, lookup, and remove.

```xiom
type Map[K, V] = {}
```

### `Map.new()`
Creates a new, empty hash map.

```xiom
fn Map.new[K, V]() -> Map[K, V];
```

### `Map.insert(key, value)`
Inserts a key-value pair into the map. If the key already exists, the value is replaced.

```xiom
fn Map.insert[K, V](key: K, value: V);
```

### `Map.get(key)`
Returns a reference to the value associated with `key`, or `None` if the key is not present.

```xiom
fn Map.get[K, V](key: &K) -> Option[&V];
```

### `Map.remove(key)`
Removes the key-value pair for `key` and returns the value. Returns `None` if the key is not present.

```xiom
fn Map.remove[K, V](key: &K) -> Option[V];
```

### `Map.contains(key)`
Returns true if the map contains an entry for `key`.

```xiom
fn Map.contains[K, V](key: &K) -> Bool;
```

### `Map.len()`
Returns the number of key-value pairs in the map.

```xiom
fn Map.len[K, V]() -> Int;
```

### `Map.keys()`
Returns a `Vec[K]` containing all keys in the map. The order is not guaranteed.

```xiom
fn Map.keys[K, V]() -> Vec[K];
```

### `Map.values()`
Returns a `Vec[V]` containing all values in the map. The order is not guaranteed.

```xiom
fn Map.values[K, V]() -> Vec[V];
```

### `Map.clear()`
Removes all key-value pairs from the map.

```xiom
fn Map.clear[K, V]();
```

---

## Set

A hash set of values of type `T`. Provides average O(1) insert, lookup, and remove.

```xiom
type Set[T] = {}
```

### `Set.new()`
Creates a new, empty hash set.

```xiom
fn Set.new[T]() -> Set[T];
```

### `Set.insert(value)`
Inserts a value into the set. If the value was already present, the set is unchanged.

```xiom
fn Set.insert[T](value: T);
```

### `Set.remove(value)`
Removes `value` from the set. No-op if the value is not present.

```xiom
fn Set.remove[T](value: &T);
```

### `Set.contains(value)`
Returns true if the set contains `value`.

```xiom
fn Set.contains[T](value: &T) -> Bool;
```

### `Set.len()`
Returns the number of elements in the set.

```xiom
fn Set.len[T]() -> Int;
```

### `Set.union(other)`
Returns a new set containing all elements from `self` and `other`.

```xiom
fn Set.union[T](other: &Set[T]) -> Set[T];
```

### `Set.intersection(other)`
Returns a new set containing elements present in both `self` and `other`.

```xiom
fn Set.intersection[T](other: &Set[T]) -> Set[T];
```

### `Set.difference(other)`
Returns a new set containing elements present in `self` but not in `other`.

```xiom
fn Set.difference[T](other: &Set[T]) -> Set[T];
```

---

## LinkedList

A doubly-linked list providing O(1) insertion and removal at both ends.

```xiom
type LinkedList[T] = {}
```

### `LinkedList.new()`
Creates a new, empty linked list.

```xiom
fn LinkedList.new[T]() -> LinkedList[T];
```

### `LinkedList.push_front(value)`
Prepends `value` to the front of the list.

```xiom
fn LinkedList.push_front[T](value: T);
```

### `LinkedList.push_back(value)`
Appends `value` to the end of the list.

```xiom
fn LinkedList.push_back[T](value: T);
```

### `LinkedList.pop_front()`
Removes and returns the first element. Returns `None` if the list is empty.

```xiom
fn LinkedList.pop_front[T]() -> Option[T];
```

### `LinkedList.pop_back()`
Removes and returns the last element. Returns `None` if the list is empty.

```xiom
fn LinkedList.pop_back[T]() -> Option[T];
```

### `LinkedList.len()`
Returns the number of elements in the list.

```xiom
fn LinkedList.len[T]() -> Int;
```

### `LinkedList.is_empty()`
Returns true if the list contains no elements.

```xiom
fn LinkedList.is_empty[T]() -> Bool;
```

---

## Queue

A first-in-first-out (FIFO) queue.

```xiom
type Queue[T] = {}
```

### `Queue.new()`
Creates a new, empty queue.

```xiom
fn Queue.new[T]() -> Queue[T];
```

### `Queue.enqueue(value)`
Adds `value` to the back of the queue.

```xiom
fn Queue.enqueue[T](value: T);
```

### `Queue.dequeue()`
Removes and returns the element at the front of the queue. Returns `None` if the queue is empty.

```xiom
fn Queue.dequeue[T]() -> Option[T];
```

### `Queue.peek()`
Returns a reference to the front element without removing it. Returns `None` if the queue is empty.

```xiom
fn Queue.peek[T]() -> Option[&T];
```

### `Queue.len()`
Returns the number of elements in the queue.

```xiom
fn Queue.len[T]() -> Int;
```

### `Queue.is_empty()`
Returns true if the queue contains no elements.

```xiom
fn Queue.is_empty[T]() -> Bool;
```

---

## Stack

A last-in-first-out (LIFO) stack.

```xiom
type Stack[T] = {}
```

### `Stack.new()`
Creates a new, empty stack.

```xiom
fn Stack.new[T]() -> Stack[T];
```

### `Stack.push(value)`
Pushes `value` onto the top of the stack.

```xiom
fn Stack.push[T](value: T);
```

### `Stack.pop()`
Removes and returns the top element. Returns `None` if the stack is empty.

```xiom
fn Stack.pop[T]() -> Option[T];
```

### `Stack.peek()`
Returns a reference to the top element without removing it. Returns `None` if the stack is empty.

```xiom
fn Stack.peek[T]() -> Option[&T];
```

### `Stack.len()`
Returns the number of elements on the stack.

```xiom
fn Stack.len[T]() -> Int;
```

### `Stack.is_empty()`
Returns true if the stack contains no elements.

```xiom
fn Stack.is_empty[T]() -> Bool;
```

---

## VecDeque

A double-ended queue implemented with a growable ring buffer. Provides O(1) push and pop at both ends.

```xiom
type VecDeque[T] = { data: Vec[T]; head: Int; tail: Int; }
```

### `VecDeque.new()`
Creates a new, empty `VecDeque`.

```xiom
fn VecDeque[T].new() -> VecDeque[T];
```

### `VecDeque.with_capacity(cap)`
Creates a new, empty `VecDeque` pre-allocated with space for at least `cap` elements.

```xiom
fn VecDeque[T].with_capacity(cap: Int) -> VecDeque[T];
```

### `VecDeque.push_front(value)`
Prepends `value` to the front of the deque.

```xiom
fn VecDeque[T].push_front(self, value: T);
```

### `VecDeque.push_back(value)`
Appends `value` to the back of the deque.

```xiom
fn VecDeque[T].push_back(self, value: T);
```

### `VecDeque.pop_front()`
Removes and returns the front element. Returns `None` if the deque is empty.

```xiom
fn VecDeque[T].pop_front(self) -> Option[T];
```

### `VecDeque.pop_back()`
Removes and returns the back element. Returns `None` if the deque is empty.

```xiom
fn VecDeque[T].pop_back(self) -> Option[T];
```

### `VecDeque.front()`
Returns a reference to the front element without removing it. Returns `None` if the deque is empty.

```xiom
fn VecDeque[T].front(self) -> Option[&T];
```

### `VecDeque.back()`
Returns a reference to the back element without removing it. Returns `None` if the deque is empty.

```xiom
fn VecDeque[T].back(self) -> Option[&T];
```

### `VecDeque.len()`
Returns the number of elements in the deque.

```xiom
fn VecDeque[T].len(self) -> Int;
```

---

## BTreeMap

A sorted map implemented as a B-tree. Keys must implement `Ord`. Provides O(log n) insert, lookup, and remove, with ordered iteration.

```xiom
type BTreeMap[K: Ord, V] = { ... }
```

### `BTreeMap.new()`
Creates a new, empty `BTreeMap`.

```xiom
fn BTreeMap[K: Ord, V].new() -> BTreeMap[K, V];
```

### `BTreeMap.insert(key, value)`
Inserts a key-value pair. If the key already existed, the old value is returned wrapped in `Some`; otherwise `None` is returned.

```xiom
fn BTreeMap[K: Ord, V].insert(self, key: K, value: V) -> Option[V];
```

### `BTreeMap.get(key)`
Returns a reference to the value associated with `key`, or `None` if the key is not present.

```xiom
fn BTreeMap[K: Ord, V].get(self, key: &K) -> Option[&V];
```

### `BTreeMap.remove(key)`
Removes the key-value pair for `key` and returns the value. Returns `None` if the key is not present.

```xiom
fn BTreeMap[K: Ord, V].remove(self, key: &K) -> Option[V];
```

### `BTreeMap.contains_key(key)`
Returns true if the map contains an entry for `key`.

```xiom
fn BTreeMap[K: Ord, V].contains_key(self, key: &K) -> Bool;
```

### `BTreeMap.first_entry()`
Returns the smallest key-value pair in the map, or `None` if the map is empty.

```xiom
fn BTreeMap[K: Ord, V].first_entry(self) -> Option[(K, V)];
```

### `BTreeMap.last_entry()`
Returns the largest key-value pair in the map, or `None` if the map is empty.

```xiom
fn BTreeMap[K: Ord, V].last_entry(self) -> Option[(K, V)];
```

### `BTreeMap.len()`
Returns the number of key-value pairs in the map.

```xiom
fn BTreeMap[K: Ord, V].len(self) -> Int;
```

---

## BTreeSet

A sorted set implemented as a B-tree. Values must implement `Ord`. Provides O(log n) insert, lookup, and remove, with ordered iteration.

```xiom
type BTreeSet[T: Ord] = { ... }
```

### `BTreeSet.new()`
Creates a new, empty `BTreeSet`.

```xiom
fn BTreeSet[T: Ord].new() -> BTreeSet[T];
```

### `BTreeSet.insert(value)`
Inserts a value. Returns true if the value was newly inserted, false if it was already present.

```xiom
fn BTreeSet[T: Ord].insert(self, value: T) -> Bool;
```

### `BTreeSet.remove(value)`
Removes a value. Returns true if the value was present and removed, false otherwise.

```xiom
fn BTreeSet[T: Ord].remove(self, value: &T) -> Bool;
```

### `BTreeSet.contains(value)`
Returns true if the set contains `value`.

```xiom
fn BTreeSet[T: Ord].contains(self, value: &T) -> Bool;
```

### `BTreeSet.first()`
Returns a reference to the smallest element, or `None` if the set is empty.

```xiom
fn BTreeSet[T: Ord].first(self) -> Option<&T>;
```

### `BTreeSet.last()`
Returns a reference to the largest element, or `None` if the set is empty.

```xiom
fn BTreeSet[T: Ord].last(self) -> Option<&T>;
```

### `BTreeSet.len()`
Returns the number of elements in the set.

```xiom
fn BTreeSet[T: Ord].len(self) -> Int;
```

---

## Slice Methods

Utility methods on `Slice[T]`, a borrowed view into a contiguous sequence of elements.

### `Slice.len()`
Returns the number of elements in the slice.

```xiom
fn Slice[T].len(self) -> Int;
```

### `Slice.is_empty()`
Returns true if the slice contains no elements.

```xiom
fn Slice[T].is_empty(self) -> Bool;
```

### `Slice.first()`
Returns a reference to the first element, or `None` if the slice is empty.

```xiom
fn Slice[T].first(self) -> Option<&T>;
```

### `Slice.last()`
Returns a reference to the last element, or `None` if the slice is empty.

```xiom
fn Slice[T].last(self) -> Option<&T>;
```

### `Slice.get(index)`
Returns a reference to the element at `index`, or `None` if out of bounds.

```xiom
fn Slice[T].get(self, index: Int) -> Option<&T>;
```
