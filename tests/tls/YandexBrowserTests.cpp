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

using namespace camouflage::tls;

TEST(YandexBrowserTests, Version_24_12_0_1772) {
  YandexBrowserBuilder builder(yandex_browser::Version::kV_24_12_0_1772);
  CheckBrowser(builder, kBrowserYandex_24_12_0_1772);
}

TEST(YandexBrowserTests, Version_25_8_3_828) {
  YandexBrowserBuilder builder(yandex_browser::Version::kV_25_8_3_828);
  CheckBrowser(builder, kBrowserYandex_25_8_3_828);
}

TEST(YandexBrowserTests, Version_26_3_3_881) {
  YandexBrowserBuilder builder(yandex_browser::Version::kV_26_3_3_881);
  CheckBrowser(builder, kBrowserYandex_26_3_3_881);
}
