# `axiom.net` — Networking

Provides networking primitives including TCP, UDP, HTTP, DNS resolution, and URL parsing.

```axiom
use axiom.net;
```

---

## Types

### `NetError`

A networking error carrying a human-readable message and a numeric error code.

```axiom
pub type NetError = { message: Str; code: Int; }
```

### `HttpMethod`

An enum representing standard HTTP request methods.

```axiom
pub type HttpMethod = enum { GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS }
```

### `HttpResponse`

The response from an HTTP request, containing the status code and response body as a string.

```axiom
pub type HttpResponse = { status: Int; body: Str; } derive[Clone]
```

### `UrlParts`

The result of parsing a URL into its constituent components.

```axiom
pub type UrlParts = { scheme: Str; host: Str; port: Int; path: Str; query: Str; fragment: Str; }
```

---

## TCP

### `tcp_connect(host, port)`

Opens a TCP connection to the given host and port. Returns a `TcpStream` on success.

```axiom
pub fn tcp_connect(host: Str, port: Int) -> Result[TcpStream, NetError]
```

### `tcp_listen(host, port)`

Binds a TCP listener to the given host and port, accepting incoming connections. Returns a `TcpListener` on success.

```axiom
pub fn tcp_listen(host: Str, port: Int) -> Result[TcpListener, NetError]
```

### `TcpStream`

A connected TCP stream that can be read from and written to.

```axiom
pub type TcpStream = { fd: Int; } derive[Clone]
```

### `TcpStream.read(self, buf)`

Reads data from the TCP stream into the provided byte buffer. Returns the number of bytes read.

```axiom
pub fn TcpStream.read(self, buf: &mut Vec[UInt8]) -> Result[Int, NetError]
```

### `TcpStream.write(self, data)`

Writes the provided byte buffer to the TCP stream. Returns the number of bytes written.

```axiom
pub fn TcpStream.write(self, data: &Vec[UInt8]) -> Result[Int, NetError]
```

### `TcpStream.close(self)`

Closes the TCP stream, releasing the underlying socket descriptor.

```axiom
pub fn TcpStream.close(self) -> Result[Unit, NetError]
```

### `TcpListener`

A TCP socket listener that accepts incoming connections.

```axiom
pub type TcpListener = { fd: Int; } derive[Clone]
```

### `TcpListener.accept(self)`

Blocks until a new TCP connection arrives. Returns a tuple of `(TcpStream, Str)` containing the connected stream and the remote address.

```axiom
pub fn TcpListener.accept(self) -> Result[(TcpStream, Str), NetError]
```

---

## HTTP

### `http_get(url)`

Performs an HTTP GET request to the specified URL. Returns the response including status code and body.

```axiom
pub fn http_get(url: Str) -> Result[HttpResponse, NetError]
```

### `http_post(url, body)`

Performs an HTTP POST request to the specified URL with the given string body. Returns the response including status code and body.

```axiom
pub fn http_post(url: Str, body: Str) -> Result[HttpResponse, NetError]
```

---

## UDP

### `udp_bind(host, port)`

Binds a UDP socket to the given host and port. Returns a `UdpSocket` for sending and receiving datagrams.

```axiom
fn udp_bind(host: Str, port: Int) -> Result[UdpSocket, NetError]
```

### `UdpSocket`

A UDP socket bound to a local address for connectionless datagram communication.

```axiom
pub type UdpSocket = { fd: Int; }
```

### `UdpSocket.send_to(self, data, addr, port)`

Sends a datagram to the specified remote address and port. Returns the number of bytes sent.

```axiom
pub fn UdpSocket.send_to(self, data: &Vec[UInt8], addr: Str, port: Int) -> Result[Int, NetError]
```

### `UdpSocket.recv_from(self, buf)`

Receives a datagram into the provided buffer. Returns a tuple of `(bytes_read, source_addr, source_port)`.

```axiom
pub fn UdpSocket.recv_from(self, buf: &mut Vec[UInt8]) -> Result[(Int, Str, Int), NetError]
```

### `UdpSocket.close(self)`

Closes the UDP socket, releasing the underlying socket descriptor.

```axiom
pub fn UdpSocket.close(self) -> Result[Unit, NetError]
```

---

## DNS

### `resolve_host(hostname)`

Resolves a hostname to a list of IP address strings. Returns any addresses found.

```axiom
fn resolve_host(hostname: Str) -> Result[Vec[Str], NetError]
```

### `local_addr(port)`

Resolves the local IP address that would be used to connect to the given port. Useful for determining the machine's outward-facing address.

```axiom
fn local_addr(port: Int) -> Result[Str, NetError]
```

---

## URL Parsing

### `parse_url(url)`

Parses a URL string into its components (scheme, host, port, path, query, fragment). Returns a `UrlParts` struct on success.

```axiom
fn parse_url(url: Str) -> Result[UrlParts, NetError]
```
