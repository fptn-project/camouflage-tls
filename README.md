# Camouflage-TLS

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![C++20](https://img.shields.io/badge/C++-20-blue.svg)](https://en.cppreference.com/w/cpp/20)

Camouflage-TLS is a C++ library for generating authentic TLS ClientHello messages reconstructed from real browser
traffic.

The library operates on real browser TLS handshakes and reuses previously recorded handshake data.  
It generates new ClientHello messages by preserving the structure of an original handshake while selectively modifying
fields such as `SNI`, `SESSION_ID`, and `RANDOM`.

The library supports generating ClientHello messages with SNI lengths between `4` and `64` bytes.

## Features

- Generates TLS ClientHello messages based on real browser handshakes
- Produces ClientHello messages matching Chrome, Firefox, Yandex Browser, and Safari fingerprints
- Includes a Python tool (`tools/capture-handshake.py`) to automatically launch a browser and extract TLS ClientHello
  data as C++ code

## Supported Versions

| Browser                                                                                                                                                   | Version        |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------|----------------|
| <img src="https://static.wikia.nocookie.net/logopedia/images/0/0d/Firefox_logo_2019.svg/revision/latest?cb=20191026110452" height="15"/> Firefox          | 149.0          |
| <img src="https://static.wikia.nocookie.net/logopedia/images/b/b4/Google_Chrome_2022.svg/revision/latest?cb=20220405034021" height="15"/> Google Chrome   | 147.0.7727.56  |
| <img src="https://static.wikia.nocookie.net/logopedia/images/b/b4/Google_Chrome_2022.svg/revision/latest?cb=20220405034021" height="15"/> Google Chrome   | 146.0.7680.178 |
| <img src="https://static.wikia.nocookie.net/logopedia/images/b/b4/Google_Chrome_2022.svg/revision/latest?cb=20220405034021" height="15"/> Google Chrome   | 145.0.7632.46  |
| <img src="https://static.wikia.nocookie.net/logopedia/images/7/73/Safari_2025.png/revision/latest?cb=20251104204856" height="15"/> Safari                 | 26.4           |
| <img src="https://static.wikia.nocookie.net/logopedia/images/8/89/Yandex_Browser_2024.svg/revision/latest?cb=20240723101636" height="15"/> Yandex Browser | 26.3.3.881     |
| <img src="https://static.wikia.nocookie.net/logopedia/images/8/89/Yandex_Browser_2024.svg/revision/latest?cb=20240723101636" height="15"/> Yandex Browser | 25.8.3.828     |
| <img src="https://static.wikia.nocookie.net/logopedia/images/8/89/Yandex_Browser_2024.svg/revision/latest?cb=20240723101636" height="15"/> Yandex Browser | 24.12.0.1772   |

## Quick Start

```cpp

#include <iostream>

#include "camouflage/tls/builder.hpp"

int main() {
  const auto h1 = camouflage::tls::Builder::Create()
                      .GoogleChrome()
                      .SetSNI("t.me")
                      .Generate();
  std::cerr << "H1 has value " << h1.has_value() << std::endl;
  if (h1.has_value()) {
    std::cerr << "H1 size: " << h1->handshake_packet_size << " bytes"
              << std::endl;
  }

  const auto h2 =
      camouflage::tls::Builder::Create()
          .GoogleChrome(
              camouflage::tls::google_chrome::Version::kV_147_0_7727_56)
          .SetSNI("google.com")
          .Generate();
  std::cerr << "H2 has value " << h2.has_value() << std::endl;
  if (h2.has_value()) {
    std::cerr << "H2 size: " << h2->handshake_packet_size << " bytes"
              << std::endl;
  }

  const auto h3 =
      camouflage::tls::Builder::Create()
          .YandexBrowser(
              camouflage::tls::yandex_browser::Version::kV_26_3_3_881)
          .SetSNI("example.com")
          .SetSessionId("12345678901234567890123456789012")
          .Generate();
  std::cerr << "H3 has value " << h3.has_value() << std::endl;
  if (h3.has_value()) {
    std::cerr << "H3 size: " << h3->handshake_packet_size << " bytes"
              << std::endl;
  }

  const auto h4 = camouflage::tls::Builder::Create()
                      .Firefox(camouflage::tls::firefox::Version::kV_149_0)
                      .SetSNI("test.com")
                      .Generate();
  std::cerr << "H4 has value " << h4.has_value() << std::endl;
  if (h4.has_value()) {
    std::cerr << "H4 size: " << h4->handshake_packet_size << " bytes"
              << std::endl;
  }

  return 0;
}
```

# BUILDING

```bash
conan install . --output-folder=build --build=missing  -s compiler.cppstd=20 --settings build_type=Release

cd build

# Linux & macOS only
cmake .. -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release
# Windows only
cmake .. -G "Visual Studio 17 2022" -DCMAKE_TOOLCHAIN_FILE="conan_toolchain.cmake" -DCMAKE_BUILD_TYPE=Release

cmake --build . --config Release
ctest
```
