/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/
#pragma once

#include "camouflage/tls/browsers/base_browser_builder.hpp"
#include "camouflage/tls/browsers/google_chrome.hpp"
#include "camouflage/tls/browsers/yandex_browser.hpp"
#include "camouflage/tls/types.hpp"

namespace camouflage::tls {

class YandexBrowserBuilder final : public BaseBrowserBuilder {
 public:
  explicit YandexBrowserBuilder(yandex_browser::Version version);

  ~YandexBrowserBuilder() override = default;

  HandshakeRecordOptional GenerateHandshake(const SNI& sni) override;

  HandshakeRecordOptional GenerateHandshake(
      const SNI& sni, const SessionId& session_id) override;

 private:
  const yandex_browser::Version version_;
  const HandshakeData* handshake_data_;
};

}  // namespace camouflage::tls
