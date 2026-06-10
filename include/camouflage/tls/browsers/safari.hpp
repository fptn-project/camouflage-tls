/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#pragma once

#include <cstdint>

namespace camouflage::tls::safari {

enum class Version : uint32_t {
  kV_26_4 = 1,
  kV_26_5 = 2,
};

}  // namespace camouflage::tls::safari
