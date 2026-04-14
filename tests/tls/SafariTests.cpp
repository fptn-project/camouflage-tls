/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#include <gtest/gtest.h>  // NOLINT(build/include_order)

#include "browsers/safari/safari_builder.hpp"
#include "browsers/safari/versions/safari_26_4/safari_26_4.hpp"
#include "camouflage/tls/browsers/safari.hpp"
#include "utils/test_utils.hpp"

TEST(FirefoxTests, Version_149_0) {
  camouflage::tls::SafariBuilder builder(
      camouflage::tls::safari::Version::kV_26_4);
  CheckBrowser(builder, camouflage::tls::kBrowserSafari_26_4);
}
