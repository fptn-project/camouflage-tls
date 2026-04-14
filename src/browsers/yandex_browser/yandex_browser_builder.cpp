/*=============================================================================
Copyright (c) 2025 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#include "browsers/yandex_browser/yandex_browser_builder.hpp"

#include "camouflage/tls/browsers/yandex_browser.hpp"
#include "camouflage/tls/types.hpp"
#include "camouflage/tls/utils.hpp"
#include "versions/yandex_24_12_0_1772/yandex_24_12_0_1772.hpp"
#include "versions/yandex_25_8_3_828/yandex_25_8_3_828.hpp"
#include "versions/yandex_26_3_3_881/yandex_26_3_3_881.hpp"

namespace camouflage::tls {

YandexBrowserBuilder::YandexBrowserBuilder(yandex_browser::Version version)
    : version_(version), handshake_data_(nullptr) {
  handshake_data_ = nullptr;
  if (version_ == yandex_browser::Version::kV_26_3_3_881) {
    handshake_data_ = &kBrowserYandex_26_3_3_881;
  } else if (version_ == yandex_browser::Version::kV_25_8_3_828) {
    handshake_data_ = &kBrowserYandex_25_8_3_828;
  } else if (version == yandex_browser::Version::kV_24_12_0_1772) {
    handshake_data_ = &kBrowserYandex_24_12_0_1772;
  }
}

HandshakeRecordOptional YandexBrowserBuilder::GenerateHandshake(
    const SNI& sni) {
  return camouflage::tls::GenerateHandshake(handshake_data_, sni);
}

HandshakeRecordOptional YandexBrowserBuilder::GenerateHandshake(
    const SNI& sni, const SessionId& session_id) {
  return camouflage::tls::GenerateHandshake(handshake_data_, sni, session_id);
}

}  // namespace camouflage::tls
