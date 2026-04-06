# Camouflage-TLS

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![C++17](https://img.shields.io/badge/C++-17-blue.svg)](https://en.cppreference.com/w/cpp/17)

C++ library for generating realistic browser TLS handshakes through captured and reproduced handshake patterns from major browsers.

## Features

- Real browser TLS handshake capture and reproduction
- Support for Chrome, Firefox, Yandex Browser, and Safari
- Domain-specific handshake patterns based on SNI length
- Builder pattern API for easy integration
- Extensible architecture for custom handshake data

## Quick Start

```cpp
#include <iostream>

#include "camouflage/tls/builder.hpp"


int main() {
  const auto handshake_chrome =
      camouflage::tls::Builder::create().GoogleChrome()->GenerateHandshake(
          "google.com");

  std::cerr << "Result: " << handshake_chrome.has_value() << std::endl;

  const auto session_id =
      camouflage::tls::ToSessionId("12345678901234567890123456789012");
  const auto handshake_yandex =
      camouflage::tls::Builder::create().GoogleChrome()->GenerateHandshake(
          "google.com", session_id.value());
  std::cerr << "Result: " << handshake_yandex.has_value() << std::endl;

  return 0;
}
```
