date
set_host_options -max_cores 8
set timing_separate_clock_gating_group     true
set search_path [concat * $search_path]
define_design_lib WORK -path ./work
  set target_library [list ../../../lib/NangateOpenCellLibrary.db]
  set link_library [list ../../../lib/NangateOpenCellLibrary.db]
  analyze -library WORK -format sverilog ./constraint.v
  elaborate constraint_module
date
  set_dont_use [get_lib_cells NangateOpenCellLibrary/*]
  set_attribute [get_lib_cells NangateOpenCellLibrary/AND2_*] dont_use false
  set_attribute [get_lib_cells NangateOpenCellLibrary/OR2_*] dont_use false
  set_attribute [get_lib_cells NangateOpenCellLibrary/INV_*] dont_use false
  set_attribute [get_lib_cells NangateOpenCellLibrary/NAND2_*] dont_use false
  set_attribute [get_lib_cells NangateOpenCellLibrary/NOR2_*] dont_use false
  set_wire_load_model -name 5K_hvratio_1_1; # Medium
  set_max_area 0
  create_clock -name VCLK -period 10  -waveform {0 5}
  set input_ports  [all_inputs]
  set output_ports [all_outputs]
  set_input_delay -max 1 [get_ports $input_ports ] -clock VCLK
  set_input_delay -min 0 [get_ports $input_ports ] -clock VCLK
  set_output_delay -max 2 [get_ports $output_ports ] -clock VCLK
  set_output_delay -min 1 [get_ports $output_ports ] -clock VCLK
date
  ungroup -flatten -all
  compile -exact_map -ungroup_all -auto_ungroup area
report_timing -nworst 10 -max_paths 20 -nosplit -input_pins -nets -capacitance  >         constraint_time.rpt
report_area                                        > ./constraint_area.rpt
report_power -analysis_effort high                 > ./constraint_power.rpt
write -format verilog -hierarchy -output constraint_netlist.v
exit
