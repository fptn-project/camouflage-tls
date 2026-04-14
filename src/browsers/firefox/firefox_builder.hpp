/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/
#pragma once

#include "camouflage/tls/browsers/base_browser_builder.hpp"
#include "camouflage/tls/browsers/firefox.hpp"
#include "camouflage/tls/types.hpp"

namespace camouflage::tls {

class FirefoxBuilder final : public BaseBrowserBuilder {
 public:
  explicit FirefoxBuilder(firefox::Version version);

  ~FirefoxBuilder() override = default;

  HandshakeRecordOptional GenerateHandshake(const SNI& sni) override;

  HandshakeRecordOptional GenerateHandshake(
      const SNI& sni, const SessionId& session_id) override;

 private:
  const firefox::Version version_;
  const HandshakeData* handshake_data_;
};

}  // namespace camouflage::tls
