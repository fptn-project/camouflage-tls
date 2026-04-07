/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#pragma once

#include <memory>
#include <optional>
#include <variant>

#include "browsers/google_chrome.h"
#include "browsers/yandex_browser.h"
#include "camouflage/tls/browsers/base_browser_builder.h"
#include "camouflage/tls/types.hpp"

namespace camouflage::tls {

class Builder {
 public:
  static Builder Create() { return Builder(); }

  Builder& GoogleChrome(google_chrome::Version version =
                            google_chrome::Version::kV_146_0_7680_178);

  Builder& YandexBrowser(yandex_browser::Version version =
                             yandex_browser::Version::kV_26_3_0_2182);

  Builder& SetSNI(const SNI& sni);

  Builder& SetSessionId(const SessionId& session_id);

  Builder& SetSessionId(const std::string& session_id_hex);

  HandshakeRecordOptional Generate();

 protected:
  Builder() = default;

 private:
  std::unique_ptr<BaseBrowserBuilder> current_builder_;
  std::variant<google_chrome::Version, yandex_browser::Version>
      current_version_;
  std::optional<SessionId> session_id_;
  std::optional<SNI> sni_;
};
}  // namespace camouflage::tls
