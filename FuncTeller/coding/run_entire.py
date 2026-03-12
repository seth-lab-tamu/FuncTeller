import sys
import os
import glob
from subprocess import Popen,PIPE

def read_original_bench(original_bench):
	fp = open(original_bench,'r')
	data = fp.readlines()
	fp.close()
	inputs = []
	outputs = []
	for line in data:
		line = line.strip().replace(' ','')
		if len(line)==0 or line[0] == '#':
			continue
		elif line.startswith('INPUT('):
			item = line[line.find('(')+1:line.find(')')]
			inputs.append(item)
		elif line.startswith('OUTPUT('):
			item = line[line.find('(')+1:line.find(')')]
			outputs.append(item)
		elif line.find('=')!=-1:
			break
	return inputs, outputs

def read_predicted_bench(bench_cone):
	fp = open(bench_cone,'r')
	data = fp.readlines()
	fp.close()
	inputs = []
	gates = []
	eof = len(data)
	num = 0
	for line in data:
		line = line.strip()
		if line.startswith('INPUT('):
			item = line[line.find('(')+1:line.find(')')]
			inputs.append(item)
		elif line.startswith('OUTPUT('):
			item = line[line.find('(')+1:line.find(')')]
			cone_out = item
		elif line.find('=')!=-1:
			gates.append(line)
	return inputs, cone_out, gates

def build_predicted_entire_circuit(inputs, outputs, original_bench,converge_p):
	bm = original_bench.split('/')[-1].replace('.bench','')
	fp0 = open('../middle_process/predicted_circuit_entire/'+bm+'_converge_'+str(converge_p)+'.bench','w')
	for in1 in inputs:
		fp0.write('INPUT('+in1+')\n')
	for out in outputs:
		fp0.write('OUTPUT('+out+')\n')
	for single_cone in glob.glob('../middle_process/predicted_circuit/'+bm+'*.bench'):
		bm_cone = single_cone.split('/')[-1].replace('.bench','').split('_converge_')[0]
		inputs_cone, cone_out, gates_cone = read_predicted_bench(single_cone)
		for gate in gates_cone:
			gate_out = gate[:gate.find('=')]
			gate_func = gate[gate.find('=')+1:gate.find('(')]
			gate_ins = gate[gate.find('(')+1:gate.find(')')].split(',')
			new_gate = ''
			if gate_out == cone_out:
				new_gate += cone_out+'='+gate_func+'('
			else:
				new_gate += gate_out+'_'+cone_out+'='+gate_func+'('
			for in1 in gate_ins:
				if in1 not in inputs_cone:
					new_gate += in1+'_'+cone_out+','
				else:
					new_gate += in1+','
			new_gate += '#'
			new_gate = new_gate.replace(',#',')')
			fp0.write(new_gate+'\n')
	fp0.close()
	
def num_proc(process, user_id):
    p1 = Popen(['ps', 'aux'], stdout=PIPE) 
    p2 = Popen(['grep', user_id], stdout=PIPE, stdin=p1.stdout)
    p3 = Popen(['grep', process], stdout=PIPE, stdin=p2.stdout)
    p4 = Popen(['grep', 'random_no_budget_1point1times'], stdout=PIPE, stdin=p3.stdout)
    p1.stdout.close()
    out,_ = p4.communicate()
    p4.stdout.close()
    return len(out.splitlines())

def main():
	original_bench = sys.argv[1]
	converge_p = int(sys.argv[2])
	d0 = int(sys.argv[3])
	second_constraint = float(sys.argv[4])
	max_num_process = int(sys.argv[5])
	user_id = sys.argv[6]
	if not os.path.isdir('./log_files/'):
		os.system('mkdir log_files/')
	process = 'python3'
	a = 0
	for single_cone in glob.glob(original_bench.replace('.bench','_*.bench')):
		oracle_cone = single_cone.replace('.bench','').replace('/split_to_cone','')
		bm_cone_oracle = oracle_cone.split('/')[-1]		
		if os.path.isfile('../middle_process/predicted_circuit/'+bm_cone_oracle+'_converge_'+str(converge_p)+'.bench'):
			continue
		log_file = './log_files/'+oracle_cone.split('/')[-1]+'_converge_'+str(converge_p)+'_d0_'+str(d0)+'_2times_'+str(second_constraint)+'.log'
		#print num_proc(process) 
		while (num_proc(process, user_id) > max_num_process):
			os.system('sleep 10')
		cmd = 'python3 random_no_budget_1point1times.py '+oracle_cone+' '+str(converge_p)+' '+str(d0)+' '+str(second_constraint)+' > '+log_file+' &'
			#print cmd 
		os.system(cmd)
			
	while(1):
		flag = 1
		for single_cone in glob.glob(original_bench.replace('.bench','_*.bench')):
			bm = single_cone.split('/')[-1].replace('.bench','')
			predicted_bench = '../middle_process/predicted_circuit/'+bm+'_converge_'+str(converge_p)+'.bench'
			if not os.path.isfile(predicted_bench):
				flag = 0
		if flag == 0:
			os.system('sleep 60')
			continue
		else:
			break

	inputs, outputs = read_original_bench(original_bench)
	build_predicted_entire_circuit(inputs, outputs, original_bench, converge_p)

main()


# python run_entire.py ../original_bench/c880/split_to_cone/c880.bench 10 2 3600
