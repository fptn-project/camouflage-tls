/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/
#pragma once

#include <random>

#include "camouflage/tls/types.hpp"

namespace camouflage::tls {

inline camouflage::tls::HandshakeRecordOptional FindRandomRecordBySni(
    SNI sni, const camouflage::tls::HandshakeData* handshake_data) {
  if (!handshake_data) {
    return std::nullopt;
  }

  const auto it = handshake_data->find(sni.size());
  if (it == handshake_data->end()) {
    return std::nullopt;
  }

  const auto& records = it->second;
  if (records.empty()) {
    return std::nullopt;
  }

  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_int_distribution<size_t> dis(0, records.size() - 1);

  HandshakeRecord new_record = records[dis(gen)];
  return new_record;
}

}  // namespace camouflage::tls
