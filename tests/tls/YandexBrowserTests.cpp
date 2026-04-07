/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#include <vector>

#include <gtest/gtest.h>  // NOLINT(build/include_order)

#include "browsers/yandex_browser/yandex_browser_builder.hpp"
#include "camouflage/tls/browsers/yandex_browser.hpp"
#include "camouflage/tls/builder.hpp"
#include "utils/test_utils.hpp"

namespace camouflage::tls {
extern const HandshakeData kBrowserYandex_26_3_0_2182;
}

TEST(YandexBrowserTest_26_3_0_2182, YandexBrowserBuilderTests) {
  camouflage::tls::YandexBrowserBuilder builder(
      camouflage::tls::yandex_browser::Version::kV_26_3_0_2182);
  camouflage::tls::CheckBrowser(
      builder, camouflage::tls::kBrowserYandex_26_3_0_2182);
}

TEST(ChromeBuilderTest_26_3_0_2182, AllSniLengthsFromData100Iterations) {
  const auto& database = camouflage::tls::kBrowserYandex_26_3_0_2182;
  for (const auto& [sni_length, records] : database) {
    for (int iter = 0; iter < 100; iter++) {
      camouflage::tls::SNI test_sni(sni_length, 'a' + (iter % 26));
      auto handshake =
          camouflage::tls::Builder::Create()
              .YandexBrowser(
                  camouflage::tls::yandex_browser::Version::kV_26_3_0_2182)
              .SetSNI(test_sni)
              .Generate();
      ASSERT_TRUE(handshake.has_value())
          << "Failed for SNI length: " << sni_length << ", iter: " << iter;
      EXPECT_EQ(handshake->sni, test_sni)
          << "SNI mismatch for length: " << sni_length;

      std::vector<uint8_t> sni_bytes(test_sni.begin(), test_sni.end());
      auto sni_pos =
          std::ranges::search(handshake->handshake_packet, sni_bytes);
      EXPECT_FALSE(sni_pos.empty())
          << "SNI not found in binary packet for length: " << sni_length;
      auto sid_pos = std::ranges::search(
          handshake->handshake_packet, handshake->session_id);
      EXPECT_FALSE(sid_pos.empty())
          << "Session ID not found for length: " << sni_length;
    }
  }
}

TEST(ChromeBuilderTest_26_3_0_2182, CustomSessionIdFromData100Iterations) {
  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_int_distribution<> dis(0, 255);

  const auto& database = camouflage::tls::kBrowserYandex_26_3_0_2182;
  for (const auto& [sni_length, records] : database) {
    for (int iter = 0; iter < 100; iter++) {
      camouflage::tls::SNI test_sni(sni_length, 'x');

      camouflage::tls::SessionId custom_sid;
      for (auto& byte : custom_sid) {
        byte = static_cast<std::uint8_t>(dis(gen));
      }
      auto handshake =
          camouflage::tls::Builder::Create()
              .YandexBrowser(
                  camouflage::tls::yandex_browser::Version::kV_26_3_0_2182)
              .SetSNI(test_sni)
              .SetSessionId(custom_sid)
              .Generate();
      ASSERT_TRUE(handshake.has_value())
          << "Failed for SNI length: " << sni_length << ", iter: " << iter;
      EXPECT_EQ(handshake->session_id, custom_sid)
          << "Session ID mismatch for length: " << sni_length;
      auto sid_pos =
          std::ranges::search(handshake->handshake_packet, custom_sid);
      EXPECT_FALSE(sid_pos.empty())
          << "Custom Session ID not found in packet for length: " << sni_length;

      std::vector<std::uint8_t> sni_bytes(test_sni.begin(), test_sni.end());
      const auto sni_pos =
          std::ranges::search(handshake->handshake_packet, sni_bytes);
      EXPECT_FALSE(sni_pos.empty())
          << "SNI not found for length: " << sni_length;
    }
  }
}
