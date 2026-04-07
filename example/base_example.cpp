/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#include <iostream>

#include "camouflage/tls/builder.hpp"

int main() {
  auto h1 = camouflage::tls::Builder::Create()
                .GoogleChrome()
                .SetSNI("t.me")
                .Generate();
  std::cerr << "H1 has value " << h1.has_value() << std::endl;
  if (h1.has_value()) {
    std::cerr << "H1 size: " << h1->handshake_packet.size() << " bytes"
              << std::endl;
  }

  auto h2 = camouflage::tls::Builder::Create()
                .GoogleChrome(
                    camouflage::tls::google_chrome::Version::kV_146_0_7680_178)
                .SetSNI("google.com")
                .Generate();
  std::cerr << "H2 has value " << h2.has_value() << std::endl;
  if (h2.has_value()) {
    std::cerr << "H2 size: " << h2->handshake_packet.size() << " bytes"
              << std::endl;
  }

  auto h3 = camouflage::tls::Builder::Create()
                .YandexBrowser(
                    camouflage::tls::yandex_browser::Version::kV_26_3_0_2182)
                .SetSNI("example.com")
                .SetSessionId("12345678901234567890123456789012")
                .Generate();
  std::cerr << "H3 has value " << h3.has_value() << std::endl;
  if (h3.has_value()) {
    std::cerr << "H3 size: " << h3->handshake_packet.size() << " bytes"
              << std::endl;
  }

  auto h4 = camouflage::tls::Builder::Create()
                .Firefox(camouflage::tls::firefox::Version::kV_149_0)
                .SetSNI("test.com")
                .Generate();
  std::cerr << "H4 has value " << h4.has_value() << std::endl;
  if (h4.has_value()) {
    std::cerr << "H4 size: " << h4->handshake_packet.size() << " bytes"
              << std::endl;
  }

  return 0;
}
