/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#pragma once

#include <memory>
#include <string>

#include "camouflage/tls/utils.hpp"

namespace camouflage::tls {

class BaseBrowserBuilder {
 public:
  virtual ~BaseBrowserBuilder() = default;

  virtual HandshakeRecordOptional GenerateHandshake(const SNI& sni) = 0;

  virtual HandshakeRecordOptional GenerateHandshake(
      const SNI& sni, const SessionId& session_id) = 0;
};

using BaseBrowserBuilderPtr = std::unique_ptr<BaseBrowserBuilder>;

}  // namespace camouflage::tls
