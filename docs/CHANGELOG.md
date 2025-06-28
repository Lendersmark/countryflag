# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - YYYY-MM-DD

### Added
- **Cache Singleton Behavior**: Global shared cache automatically used by all CountryFlag instances without explicit cache parameter
- **Enhanced Thread Safety**: All cache operations now use threading.Lock for concurrent access protection
- **Cache Key Normalization**: Deterministic cache keys using sorted country names for improved cache hit rates
- **Global Cache Management**: Added `CountryFlag.clear_global_cache()` class method for easy cache reset
- **Cache Hit Accumulation**: Multiple instances now share cache data, improving performance across application lifecycle

### Changed
- **BREAKING**: Cache behavior changed - instances without explicit cache now share global cache instead of having no cache
- **Cache Efficiency**: Improved cache key generation with order-independent normalization
- **Memory Usage**: Reduced memory footprint through singleton cache pattern

### Fixed
- Resolved two failing tests from 1.0.0 release
- Fixed cache fragmentation issues with multiple CountryFlag instances
- Improved cache hit rates through better key normalization

## [1.0.0] - 2025-06-20

### Added
- Major release with full production readiness
- Comprehensive Docker, Kubernetes, and Cloud deployment support
- Performance monitoring with Prometheus and Grafana setups
- High availability and caching improvements
- Fuzzy matching and reverse lookup support in the API
- Multiple output formats: text, JSON, CSV
- Enhanced CLI usability and documentation
- Production-ready deployment examples and configurations
- Custom plugins and integrations examples
- Extensive documentation for deployment and integration

### Fixed
- Correct fuzzy matching threshold handling
- Bug fixes and improved error handling

## [0.2.0] - 2025-06-20

### Added
- Completely restructured package architecture for better maintainability
- Caching system with memory and disk-based implementations
- Support for region/continent grouping of countries
- Comprehensive performance benchmarking
- Asynchronous file operations
- Parallel processing for multiple files
- Interactive CLI mode with auto-completion
- Fuzzy matching for country names
- Property-based testing
- Stress testing with large datasets
- Runtime type checking
- Design by contract pattern implementation
- Improved error handling with custom exceptions
- Performance optimization guide
- Comprehensive documentation

### Changed
- Improved package structure with proper modules
- Enhanced command-line interface with more options
- Better error messages and validation
- More efficient string handling
- Memory-efficient processing for large datasets
- Improved documentation with examples

### Fixed
- Issue with empty input lists
- Issue with non-string inputs
- Memory leaks with large datasets
- Thread safety issues
- Unicode handling problems

## [0.1.2b4] - 2024-01-01

### Added
- Initial public release
- Basic functionality for converting country names to emoji flags
- Simple command-line interface
- Python API with `getflag()` function

[1.0.1]: https://github.com/Lendersmark/countryflag/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/Lendersmark/countryflag/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/Lendersmark/countryflag/compare/v0.1.2b4...v0.2.0
[0.1.2b4]: https://github.com/Lendersmark/countryflag/releases/tag/v0.1.2b4
