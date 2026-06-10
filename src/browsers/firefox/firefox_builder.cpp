/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#include "browsers/firefox/firefox_builder.hpp"

#include "camouflage/tls/types.hpp"
#include "camouflage/tls/utils.hpp"
#include "versions/firefox_149_0/firefox_149_0.hpp"
#include "versions/firefox_150_0_3/firefox_150_0_3.hpp"
#include "versions/firefox_151_0_3/firefox_151_0_3.hpp"

namespace camouflage::tls {

FirefoxBuilder::FirefoxBuilder(firefox::Version version)
    : version_(version), handshake_data_(nullptr) {
  handshake_data_ = nullptr;
  if (version_ == firefox::Version::kV_149_0) {
    handshake_data_ = &kBrowserFirefox_149_0;
  } else if (version_ == firefox::Version::kV_150_0_3) {
    handshake_data_ = &kBrowserFirefox_150_0_3;
  } else if (version_ == firefox::Version::kV_151_0_3) {
    handshake_data_ = &kBrowserFirefox_151_0_3;
  }
}

HandshakeRecordOptional FirefoxBuilder::GenerateHandshake(const SNI& sni) {
  return camouflage::tls::GenerateHandshake(handshake_data_, sni);
}

HandshakeRecordOptional FirefoxBuilder::GenerateHandshake(
    const SNI& sni, const SessionId& session_id) {
  return camouflage::tls::GenerateHandshake(handshake_data_, sni, session_id);
}

}  // namespace camouflage::tls
