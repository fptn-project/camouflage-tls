cmake_minimum_required(VERSION 3.16)
project(camouflage_tls VERSION "1.0.0" LANGUAGES CXX)

# project settings
set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# --- project ---
set(CMAKE_COMPILE_WARNING_AS_ERROR ON) # check all warnings!
if (MSVC)
  set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
  add_compile_options(/W4 /WX)
  add_compile_options("/bigobj")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /MP1")
else ()
  add_compile_options(-Wall -Werror -pedantic)
endif ()

# --- include ---
include_directories(src/)
include_directories(include/)

add_library(camouflage-tls STATIC
  src/utils.cpp
  src/builder.cpp include/camouflage/tls/builder.hpp

  # firefox
  src/browsers/firefox/firefox_builder.hpp src/browsers/firefox/firefox_builder.cpp
  src/browsers/firefox/versions/firefox_149_0/firefox_149_0.hpp src/browsers/firefox/versions/firefox_149_0/firefox_149_0.cpp

  # google chrome
  src/browsers/google_chrome/google_chrome_builder.hpp src/browsers/google_chrome/google_chrome_builder.cpp
  src/browsers/google_chrome/versions/chrome_147_0_7727_56/chrome_147_0_7727_56.hpp src/browsers/google_chrome/versions/chrome_147_0_7727_56/chrome_147_0_7727_56.cpp
  src/browsers/google_chrome/versions/chrome_146_0_7680_178/chrome_146_0_7680_178.hpp src/browsers/google_chrome/versions/chrome_146_0_7680_178/chrome_146_0_7680_178.cpp
  src/browsers/google_chrome/versions/chrome_145_0_7632_46/chrome_145_0_7632_46.hpp src/browsers/google_chrome/versions/chrome_145_0_7632_46/chrome_145_0_7632_46.cpp

  # safari
  src/browsers/safari/safari_builder.hpp src/browsers/safari/safari_builder.cpp
  src/browsers/safari/versions/safari_26_4/safari_26_4.hpp src/browsers/safari/versions/safari_26_4/safari_26_4.cpp

  # yandex
  src/browsers/yandex_browser/yandex_browser_builder.hpp src/browsers/yandex_browser/yandex_browser_builder.cpp
  src/browsers/yandex_browser/versions/yandex_24_12_0_1772/yandex_24_12_0_1772.hpp src/browsers/yandex_browser/versions/yandex_24_12_0_1772/yandex_24_12_0_1772.cpp
  src/browsers/yandex_browser/versions/yandex_25_8_3_828/yandex_25_8_3_828.hpp src/browsers/yandex_browser/versions/yandex_25_8_3_828/yandex_25_8_3_828.cpp
  src/browsers/yandex_browser/versions/yandex_26_3_3_881/yandex_26_3_3_881.hpp src/browsers/yandex_browser/versions/yandex_26_3_3_881/yandex_26_3_3_881.cpp
)

target_include_directories(camouflage-tls PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:include>)

install(
        TARGETS camouflage-tls
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib)

install(DIRECTORY include/camouflage-tls DESTINATION include)

add_subdirectory(example)

# --- tests ---
enable_testing()
add_subdirectory(tests)
include_directories(tests/)
