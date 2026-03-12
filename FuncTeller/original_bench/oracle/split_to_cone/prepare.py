import sys
import os

def before_bench_to_verilog(before_bench):
  cmd = '../abc_tool/abc -c "read_bench '+before_bench+'; write_verilog '+before_bench.replace('.bench','.v')+'"'
  os.system(cmd)

def change_name(before_bench):
  if os.path.isfile(before_bench):
    cmd = 'mv '+before_bench+' oracle.bench'
    os.system(cmd)
  return 'oracle.bench'

def run_dc():
  cmd = 'dc_shell -f rtl.tcl > dc.log'
  os.system(cmd)

def read_netlist():
  if not os.path.isfile('oracle_netlist.v'):
    sys.exit('cannot find oracle netlist after resynthesis')
  fp = open('oracle_netlist.v','r')
  data = fp.readlines()
  fp.close()
  inputs = []
  outputs = []
  gates = []
  eof = len(data)
  num = 0
  while(num<eof):
    line = data[num].strip()
    num += 1
    if len(line)==0:
      continue
    elif line.startswith('//'):
      continue
    elif line.startswith('endmodule'):
      break
    while(line.find(';')==-1):
      line += data[num].strip()
      num += 1
    if line.startswith('module '):
      continue    # module line
    elif line.startswith('input '):
      inputs += line[6:].replace(';','').replace(' ','').strip().split(',')
    elif line.startswith('output '):
      outputs += line[7:].replace(';','').replace(' ','').strip().split(',')
    elif line.startswith('wire '):
      continue
    else:
      if line.startswith('assign '):
        if line.find("1'b0")!=-1:
          gate_out = line.replace('assign ','').split('=')[0].strip()
          gate = gate_out+'=XOR('+inputs[0]+','+inputs[0]+')'
        elif line.find("1'b1")!=-1:
          gate_out = line.replace('assign ','').split('=')[0].strip()
          gate = gate_out+'=XNOR('+inputs[0]+','+inputs[0]+')'
        else:
          if line.find('~')!=-1:
            gate = line.replace('assign','').replace('~','').replace(';','').replace(' ','').replace('=','=NOT(')+')'
          else:
            gate = line.replace('assign','').replace(';','').replace(' ','').replace('=','=BUF(')+')'
        gates.append(gate)
      elif line.find('.'):
        cell_type = line.split(' ')[0]
        if cell_type.startswith('XNOR'):
          gate_type = 'XNOR'
        elif cell_type.startswith('XOR'):
          gate_type = 'XOR'
        elif cell_type.startswith('NOR'):
          gate_type = 'NOR'
        elif cell_type.startswith('OR'):
          gate_type = 'OR'
        elif cell_type.startswith('NAND'):
          gate_type = 'NAND'
        elif cell_type.startswith('AND'):
          gate_type = 'AND'
        elif cell_type.startswith('INV'):
          gate_type = 'NOT'
        elif cell_type.startswith('BUF'):
          gate_type = 'BUF'
        else:
          print(line)
        gate_ports = line[line.find('(')+1:-2].replace(' ','').split(',')
        gate_out = gate_ports[-1]
        gate_inputs = gate_ports[:-1]
        gate_out = gate_out[gate_out.find('(')+1:gate_out.find(')')]
        gate_ins = []
        for in1 in gate_inputs:
          gate_ins.append(in1[in1.find('(')+1:in1.find(')')])
        gate = gate_out+'='+gate_type+'('
        for in1 in gate_ins:
          gate += in1+','
        gate += '#'
        gate = gate.replace(',#',')')
        gates.append(gate)
  cmd = 'rm oracle.bench'
  os.system(cmd)
  
  fp = open('oracle.bench','w')
  for in1 in inputs:
    fp.write('INPUT('+in1+')\n')
  for out in outputs:
    fp.write('OUTPUT('+out+')\n')
  for gate in gates:
    fp.write(gate+'\n')
  fp.close()
  
def main():
  before_bench = 'fpga_oracle.bench'
  before_bench = change_name(before_bench)
  before_bench_to_verilog(before_bench)
  run_dc()
  read_netlist()



main()



