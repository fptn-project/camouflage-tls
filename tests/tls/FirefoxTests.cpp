/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#include <gtest/gtest.h>  // NOLINT(build/include_order)

#include "browsers/firefox/firefox_builder.hpp"
#include "browsers/firefox/versions/firefox_149_0/firefox_149_0.hpp"
#include "browsers/firefox/versions/firefox_150_0_3/firefox_150_0_3.hpp"
#include "browsers/firefox/versions/firefox_151_0_3/firefox_151_0_3.hpp"
#include "camouflage/tls/browsers/firefox.hpp"
#include "utils/test_utils.hpp"

// NOLINTNEXTLINE(google-readability-avoid-underscore-in-googletest-name)
TEST(FirefoxTests, Version_149_0) {
  camouflage::tls::FirefoxBuilder builder(
      camouflage::tls::firefox::Version::kV_149_0);
  CheckBrowser(builder, camouflage::tls::kBrowserFirefox_149_0);
}

// NOLINTNEXTLINE(google-readability-avoid-underscore-in-googletest-name)
TEST(FirefoxTests, Version_150_0_3) {
  camouflage::tls::FirefoxBuilder builder(
      camouflage::tls::firefox::Version::kV_150_0_3);
  CheckBrowser(builder, camouflage::tls::kBrowserFirefox_150_0_3);
}

// NOLINTNEXTLINE(google-readability-avoid-underscore-in-googletest-name)
TEST(FirefoxTests, Version_151_0_3) {
  camouflage::tls::FirefoxBuilder builder(
      camouflage::tls::firefox::Version::kV_151_0_3);
  CheckBrowser(builder, camouflage::tls::kBrowserFirefox_151_0_3);
}
