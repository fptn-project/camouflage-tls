/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#include "browsers/google_chrome/google_chrome_builder.hpp"

#include "camouflage/tls/types.hpp"
#include "camouflage/tls/utils.hpp"

namespace camouflage::tls {
extern const HandshakeData kBrowserChrome_146_0_7680_178;
}

namespace camouflage::tls {

GoogleChromeBrowserBuilder::GoogleChromeBrowserBuilder(
    google_chrome::Version version)
    : version_(version), handshake_data_(nullptr) {
  if (version_ == google_chrome::Version::kV_146_0_7680_178) {
    handshake_data_ = &kBrowserChrome_146_0_7680_178;
  }
}

HandshakeRecordOptional GoogleChromeBrowserBuilder::GenerateHandshake(
    const SNI& sni) {
  auto handshake = FindRandomRecordBySni(sni, handshake_data_);
  if (handshake.has_value() && handshake->GenerateNewRandom() &&
      handshake->ReplaceSni(sni) && handshake->GenerateNewSessionId()) {
    return handshake;
  }
  return std::nullopt;
}

HandshakeRecordOptional GoogleChromeBrowserBuilder::GenerateHandshake(
    const SNI& sni, const SessionId& session_id) {
  auto handshake = GenerateHandshake(sni);
  if (handshake.has_value() && handshake->ReplaceSessionId(session_id)) {
    return handshake;
  }
  return std::nullopt;
}

}  // namespace camouflage::tls
