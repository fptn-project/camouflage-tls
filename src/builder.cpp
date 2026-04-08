/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#include "camouflage/tls/builder.hpp"

#include <memory>
#include <string>
#include <utility>

#include "browsers/firefox/firefox_builder.hpp"
#include "browsers/google_chrome/google_chrome_builder.hpp"
#include "browsers/yandex_browser/yandex_browser_builder.hpp"

namespace camouflage::tls {

Builder& Builder::GoogleChrome(google_chrome::Version version) {
  builder_ = std::make_unique<GoogleChromeBrowserBuilder>(version);
  version_ = version;
  return *this;
}

Builder& Builder::YandexBrowser(yandex_browser::Version version) {
  builder_ = std::make_unique<YandexBrowserBuilder>(version);
  version_ = version;
  return *this;
}

Builder& Builder::Firefox(firefox::Version version) {
  builder_ = std::make_unique<FirefoxBuilder>(version);
  version_ = version;
  return *this;
}

Builder& Builder::SetSNI(const SNI& sni) {
  sni_ = sni;
  return *this;
}

Builder& Builder::SetSessionId(const SessionId& session_id) {
  session_id_ = session_id;
  return *this;
}

Builder& Builder::SetSessionId(const std::string& session_id_hex) {
  auto result = ToSessionId(session_id_hex);
  if (result.has_value()) {
    session_id_ = std::move(result.value());
  }
  return *this;
}

HandshakeRecordOptional Builder::Generate() {
  if (!builder_ || !sni_.has_value()) {
    return std::nullopt;
  }
  if (session_id_.has_value()) {
    return builder_->GenerateHandshake(sni_.value(), session_id_.value());
  }
  return builder_->GenerateHandshake(sni_.value());
}

}  // namespace camouflage::tls
