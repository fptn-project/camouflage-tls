/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#include "camouflage/tls/builder.hpp"

#include "browsers/google_chrome/google_chrome_builder.h"
#include "browsers/yandex_browser/yandex_browser_builder.h"
#include "camouflage/tls/browsers/base_browser_builder.h"

namespace camouflage::tls {

BaseBrowserBuilderPtr Builder::GoogleChrome(google_chrome::Version version) {
  return std::make_unique<GoogleChromeBrowserBuilder>(version);
}

BaseBrowserBuilderPtr Builder::YandexBrowser(yandex_browser::Version version) {
  return std::make_unique<YandexBrowserBuilder>(version);
}

}  // namespace camouflage::tls
