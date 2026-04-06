cmake_minimum_required(VERSION 3.16)
project(example LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(base_example
    base_example.cpp
)

target_include_directories(base_example PRIVATE
    ${CMAKE_SOURCE_DIR}/include
)

target_link_libraries(base_example
    PRIVATE camouflage-tls
)
