cmake_minimum_required(VERSION 3.16)

find_package(GTest REQUIRED)

get_filename_component(PROJECT_ROOT ${CMAKE_CURRENT_SOURCE_DIR} DIRECTORY)

# Firefox
add_executable(FirefoxTests tls/FirefoxTests.cpp)
target_link_libraries(FirefoxTests PRIVATE
  GTest::gtest
  GTest::gtest_main
  camouflage-tls
)
target_include_directories(FirefoxTests PRIVATE ${PROJECT_ROOT}/include)
add_test(NAME FirefoxTests COMMAND FirefoxTests)

# GoogleСhrome
add_executable(GoogleChromeTests tls/GoogleChromeTests.cpp)
target_link_libraries(GoogleChromeTests PRIVATE
  GTest::gtest
  GTest::gtest_main
  camouflage-tls
)
target_include_directories(GoogleChromeTests PRIVATE ${PROJECT_ROOT}/include)
add_test(NAME GoogleChromeTests COMMAND GoogleChromeTests)

# YandexBrowser
add_executable(YandexBrowserTests tls/YandexBrowserTests.cpp)
target_link_libraries(YandexBrowserTests PRIVATE
  GTest::gtest
  GTest::gtest_main
  camouflage-tls
)
target_include_directories(YandexBrowserTests PRIVATE ${PROJECT_ROOT}/include)
add_test(NAME YandexBrowserTests COMMAND YandexBrowserTests)
