/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

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
