/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/
#pragma once

#include <array>
#include <optional>

#include "camouflage/tls/types.hpp"

namespace camouflage::tls {

using HandshakeRecordOptional = std::optional<tls::HandshakeRecord>;

using SNI = std::string;
using SessionId = std::array<std::uint8_t, 32>;
using Random = std::array<std::uint8_t, 32>;

HandshakeRecordOptional GenerateHandshake(
    const HandshakeData* data, const std::string& sni);

HandshakeRecordOptional GenerateHandshake(const HandshakeData* data,
    const std::string& sni,
    const SessionId& session_id);

}  // namespace camouflage::tls
