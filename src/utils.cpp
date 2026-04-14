/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#include "camouflage/tls/utils.hpp"

#include <algorithm>
#include <array>
#include <optional>
#include <random>

#include "camouflage/tls/types.hpp"

namespace {
void GenerateRandomBytes(std::uint8_t* bytes, std::size_t size) {
  static std::random_device rd;
  static std::mt19937 gen(rd());
  std::uniform_int_distribution<> dis(0, 255);
  for (size_t i = 0; i < size; ++i) {
    bytes[i] = static_cast<std::uint8_t>(dis(gen));
  }
}

std::optional<camouflage::tls::HandshakeRecord> GetRandomHandshakeRecord(
    const camouflage::tls::HandshakeData* data, const std::string& sni) {
  if (!data || sni.empty()) {
    return std::nullopt;
  }

  const std::size_t sni_len = sni.size();
  for (std::size_t i = 0; i < data->entry_count; ++i) {
    if (data->entries[i].sni_length != sni_len) {
      continue;
    }
    const auto& entry = data->entries[i];
    if (entry.record_count == 0) {
      continue;
    }

    static std::random_device rd;
    static std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, entry.record_count - 1);
    const std::size_t idx = dis(gen);
    return entry.records[idx];
  }
  return std::nullopt;
}

// Замена данных в пакете
template <size_t N>
bool ReplaceInPacket(std::uint8_t* packet,
    std::size_t packet_size,
    const std::uint8_t (&old_data)[N],
    const std::array<std::uint8_t, N>& new_data) {
  auto it = std::search(packet, packet + packet_size, old_data, old_data + N);
  if (it == packet + packet_size) {
    return false;
  }
  std::copy_n(new_data.data(), N, it);
  return true;
}

bool ReplaceSNIInPacket(std::uint8_t* packet,
    std::size_t packet_size,
    const std::string& old_sni,
    const std::string& new_sni) {
  // 0x16 (Handshake) | length(3) | 0x01 (ClientHello) | length(3)
  // | version(2) | random(32) | session_id_len(1) | session_id
  // | cipher_len(2) | ciphers | comp_len(1) | comp_methods
  // | extensions_len(2) | extensions...

  std::size_t offset = 0;

  // Skip record header (5 bytes: type(1) + version(2) + length(2))
  if (packet_size < 5 || packet[0] != 0x16) {
    return false;
  }
  offset = 5;

  // Skip handshake header (4 bytes: type(1) + length(3))
  if (offset + 4 > packet_size || packet[offset] != 0x01) {
    return false;
  }
  offset += 4;

  // Skip version (2 bytes)
  offset += 2;

  // Skip random (32 bytes)
  offset += 32;

  // Skip session_id
  if (offset >= packet_size) {
    return false;
  }
  const std::uint8_t session_id_len = packet[offset];
  offset += 1 + session_id_len;

  // Skip ciphers
  if (offset + 2 > packet_size) {
    return false;
  }
  const std::uint16_t cipher_len = (packet[offset] << 8) | packet[offset + 1];
  offset += 2 + cipher_len;

  // Skip compression methods
  if (offset >= packet_size) {
    return false;
  }
  const std::uint8_t comp_len = packet[offset];
  offset += 1 + comp_len;

  // Get extensions length
  if (offset + 2 > packet_size) {
    return false;
  }
  const std::uint16_t extensions_len =
      (packet[offset] << 8) | packet[offset + 1];
  offset += 2;

  const std::size_t extensions_end = offset + extensions_len;

  // Find SNI extension (type = 0)
  while (offset + 4 <= extensions_end && offset + 4 <= packet_size) {
    const std::uint16_t ext_type = (packet[offset] << 8) | packet[offset + 1];
    const std::uint16_t ext_len =
        (packet[offset + 2] << 8) | packet[offset + 3];
    offset += 4;

    if (ext_type == 0) {  // SNI extension
      if (offset + 2 > packet_size) {
        return false;
      }

      // Skip server_name_list length
      offset += 2;

      // Skip name_type (1 byte, should be 0)
      if (offset >= packet_size) {
        return false;
      }
      offset += 1;

      // Get hostname length
      if (offset + 2 > packet_size) {
        return false;
      }
      const std::uint16_t hostname_len =
          (packet[offset] << 8) | packet[offset + 1];
      offset += 2;

      // Now we're at the hostname
      if (offset + hostname_len <= packet_size &&
          hostname_len == old_sni.size()) {
        // Replace with new SNI (must be same length!)
        std::copy_n(new_sni.data(), new_sni.size(), packet + offset);
      }
      break;
    }
    offset += ext_len;
  }
  return true;
}

}  // namespace

namespace camouflage::tls {

HandshakeRecordOptional GenerateHandshake(
    const HandshakeData* data, const std::string& sni) {
  std::array<std::uint8_t, TLS_SESSION_ID_SIZE> session_id;
  GenerateRandomBytes(session_id.data(), 32);
  return GenerateHandshake(data, sni, session_id);
}

HandshakeRecordOptional GenerateHandshake(const HandshakeData* data,
    const std::string& sni,
    const SessionId& session_id) {
  if (!data || sni.empty() || sni.size() > TLS_MAX_SNI_LEN - 1) {
    return std::nullopt;
  }

  const auto record_opt = GetRandomHandshakeRecord(data, sni);
  if (!record_opt.has_value()) {
    return std::nullopt;
  }

  HandshakeRecord record = record_opt.value();

  // Change session_id
  ReplaceInPacket(record.handshake_packet, record.handshake_packet_size,
      record.session_id, session_id);
  std::copy_n(session_id.data(), 32, record.session_id);

  // Change random
  std::array<std::uint8_t, 32> new_random;
  GenerateRandomBytes(new_random.data(), 32);
  ReplaceInPacket(record.handshake_packet, record.handshake_packet_size,
      record.random, new_random);
  std::copy_n(new_random.data(), 32, record.random);

  // Change sni
  ReplaceSNIInPacket(record.handshake_packet, record.handshake_packet_size,
      record_opt->sni, sni);
  std::memset(record.sni, '\0', TLS_MAX_SNI_LEN);
  std::copy_n(sni.data(), sni.size(), record.sni);

  return record;
}

}  // namespace camouflage::tls