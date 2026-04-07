/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#include "firefox_builder.h"

#include "camouflage/tls/types.hpp"
#include "camouflage/tls/utils.h"

namespace camouflage::tls {
extern const HandshakeData kBrowserFirefox_149_0;
}

namespace camouflage::tls {

FirefoxBuilder::FirefoxBuilder(firefox::Version version)
    : version_(version), handshake_data_(nullptr) {
  if (version_ == firefox::Version::kV_149_0) {
    handshake_data_ = &kBrowserFirefox_149_0;
  }
}

HandshakeRecordOptional FirefoxBuilder::GenerateHandshake(const SNI& sni) {
  auto handshake = FindRandomRecordBySni(sni, handshake_data_);
  if (handshake.has_value() && handshake->GenerateNewRandom() &&
      handshake->ReplaceSni(sni) && handshake->GenerateNewSessionId()) {
    return handshake;
  }
  return std::nullopt;
}

HandshakeRecordOptional FirefoxBuilder::GenerateHandshake(
    const SNI& sni, const SessionId& session_id) {
  auto handshake = GenerateHandshake(sni);
  if (handshake.has_value() && handshake->ReplaceSessionId(session_id)) {
    return handshake;
  }
  return std::nullopt;
};

}  // namespace camouflage::tls
