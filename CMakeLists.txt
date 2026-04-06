cmake_minimum_required(VERSION 3.16)
project(camouflage_tls VERSION "1.0.0" LANGUAGES CXX)

# project settings
set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if (MSVC)
    add_compile_options("/bigobj")
    add_compile_options("/std:c++20")
    add_compile_options("/Zc:inline-")
    add_compile_options("/permissive-")
    add_compile_options("/Zc:__cplusplus")
    add_compile_options("/d2SSAOptimizer-")
    add_compile_definitions(_WIN32_WINNT=0x0A00) # Windows 10
endif ()

# --- project ---
set(CMAKE_COMPILE_WARNING_AS_ERROR ON) # check all warnings!
if (MSVC)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
    add_compile_options(/W4 /WX)
else ()
    add_compile_options(-Wall -Werror -pedantic)
endif ()

# --- include ---
include_directories(src/)
include_directories(include/)

add_library(camouflage-tls STATIC
  src/builder.cpp include/camouflage/tls/builder.hpp
  src/browsers/google_chrome/google_chrome_builder.h src/browsers/google_chrome/google_chrome_builder.cpp
  src/browsers/google_chrome/versions/google_chrome_146_0_7680_178.cpp
  src/browsers/yandex_browser/yandex_browser_builder.h src/browsers/yandex_browser/yandex_browser_builder.cpp
  src/browsers/yandex_browser/versions/yandex_browser_26_3_0_2182.cpp
)

target_include_directories(camouflage-tls PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:include>)

install(
        TARGETS camouflage-tls
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib)

install(DIRECTORY include/camouflage-tls DESTINATION include)

add_subdirectory(example)
