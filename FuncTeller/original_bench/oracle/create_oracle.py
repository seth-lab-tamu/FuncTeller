import sys
import os

import write_sim_main

def read_inputs_outputs_seq(bench_cone):
  inputs = []
  outputs = []
  fp = open(bench_cone,'r')
  data = fp.readlines()
  fp.close()
  eof = len(data)
  num = 0
  while(num<eof):
    line = data[num].strip().replace(' ','')
    num += 1
    if len(line) == 0 or line[0] == '#':
      continue
    elif line.find('INPUT')!=-1:
      item = line[line.find('(')+1:line.find(')')]
      inputs.append(item)
    elif line.find('OUTPUT')!=-1:
      item = line[line.find('(')+1:line.find(')')]
      outputs.append(item)
    elif line.find('=')!=-1:
      break
  return inputs, outputs  
    
def rewrite_bench(bench_cone):
  fp = open(bench_cone,'r')
  data = fp.readlines()
  fp.close()
  fp = open(bench_cone,'w')
  for line in data:
    fp.write(line.replace('__','_'))
  fp.close()  

def bench2verilog(bench_cone, bm_name):
  cmd = './abc_tool/abc -c "read_bench '+bench_cone +'; write_verilog '+bm_name+'.v"'
  os.system(cmd)

def write_sim(bench_cone): 
  write_sim_main.build_sim_main(bench_cone.split('/')[-1])

def generate_oracle(bm_name):
  #cmd = 'verilator -Wall -cc '+bm_name+'.v -exe '+bm_name+'_sim_main.cpp -Mdir obj_dir_'+bm_name+'/'
  cmd = 'verilator -Wno-UNUSED -cc '+bm_name+'.v -exe '+bm_name+'_sim_main.cpp -Mdir obj_dir_'+bm_name+'/'
  
  #print cmd
  
  os.system(cmd)
  #exit(1)
  cmd = 'make -j -C obj_dir_'+bm_name+'/ -f V'+bm_name+'.mk V'+bm_name
  #print cmd
  
  os.system(cmd)
  
  #exit(1)
  cmd = 'cp obj_dir_'+bm_name+'/V'+bm_name+' '+bm_name
  #print cmd
  os.system(cmd)

def delete_files(bm_name):
  cmd = 'rm '+bm_name+'.v'
  os.system(cmd)
  cmd = 'rm '+bm_name+'_*'
  os.system(cmd)
  cmd = 'rm obj_dir_'+bm_name+'/ -rf'
  os.system(cmd)

def main():
  original_bench_cone = sys.argv[1]
  bench_cone = original_bench_cone.split('/')[-1]
  cmd ='cp '+original_bench_cone+' .'
  os.system(cmd)
  bm_name = bench_cone.replace('.bench','')
  inputs, outputs = read_inputs_outputs_seq(bench_cone)
  rewrite_bench(bench_cone)
  bench2verilog(bench_cone, bm_name)
  write_sim(bench_cone)
  generate_oracle(bm_name)
  delete_files(bm_name)

main()
