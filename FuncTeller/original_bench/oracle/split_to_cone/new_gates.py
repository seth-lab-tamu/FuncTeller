import sys
import os
import math

def read_bench(bench):
  fp = open(bench ,'r')
  data = fp.readlines()
  fp.close()
  eof = len(data)
  num = 0
  inputs = []
  outputs = []
  gates = []
  while(num<eof):
    line = data[num].strip().replace(' ','')
    num += 1
    if len(line)==0 or line[0]=='#':
      continue
    elif line.startswith('INPUT('):
      term = line[line.find('(')+1:line.find(')')]
      inputs.append(term)
    elif line.startswith('OUTPUT('):
      term = line[line.find('(')+1:line.find(')')]
      outputs.append(term)
    elif line.find('=')!=-1:
      gates.append(line)
  return inputs, outputs, gates

def change_gates(gates):
  new_gates = []
  for gate in gates:
    gate_out = gate[:gate.find('=')].replace('__','_')
    if gate_out.endswith('_'):
      gate_out+='end'
    gate_type = gate[gate.find('=')+1:gate.find('(')]
    gate_ins = gate[gate.find('(')+1:gate.find(')')].split(',')
    new_gate = gate_out+'='
    if gate_type == 'and' or gate_type == 'AND':
      new_gate += 'AND'
    elif gate_type == 'nand' or gate_type == 'NAND':
      new_gate += 'NAND'
    elif gate_type == 'or' or gate_type == 'OR':
      new_gate += 'OR'
    elif gate_type == 'nor' or gate_type == 'NOR':
      new_gate += 'NOR'
    elif gate_type == 'buf' or gate_type == 'BUF' or gate_type == 'BUFF':
      new_gate += 'BUF'
    elif gate_type == 'inv' or gate_type =='not' or gate_type == 'NOT':
      new_gate += 'NOT'
    elif gate_type == 'xor' or gate_type == 'XOR':
      new_gate += 'XOR'
    elif gate_type == 'xnor' or gate_type == 'XNOR':
      new_gate += 'XNOR'
    else:
      print(gate)
    new_gate += '('
    for in1 in gate_ins:
      if in1.endswith('_'):
        in1 += 'end'
      new_gate += in1.replace('__','_')+','
    new_gate += '#'
    new_gate = new_gate.replace(',#',')')
    new_gates.append(new_gate)
  return new_gates

def int2string(index, input_size):
  string =  bin(index).split('b')[-1]
  rest_length = input_size - len(string)
  for i in range (0, rest_length):
    string = '0'+string
  return string

def creat_new_bench(bm_name, inputs, outputs, gates):
  new_bench = bm_name+'_new.bench'
  fp = open(new_bench,'w')
  new_inputs = []
  
  a1 = math.log(len(inputs),2)
  b1 = int(a1)
  if a1==b1:
    l1 = b1
  else:
    l1 = b1+1
  
  new_inputs = []
  for i in range(len(inputs)):
    new_inputs.append('in_'+int2string(i, l1))
  

  a2 = math.log(len(outputs),2)
  b2 = int(a2)
  if a2==b2:
    l2 = b2
  else:
    l2 = b2+1
  
  new_outputs = []
  for i in range(len(outputs)):
    new_outputs.append('out_'+int2string(i, l2))
 


  '''
  for in1 in inputs:
    in1 = in1.replace('__','_')
    if in1.endswith('_'):
      in1 += 'end'
    fp.write('INPUT('+in1+')\n')

  for out in outputs:
    out = out.replace('__','_')
    if out.endswith('_'):
      out += 'end'
    fp.write('OUTPUT('+out.replace('__','_')+')\n')
  '''

  for in1 in new_inputs:
    fp.write('INPUT('+in1+')\n')
  for out in new_outputs:
    fp.write('OUTPUT('+out+')\n')



  for i in range(len(inputs)):
    new_in = new_inputs[i]
    in1 = inputs[i]
    in1 = in1.replace('__','_')
    if in1.endswith('_'):
      in1 += 'end'
    gate = in1+'=BUF('+new_in+')'
    fp.write(gate+'\n')

  for gate in gates:
    fp.write(gate+'\n')
  
  for i in range(len(outputs)):
    new_out = new_outputs[i]
    out = outputs[i]
    out = out.replace('__','_')
    if out.endswith('_'):
      out += 'end'
    gate = new_out+'=BUF('+out+')'
    fp.write(gate+'\n')


  fp.close()


def exchange(bm_name):
  if not os.path.isfile(bm_name+'.bench'):
    cmd = 'mv '+bm_name+'_new.bench '+bm_name+'.bench'
    os.system(cmd)
  else:
    cmd1 = 'rm '+bm_name+'.bench'
    os.system(cmd1)
    cmd2 = 'mv '+bm_name+'_new.bench '+bm_name+'.bench'
    os.system(cmd2)

def main():
  bench = sys.argv[1]
  bm_name = bench.replace('.bench','')
  inputs, outputs, gates = read_bench(bench)
  new_gates = change_gates(gates)
  creat_new_bench(bm_name, inputs, outputs, new_gates)
  exchange(bm_name)

main()
