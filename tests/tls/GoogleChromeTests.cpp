/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#include <gtest/gtest.h>  // NOLINT(build/include_order)

#include "browsers/google_chrome/google_chrome_builder.hpp"
#include "browsers/google_chrome/versions/chrome_145_0_7632_46/chrome_145_0_7632_46.hpp"
#include "browsers/google_chrome/versions/chrome_146_0_7680_178/chrome_146_0_7680_178.hpp"
#include "browsers/google_chrome/versions/chrome_147_0_7727_56/chrome_147_0_7727_56.hpp"
#include "camouflage/tls/browsers/google_chrome.hpp"
#include "utils/test_utils.hpp"

TEST(GoogleChromeTests, Version_145_0_7632_46) {
  camouflage::tls::GoogleChromeBrowserBuilder builder(
      camouflage::tls::google_chrome::Version::kV_145_0_7632_46);
  CheckBrowser(builder, camouflage::tls::kBrowserChrome_145_0_7632_46);
}

TEST(GoogleChromeTests, Version_146_0_7680_178) {
  camouflage::tls::GoogleChromeBrowserBuilder builder(
      camouflage::tls::google_chrome::Version::kV_146_0_7680_178);
  CheckBrowser(builder, camouflage::tls::kBrowserChrome_146_0_7680_178);
}

TEST(GoogleChromeTests, Version_147_0_7727_56) {
  camouflage::tls::GoogleChromeBrowserBuilder builder(
      camouflage::tls::google_chrome::Version::kV_147_0_7727_56);
  CheckBrowser(builder, camouflage::tls::kBrowserChrome_147_0_7727_56);
}
