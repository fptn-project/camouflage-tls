/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#pragma once

#include <array>
#include <string>
#include <unordered_map>
#include <vector>

namespace camouflage::tls {

struct HandhshakeRecord {
  std::string sni;
  std::array<std::uint8_t, 32> session_id;
  std::array<std::uint8_t, 32> random;
  std::vector<std::uint8_t> handshake_packet;
};

using HandshakeData =
    std::unordered_map<std::size_t, std::vector<HandhshakeRecord>>;

}  // namespace camouflage::tls
