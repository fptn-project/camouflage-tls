/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#pragma once

#include <memory>
#include <optional>
#include <variant>

#include "camouflage/tls/browsers/base_browser_builder.hpp"
#include "camouflage/tls/browsers/firefox.hpp"
#include "camouflage/tls/browsers/google_chrome.hpp"
#include "camouflage/tls/browsers/safari.hpp"
#include "camouflage/tls/browsers/yandex_browser.hpp"
#include "camouflage/tls/types.hpp"

namespace camouflage::tls {

using Version = std::variant<firefox::Version,
    google_chrome::Version,
    safari::Version,
    yandex_browser::Version>;

class Builder {
 public:
  static Builder Create() { return Builder(); }

  Builder& Firefox(firefox::Version version = firefox::Version::kV_149_0);

  Builder& GoogleChrome(google_chrome::Version version =
                            google_chrome::Version::kV_147_0_7727_56);

  Builder& Safari(safari::Version = safari::Version::kV_26_4);

  Builder& YandexBrowser(
      yandex_browser::Version version = yandex_browser::Version::kV_26_3_3_881);

  Builder& SetSNI(const SNI& sni);

  Builder& SetSessionId(const SessionId& session_id);

  Builder& SetSessionId(const std::string& session_id_hex);

  HandshakeRecordOptional Generate();

 protected:
  Builder() = default;

 private:
  std::unique_ptr<BaseBrowserBuilder> builder_;
  Version version_;
  std::optional<SessionId> session_id_;
  std::optional<SNI> sni_;
};
}  // namespace camouflage::tls
