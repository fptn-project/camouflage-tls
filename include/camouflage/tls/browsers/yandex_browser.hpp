/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#pragma once

#include <cstdint>

namespace camouflage::tls::yandex_browser {

enum class Version : uint32_t {
  kV_26_3_3_881 = 1,
  kV_25_8_3_828 = 2,
  kV_24_12_0_1772 = 3,
};

}  // namespace camouflage::tls::yandex_browser
