/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#include <gtest/gtest.h>  // NOLINT(build/include_order)

#include "browsers/yandex_browser/versions/yandex_24_12_0_1772/yandex_24_12_0_1772.hpp"
#include "browsers/yandex_browser/versions/yandex_25_8_3_828/yandex_25_8_3_828.hpp"
#include "browsers/yandex_browser/versions/yandex_26_3_3_881/yandex_26_3_3_881.hpp"
#include "browsers/yandex_browser/yandex_browser_builder.hpp"
#include "camouflage/tls/browsers/yandex_browser.hpp"
#include "utils/test_utils.hpp"

// NOLINTNEXTLINE(google-readability-avoid-underscore-in-googletest-name)
TEST(YandexBrowserTests, Version_24_12_0_1772) {
  camouflage::tls::YandexBrowserBuilder builder(
      camouflage::tls::yandex_browser::Version::kV_24_12_0_1772);
  CheckBrowser(builder, camouflage::tls::kBrowserYandex_24_12_0_1772);
}

// NOLINTNEXTLINE(google-readability-avoid-underscore-in-googletest-name)
TEST(YandexBrowserTests, Version_25_8_3_828) {
  camouflage::tls::YandexBrowserBuilder builder(
      camouflage::tls::yandex_browser::Version::kV_25_8_3_828);
  CheckBrowser(builder, camouflage::tls::kBrowserYandex_25_8_3_828);
}

// NOLINTNEXTLINE(google-readability-avoid-underscore-in-googletest-name)
TEST(YandexBrowserTests, Version_26_3_3_881) {
  camouflage::tls::YandexBrowserBuilder builder(
      camouflage::tls::yandex_browser::Version::kV_26_3_3_881);
  CheckBrowser(builder, camouflage::tls::kBrowserYandex_26_3_3_881);
}
