import sys

def read_bench(original_bench):
  inputs = []
  outputs= []
  fp = open(original_bench, 'r')
  data = fp.readlines()
  fp.close()
  eof = len(data)
  num = 0
  while(num<eof):
    line = data[num].strip()
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

def write_cpp(inputs, outputs, original_bench):
  #print original_bench.replace('.bench','')+'_sim_main.cpp'
  fp = open(original_bench.replace('.bench','')+'_sim_main.cpp', 'w')
  
  fp.write('#include <iostream>\n')
  fp.write('#include <verilated.h>\n')
  fp.write('#include <V'+original_bench.replace('.bench','')+'.h>\n')
  fp.write('int main(int argc, char** argv) {\n')
  fp.write('\tusing namespace std;\n')
  fp.write('\tV'+original_bench.replace('.bench','')+'* top = new V'+original_bench.replace('.bench','')+';\n')
  for i in range(0, len(inputs)):
    in1 = inputs[i]
    fp.write('\ttop->'+in1+' = atoi(argv['+str(i+1)+']);\n')
  fp.write('\ttop->eval();\n')
  fp.write('\tcout<<"'+original_bench.replace('.bench','')+'"<<endl;\n')
  for out in outputs:
    fp.write('\tcout << (int)top->'+out+'  << " ";\n')
  fp.write('\tcout << endl;\n')
  fp.write('\treturn 0;\n }\n')
  fp.close()
    
def build_sim_main(original_bench):
  inputs, outputs = read_bench(original_bench)  
  write_cpp(inputs, outputs, original_bench)





















