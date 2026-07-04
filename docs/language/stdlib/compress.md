# Compression Module

Compression algorithms: Gzip, Zlib/Deflate, Brotli, LZ4, and Snappy, with format detection utilities.

```
use xiom.compress;
```

## Compressor Trait

### `Compressor`
The trait for types that can compress and decompress data.

```
pub interface Compressor {
    fn compress(self, data: &Vec[UInt8]) -> Result<Vec[UInt8], Str>;
    fn decompress(self, data: &Vec[UInt8]) -> Result<Vec[UInt8], Str>;
}
```

### `Compressor.compress(self, data)`
Compresses the input data.

### `Compressor.decompress(self, data)`
Decompresses the input data.

## Gzip

### `GzipCompressor`
A gzip compressor with configurable compression level (0 = none, 1 = fast, 9 = best).

```
pub type GzipCompressor = { level: Int; }
```

### `GzipCompressor.new()`
Creates a new `GzipCompressor` with default compression level.

```
pub fn GzipCompressor.new() -> GzipCompressor;
```

### `GzipCompressor.with_level(level)`
Creates a new `GzipCompressor` with a specific compression level (0–9).

```
pub fn GzipCompressor.with_level(level: Int) -> GzipCompressor;
```

### `gzip_compress(data)`
Compresses data using gzip with default level.

```
pub fn gzip_compress(data: &Vec[UInt8]) -> Result<Vec[UInt8], Str>;
```

### `gzip_decompress(data)`
Decompresses gzip-compressed data.

```
pub fn gzip_decompress(data: &Vec[UInt8]) -> Result<Vec[UInt8], Str>;
```

### `gzip_compress_level(data, level)`
Compresses data using gzip with a specific compression level (0–9).

```
pub fn gzip_compress_level(data: &Vec[UInt8], level: Int) -> Result<Vec[UInt8], Str>;
```

## Deflate

### `deflate_compress(data)`
Compresses data using Deflate with default level.

```
pub fn deflate_compress(data: &Vec[UInt8]) -> Result<Vec[UInt8], Str>;
```

### `deflate_decompress(data)`
Decompresses Deflate-compressed data.

```
pub fn deflate_decompress(data: &Vec[UInt8]) -> Result<Vec[UInt8], Str>;
```

### `deflate_compress_level(data, level)`
Compresses data using Deflate with a specific compression level.

```
pub fn deflate_compress_level(data: &Vec[UInt8], level: Int) -> Result<Vec[UInt8], Str>;
```

## Zlib

### `zlib_compress(data)`
Compresses data using Zlib with default level.

```
pub fn zlib_compress(data: &Vec[UInt8]) -> Result<Vec[UInt8], Str>;
```

### `zlib_decompress(data)`
Decompresses Zlib-compressed data.

```
pub fn zlib_decompress(data: &Vec[UInt8]) -> Result<Vec[UInt8], Str>;
```

### `zlib_compress_level(data, level)`
Compresses data using Zlib with a specific compression level.

```
pub fn zlib_compress_level(data: &Vec[UInt8], level: Int) -> Result<Vec[UInt8], Str>;
```

## Brotli

### `brotli_compress(data)`
Compresses data using Brotli with default quality.

```
pub fn brotli_compress(data: &Vec[UInt8]) -> Result<Vec[UInt8], Str>;
```

### `brotli_decompress(data)`
Decompresses Brotli-compressed data.

```
pub fn brotli_decompress(data: &Vec[UInt8]) -> Result<Vec[UInt8], Str>;
```

### `brotli_compress_level(data, quality)`
Compresses data using Brotli with a specific quality level (0–11).

```
pub fn brotli_compress_level(data: &Vec[UInt8], quality: Int) -> Result<Vec[UInt8], Str>;
```

## LZ4

### `lz4_compress(data)`
Compresses data using LZ4 (very fast, moderate compression ratio).

```
pub fn lz4_compress(data: &Vec[UInt8]) -> Result<Vec[UInt8], Str>;
```

### `lz4_decompress(data)`
Decompresses LZ4-compressed data.

```
pub fn lz4_decompress(data: &Vec[UInt8]) -> Result<Vec[UInt8], Str>;
```

## Snappy

### `snappy_compress(data)`
Compresses data using Snappy (Google's fast compression algorithm).

```
pub fn snappy_compress(data: &Vec[UInt8]) -> Result<Vec[UInt8], Str>;
```

### `snappy_decompress(data)`
Decompresses Snappy-compressed data.

```
pub fn snappy_decompress(data: &Vec[UInt8]) -> Result<Vec[UInt8], Str>;
```

## Utility

### `compression_ratio(original, compressed)`
Calculates the compression ratio as `original / compressed`.

```
pub fn compression_ratio(original: Int, compressed: Int) -> Float64;
```

### `is_compressed(data)`
Heuristically determines whether the data appears to be compressed.

```
pub fn is_compressed(data: &Vec[UInt8]) -> Bool;
```

### `detect_format(data)|
Detects the compression format from the data's magic bytes. Returns `"gzip"`, `"zlib"`, `"brotli"`, or `"unknown"`.

```
pub fn detect_format(data: &Vec[UInt8]) -> Str;
```
