/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#include "browsers/google_chrome/google_chrome_builder.hpp"

#include "camouflage/tls/types.hpp"
#include "camouflage/tls/utils.hpp"
#include "versions/chrome_145_0_7632_46/chrome_145_0_7632_46.hpp"
#include "versions/chrome_146_0_7680_178/chrome_146_0_7680_178.hpp"
#include "versions/chrome_147_0_7727_56/chrome_147_0_7727_56.hpp"

namespace camouflage::tls {

GoogleChromeBrowserBuilder::GoogleChromeBrowserBuilder(
    google_chrome::Version version)
    : version_(version), handshake_data_(nullptr) {
  if (version_ == google_chrome::Version::kV_147_0_7727_56) {
    handshake_data_ = &kBrowserChrome_147_0_7727_56;
  } else if (version == google_chrome::Version::kV_146_0_7680_178) {
    handshake_data_ = &kBrowserChrome_146_0_7680_178;
  } else if (version == google_chrome::Version::kV_145_0_7632_46) {
    handshake_data_ = &kBrowserChrome_145_0_7632_46;
  }
}

HandshakeRecordOptional GoogleChromeBrowserBuilder::GenerateHandshake(
    const SNI& sni) {
  return camouflage::tls::GenerateHandshake(handshake_data_, sni);
}

HandshakeRecordOptional GoogleChromeBrowserBuilder::GenerateHandshake(
    const SNI& sni, const SessionId& session_id) {
  return camouflage::tls::GenerateHandshake(handshake_data_, sni, session_id);
}

}  // namespace camouflage::tls
