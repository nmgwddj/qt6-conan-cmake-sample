## Build Qt project with Conan

This project demonstrates the simplest implementation of using Conan to manage Qt's third-party dependencies. You can create Qt applications on various platforms based on this project.

### Configuration

```bash
cmake -Bbuild -DCMAKE_BUILD_TYPE=Debug
```

### Build

```bash
cmake --build build --config Debug
```

### Run

On macOS

```bash
open ./build/bin/QtWithConan.app
```
