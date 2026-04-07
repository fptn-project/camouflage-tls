/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#pragma once

#include <vector>

#include <gtest/gtest.h>  // NOLINT(build/include_order)

#include "camouflage/tls/types.hpp"

namespace camouflage::tls {

template <typename BuilderType>
void CheckSni(BuilderType& builder, const std::size_t sni_length) {
  const SNI test_sni(sni_length, 'a');

  auto handshake = builder.GenerateHandshake(test_sni);

  // CHECK SNI
  ASSERT_TRUE(handshake.has_value())
      << "Failed to generate handshake for SNI length: " << sni_length;
  EXPECT_EQ(handshake->sni, test_sni)
      << "SNI mismatch for length: " << sni_length;
  std::vector<uint8_t> sni_bytes(test_sni.begin(), test_sni.end());
  auto sni_pos = std::ranges::search(handshake->handshake_packet, sni_bytes);
  EXPECT_FALSE(sni_pos.empty())
      << "SNI not found in binary packet for length: " << sni_length;

  // CHECK SESSION ID
  auto sid_pos =
      std::ranges::search(handshake->handshake_packet, handshake->session_id);
  EXPECT_FALSE(sid_pos.empty())
      << "Session ID not found in binary packet for length: " << sni_length;

  // CHECK RANDOM
  auto random_pos =
      std::ranges::search(handshake->handshake_packet, handshake->random);
  EXPECT_FALSE(random_pos.empty())
      << "Random not found in binary packet for length: " << sni_length;
}

template <typename BuilderType>
void CheckSniAndSessionId(BuilderType& builder, const std::size_t sni_length) {
  const SNI test_sni(sni_length, 'a');

  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_int_distribution<> dis(0, 255);

  SessionId custom_session_id;
  for (auto& byte : custom_session_id) {
    byte = static_cast<uint8_t>(dis(gen));
  }

  auto handshake = builder.GenerateHandshake(test_sni, custom_session_id);

  // CHECK SNI
  ASSERT_TRUE(handshake.has_value())
      << "Failed to generate handshake for SNI length: " << sni_length;
  EXPECT_EQ(handshake->sni, test_sni)
      << "SNI mismatch for length: " << sni_length;
  std::vector<uint8_t> sni_bytes(test_sni.begin(), test_sni.end());
  auto sni_pos = std::ranges::search(handshake->handshake_packet, sni_bytes);
  EXPECT_FALSE(sni_pos.empty())
      << "SNI not found in binary packet for length: " << sni_length;

  // CHECK SESSION ID
  EXPECT_EQ(handshake->session_id, custom_session_id)
      << "Session ID mismatch for length: " << sni_length;

  auto sid_pos =
      std::ranges::search(handshake->handshake_packet, handshake->session_id);
  EXPECT_FALSE(sid_pos.empty())
      << "Session ID not found in binary packet for length: " << sni_length;

  // CHECK RANDOM
  auto random_pos =
      std::ranges::search(handshake->handshake_packet, handshake->random);
  EXPECT_FALSE(random_pos.empty())
      << "Random not found in binary packet for length: " << sni_length;
}

template <typename BuilderType>
void CheckBrowser(BuilderType& builder, const HandshakeData& handshake_data) {
  for (const auto& [sni_length, records] : handshake_data) {
    for (int i = 0; i < 100; i++) {
      CheckSni(builder, sni_length);
      CheckSniAndSessionId(builder, sni_length);
    }
  }
}

}  // namespace camouflage::tls
