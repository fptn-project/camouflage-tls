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
  src/builder.cpp include/camouflage/tls/builder.hpp
  # chrome
  src/browsers/google_chrome/google_chrome_builder.hpp src/browsers/google_chrome/google_chrome_builder.cpp
  # yandex
  src/browsers/yandex_browser/yandex_browser_builder.hpp src/browsers/yandex_browser/yandex_browser_builder.cpp
  # firefox
  src/browsers/firefox/firefox_builder.hpp src/browsers/firefox/firefox_builder.cpp
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
