/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/
#pragma once

#include "camouflage/tls/browsers/base_browser_builder.h"
#include "camouflage/tls/browsers/google_chrome.h"
#include "camouflage/tls/types.hpp"

namespace camouflage::tls {

class GoogleChromeBrowserBuilder final : public BaseBrowserBuilder {
 public:
  explicit GoogleChromeBrowserBuilder(google_chrome::Version version);

  ~GoogleChromeBrowserBuilder() override = default;

  HandshakeRecordOptional GenerateHandshake(const SNI& sni) override;

  HandshakeRecordOptional GenerateHandshake(
      const SNI& sni, const SessionId& session_id) override;

 private:
  const google_chrome::Version version_;
  const HandshakeData* handshake_data_;
};

}  // namespace camouflage::tls
