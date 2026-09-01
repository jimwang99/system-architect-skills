// adder.sv — 4-bit combinational adder DUT for example-testbench.cpp
//
// clk / rst_n are not used by the datapath; they exist so the testbench can
// demonstrate clock generation, a dedicated reset thread, and clocked cover
// properties.
module adder (
    input  logic       clk,
    input  logic       rst_n,
    input  logic [3:0] a,
    input  logic [3:0] b,
    output logic [4:0] sum
);
  assign sum = a + b;

  // Functional cover point: both inputs at maximum (exercised by test plan).
  cp_max_inputs: cover property (@(posedge clk) disable iff (!rst_n)
                                 a == 4'hF && b == 4'hF);
endmodule
