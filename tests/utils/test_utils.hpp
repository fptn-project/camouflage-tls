/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#pragma once

#include <algorithm>
#include <array>
#include <cstring>
#include <random>
#include <string>

#include <gtest/gtest.h>  // NOLINT(build/include_order)

#include "camouflage/tls/types.hpp"

namespace camouflage::tls {

inline bool CompareSNI(const char* actual, const std::string& expected) {
  return std::strncmp(actual, expected.c_str(), expected.length()) == 0;
}

inline std::array<std::uint8_t, TLS_MAX_SNI_LEN> StringToSNIArray(
    const std::string& sni) {
  std::array<std::uint8_t, TLS_MAX_SNI_LEN> result{};
  std::ranges::copy(sni, result.begin());
  return result;
}

template <typename T, std::size_t N>
bool FindInPacket(const std::uint8_t* packet,
    std::size_t packet_size,
    const std::array<T, N>& pattern) {
  std::size_t actual_len = 0;
  while (actual_len < N && pattern[actual_len] != 0) {
    actual_len++;
  }

  if (packet_size < actual_len) {
    return false;
  }

  return std::search(packet, packet + packet_size, pattern.begin(),
             pattern.begin() + actual_len) != (packet + packet_size);
}

template <typename BuilderType>
void CheckSni(BuilderType& builder, const std::size_t sni_length) {
  const std::string test_sni(sni_length, 'a');

  auto handshake = builder.GenerateHandshake(test_sni);

  // CHECK SNI
  ASSERT_TRUE(handshake.has_value())
      << "Failed to generate handshake for SNI length: " << sni_length;

  EXPECT_TRUE(CompareSNI(handshake->sni, test_sni))
      << "SNI mismatch for length: " << sni_length;

  auto sni_array = StringToSNIArray(test_sni);

  EXPECT_TRUE(FindInPacket(
      handshake->handshake_packet, handshake->handshake_packet_size, sni_array))
      << "SNI not found in binary packet for length: " << sni_length;

  // CHECK SESSION ID
  std::array<std::uint8_t, TLS_SESSION_ID_SIZE> session_id;
  std::copy(handshake->session_id, handshake->session_id + TLS_SESSION_ID_SIZE,
      session_id.begin());

  EXPECT_TRUE(FindInPacket(handshake->handshake_packet,
      handshake->handshake_packet_size, session_id))
      << "Session ID not found in binary packet for length: " << sni_length;

  // CHECK RANDOM
  std::array<std::uint8_t, TLS_RANDOM_SIZE> random;
  std::copy(
      handshake->random, handshake->random + TLS_RANDOM_SIZE, random.begin());

  EXPECT_TRUE(FindInPacket(
      handshake->handshake_packet, handshake->handshake_packet_size, random))
      << "Random not found in binary packet for length: " << sni_length;
}

template <typename BuilderType>
void CheckSniAndSessionId(BuilderType& builder, const std::size_t sni_length) {
  const std::string test_sni(sni_length, 'a');

  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_int_distribution<> dis(0, 255);

  std::array<std::uint8_t, TLS_SESSION_ID_SIZE> custom_session_id;
  for (auto& byte : custom_session_id) {
    byte = static_cast<std::uint8_t>(dis(gen));
  }

  auto handshake = builder.GenerateHandshake(test_sni, custom_session_id);

  // CHECK SNI
  ASSERT_TRUE(handshake.has_value())
      << "Failed to generate handshake for SNI length: " << sni_length;

  EXPECT_TRUE(CompareSNI(handshake->sni, test_sni))
      << "SNI mismatch for length: " << sni_length;

  auto sni_array = StringToSNIArray(test_sni);

  EXPECT_TRUE(FindInPacket(
      handshake->handshake_packet, handshake->handshake_packet_size, sni_array))
      << "SNI not found in binary packet for length: " << sni_length;

  // CHECK SESSION ID
  EXPECT_TRUE(std::equal(custom_session_id.begin(), custom_session_id.end(),
      handshake->session_id))
      << "Session ID mismatch for length: " << sni_length;

  EXPECT_TRUE(FindInPacket(handshake->handshake_packet,
      handshake->handshake_packet_size, custom_session_id))
      << "Session ID not found in binary packet for length: " << sni_length;

  // CHECK RANDOM
  std::array<std::uint8_t, TLS_RANDOM_SIZE> random;
  std::copy(
      handshake->random, handshake->random + TLS_RANDOM_SIZE, random.begin());

  EXPECT_TRUE(FindInPacket(
      handshake->handshake_packet, handshake->handshake_packet_size, random))
      << "Random not found in binary packet for length: " << sni_length;
}

template <typename BuilderType>
void CheckBrowser(BuilderType& builder, const HandshakeData& handshake_data) {
  for (std::size_t i = 0; i < handshake_data.entry_count; ++i) {
    const auto& entry = handshake_data.entries[i];
    for (std::size_t iter = 0; iter < 100; ++iter) {
      CheckSni(builder, entry.sni_length);
      CheckSniAndSessionId(builder, entry.sni_length);
    }
  }
}

}  // namespace camouflage::tls
