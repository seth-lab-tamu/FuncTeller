import sys
import os
import glob
from subprocess import Popen,PIPE

def read_original(oracle_bench):
	fp = open(oracle_bench,'r')
	data = fp.readlines()
	input_size = 0
	fp.close()
	for line in data:
		if line.startswith('INPUT('):
			input_size += 1
		else:
			break
	return input_size

def num_proc(process, user_id):
	p1 = Popen(['ps', 'aux'], stdout=PIPE) 
	p2 = Popen(['grep', user_id], stdout=PIPE, stdin=p1.stdout)
	p3 = Popen(['grep', process], stdout=PIPE, stdin=p2.stdout)
	p1.stdout.close()
	out,_ = p3.communicate()
	p3.stdout.close()
	return len(out.splitlines())

def write_RTL(input_size, d_0):
	fp = open('../middle_process/RTL_constraint/n_'+str(input_size)+'_d_'+str(d_0)+'/constraint.v','w')
	line = 'module constraint_module ('
	for i in range(input_size):
		line+='a_'+str(i)+', '
	for i in range(input_size):
		line+='b_'+str(i)+', '
	line += 'y);\n'
	fp.write(line)
	line = 'input '
	for i in range(input_size):
		line+='a_'+str(i)+', '
	for i in range(input_size):
		line+='b_'+str(i)+', '
	line += '#'
	line = line.replace(', #',';\n')
	fp.write(line)
	fp.write('output y;\n')
	fp.write('parameter d_0 = '+str(d_0)+';\n')
	fp.write('integer hd;\n')
	line = 'assign hd = '
	for i in range(input_size):
		line += '(a_'+str(i)+' ^ b_'+str(i)+' ? 1 : 0)+'
	line += '#'
	line = line.replace('+#',';\n')
	fp.write(line)
	fp.write('assign y = (hd < d_0 + 1);\n')
	fp.write('endmodule')
	fp.close()
	return 0

def build_distance_constraint(input_size, d):
	if not os.path.isdir('../middle_process/RTL_constraint/n_'+str(input_size)+'_d_'+str(d)+'/'):
		os.system('mkdir ../middle_process/RTL_constraint/n_'+str(input_size)+'_d_'+str(d)+'/')
	if not os.path.isfile('../middle_process/RTL_constraint/n_'+str(input_size)+'_d_'+str(d)+'/constraint_netlist.v'):
		os.system('cp rtl.tcl ../middle_process/RTL_constraint/n_'+str(input_size)+'_d_'+str(d)+'/.')
		write_RTL(input_size, d)
		os.system('cd ../middle_process/RTL_constraint/n_'+str(input_size)+'_d_'+str(d)+'/; dc_shell -f rtl.tcl > dc.log &')
	else:
		return




def main():
	oracle_bench =  sys.argv[1]
	max_num_process = int(sys.argv[2])
	user_id = sys.argv[3]

	# only collect input size from original circuit
	input_size = read_original(oracle_bench)
	process = 'dc_shell'
	for d in range(1, input_size+1):
		while(num_proc(process, user_id) > max_num_process):
			os.system('sleep 30')
		build_distance_constraint(input_size, d)


main()






