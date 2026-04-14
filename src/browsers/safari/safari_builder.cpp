/*=============================================================================
Copyright (c) 2025 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#include "browsers/safari/safari_builder.hpp"

#include "camouflage/tls/browsers/safari.hpp"
#include "camouflage/tls/types.hpp"
#include "camouflage/tls/utils.hpp"
#include "versions/safari_26_4/safari_26_4.hpp"

namespace camouflage::tls {

SafariBuilder::SafariBuilder(safari::Version version)
    : version_(version), handshake_data_(nullptr) {
  handshake_data_ = nullptr;
  if (version_ == safari::Version::kV_26_4) {
    handshake_data_ = &kBrowserSafari_26_4;
  }
}

HandshakeRecordOptional SafariBuilder::GenerateHandshake(const SNI& sni) {
  return camouflage::tls::GenerateHandshake(handshake_data_, sni);
}

HandshakeRecordOptional SafariBuilder::GenerateHandshake(
    const SNI& sni, const SessionId& session_id) {
  return camouflage::tls::GenerateHandshake(handshake_data_, sni, session_id);
}

}  // namespace camouflage::tls
