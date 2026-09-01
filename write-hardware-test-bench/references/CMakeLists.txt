# CMakeLists.txt — builds the example SystemC testbench (tb_adder).
#
# Usage (from this directory):
#   cmake -B build
#   cmake -B build -DTB_ENABLE_TRACE_FST=ON -DTB_ENABLE_COVERAGE=ON
#   cmake --build build
#   ./build/tb_adder
#
# SystemC discovery: verilator_link_systemc() honors the SYSTEMC_INCLUDE /
# SYSTEMC_LIBDIR / SYSTEMC_ROOT environment variables, then falls back to
# the default prefix (e.g. /usr/local, /opt/homebrew).
cmake_minimum_required(VERSION 3.19)
project(tb_adder CXX)

# SystemC 3.x hard-requires C++17.
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(verilator REQUIRED HINTS $ENV{VERILATOR_ROOT})

add_executable(tb_adder example-testbench.cpp)

# Keep routine runs small. Enable artifacts only when they answer a debug or
# coverage question.
option(TB_ENABLE_TRACE_FST "Build FST tracing support" OFF)
option(TB_ENABLE_COVERAGE "Build coverage instrumentation" OFF)

set(TB_VERILATE_FEATURES SYSTEMC)
if(TB_ENABLE_TRACE_FST)
    list(APPEND TB_VERILATE_FEATURES TRACE_FST)
endif()
if(TB_ENABLE_COVERAGE)
    list(APPEND TB_VERILATE_FEATURES COVERAGE)
endif()

# Keep runtime artifacts in the build tree even when the executable is
# launched from the source directory.
target_compile_definitions(tb_adder PRIVATE
    TB_OUTPUT_DIR="${CMAKE_CURRENT_BINARY_DIR}"
)

verilate(tb_adder
    SOURCES adder.sv
    TOP_MODULE adder
    ${TB_VERILATE_FEATURES}
    VERILATOR_ARGS --assert -Wall
)

# Links libsystemc and adds SystemC include paths.
verilator_link_systemc(tb_adder)
