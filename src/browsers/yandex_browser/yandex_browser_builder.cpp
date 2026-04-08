/*=============================================================================
Copyright (c) 2025 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#include "browsers/yandex_browser/yandex_browser_builder.hpp"

#include "camouflage/tls/browsers/yandex_browser.hpp"
#include "camouflage/tls/types.hpp"
#include "camouflage/tls/utils.hpp"

namespace camouflage::tls {
extern const HandshakeData kBrowserYandex_25_2_0_2118;
extern const HandshakeData kBrowserYandex_26_3_0_2182;
}  // namespace camouflage::tls

namespace camouflage::tls {

YandexBrowserBuilder::YandexBrowserBuilder(yandex_browser::Version version)
    : version_(version), handshake_data_(nullptr) {
  if (version_ == yandex_browser::Version::kV_26_3_0_2182) {
    handshake_data_ = &kBrowserYandex_26_3_0_2182;
  } else if (version_ == yandex_browser::Version::kV_25_2_0_2118) {
    handshake_data_ = &kBrowserYandex_25_2_0_2118;
  }
}

HandshakeRecordOptional YandexBrowserBuilder::GenerateHandshake(
    const SNI& sni) {
  auto handshake = FindRandomRecordBySni(sni, handshake_data_);
  if (handshake.has_value() && handshake->GenerateNewRandom() &&
      handshake->ReplaceSni(sni) && handshake->GenerateNewSessionId()) {
    return handshake;
  }
  return std::nullopt;
}

HandshakeRecordOptional YandexBrowserBuilder::GenerateHandshake(
    const SNI& sni, const SessionId& session_id) {
  auto handshake = GenerateHandshake(sni);
  if (handshake.has_value() && handshake->ReplaceSessionId(session_id)) {
    return handshake;
  }
  return std::nullopt;
}

}  // namespace camouflage::tls
