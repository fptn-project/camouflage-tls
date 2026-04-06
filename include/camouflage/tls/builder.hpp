/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#pragma once

#include "browsers/google_chrome.h"
#include "browsers/yandex_browser.h"
#include "camouflage/tls/browsers/base_browser_builder.h"
#include "camouflage/tls/types.hpp"

namespace camouflage::tls {

class Builder {
 public:
  static Builder create() { return Builder(); }

  BaseBrowserBuilderPtr GoogleChrome(
      google_chrome::Version version =
          google_chrome::Version::kV_146_0_7680_178);

  BaseBrowserBuilderPtr YandexBrowser(
      yandex_browser::Version version =
          yandex_browser::Version::kV_26_3_0_2182);

 private:
  Builder() = default;
};
}  // namespace camouflage::tls
