/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#pragma once

#include <algorithm>
#include <array>
#include <cstdint>
#include <optional>
#include <random>
#include <unordered_map>
#include <vector>

namespace camouflage::tls {

using SNI = std::string;
using SessionId = std::array<std::uint8_t, 32>;
using RandomBytes = std::array<std::uint8_t, 32>;
using Data = std::vector<uint8_t>;

inline std::optional<camouflage::tls::SessionId> ToSessionId(
    const std::string& str) {
  constexpr auto kSessionIdSize = camouflage::tls::SessionId{}.size();
  if (str.size() != kSessionIdSize) {
    return std::nullopt;
  }
  camouflage::tls::SessionId sid;
  std::copy_n(str.begin(), kSessionIdSize, sid.begin());
  return sid;
}

struct HandshakeRecord {
  SNI sni;
  SessionId session_id;
  RandomBytes random;
  Data handshake_packet;

  bool ReplaceSni(const SNI& new_sni) {
    if (new_sni.size() != sni.size()) {
      return false;
    }

    auto it = std::ranges::search(handshake_packet, sni);
    if (it.empty()) {
      return false;
    }

    if (it.begin() + new_sni.size() > handshake_packet.end()) {
      return false;
    }

    const auto result = std::ranges::copy(new_sni, it.begin());
    if (result.in != new_sni.end()) {
      return false;
    }

    this->sni = new_sni;
    return true;
  }

  bool GenerateNewRandom() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, 255);

    // replace random
    RandomBytes new_random;
    for (auto& byte : new_random) {
      byte = static_cast<std::uint8_t>(dis(gen));
    }
    auto it = std::ranges::search(handshake_packet, random);
    if (it.empty()) {
      return false;
    }
    const auto result = std::ranges::copy(new_random, it.begin());
    if (result.in != new_random.end()) {
      return false;
    }
    this->random = new_random;
    return true;
  }

  bool GenerateNewSessionId() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, 255);

    // replace session_id
    SessionId new_session_id;
    for (auto& byte : new_session_id) {
      byte = static_cast<std::uint8_t>(dis(gen));
    }
    auto it = std::ranges::search(handshake_packet, session_id);
    if (it.empty()) {
      return false;
    }
    return ReplaceSessionId(new_session_id);
  }

  bool ReplaceSessionId(const SessionId& new_session_id) {
    auto it = std::ranges::search(handshake_packet, session_id);
    if (it.empty()) {
      return false;
    }
    if (it.begin() + new_session_id.size() > handshake_packet.end()) {
      return false;
    }
    const auto result = std::ranges::copy(new_session_id, it.begin());
    if (result.in != new_session_id.end()) {
      return false;
    }
    this->session_id = new_session_id;
    return true;
  }
};

using HandshakeData = std::unordered_map<size_t, std::vector<HandshakeRecord>>;

using HandshakeRecordOptional = std::optional<HandshakeRecord>;

}  // namespace camouflage::tls
