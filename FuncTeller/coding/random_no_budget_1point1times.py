import sys
import os
import random
import math
import time
import pycosat

ON_set = []
OFF_set = []

Constraint_CNFs = {}

def read_bench(bench_path):
	fp = open(bench_path, 'r')
	data = fp.readlines()
	fp.close()
	inputs = []
	outputs = []
	gates = []
	for line in data:
		line = line.strip().replace(' ','')
		if len(line) == 0 or line.startswith('#'):
			continue
		elif line.startswith('INPUT('):
			inputs.append(line[6:-1])
		elif line.startswith('OUTPUT('):
			outputs.append(line[7:-1])
		elif line.find('=')!=-1:
			gates.append(line)
	return inputs, outputs, gates

def int2string(index, input_size):
	string =	bin(index).split('b')[-1]
	rest_length = input_size - len(string)
	for i in range (0, rest_length):
		string = '0'+string
	return string
	

def first_random_minterm(input_size, oracle_path, converge):
	counter = 0
	while(counter < 100*converge):
		#test_index = random.randrange(0,pow(2, input_size))			# 0<= test_index < pow(2,input_size)
		#test_string = int2string(test_index, input_size)
		test_string = ''
		for i in range(input_size):
			rand_byte = random.randint(0,1)
			if rand_byte == 0:
				test_string += '0'
			elif rand_byte == 1:
				test_string += '1'	
		if test_string in ON_set or test_string in OFF_set:
			continue
		test_minterm = ''
		for literal in test_string:
			test_minterm += literal+' '
		test_minterm += '#'
		test_minterm = test_minterm.replace(' #','')
		cmd = oracle_path + ' '+test_minterm+' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log'
		os.system(cmd)
		counter += 1
		fp = open('test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','r')
		data = fp.readlines()
		fp.close()
		result = int(data[1].strip())
		os.system('rm test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log')
		if result == 1:
			ON_set.append(test_string)
			return test_string
		elif result == 0:
			OFF_set.append(test_string)
		else:
			print('???') 
	if counter>=100*converge:
		#sys.exit('cannot find ON_set minterm during initilization random querying')
		return None

def generate_random_strings(free_length):
	random_strings = []
	while(1):
		string = ''
		for i in range(free_length):
			rand_byte = random.randint(0,1)
			if rand_byte == 0:
				string += '0'
			elif rand_byte == 1:
				string += '1'
		if string not in random_strings:
			random_strings.append(string)
		if len(random_strings) == int(1.1*free_length):
			break
	return random_strings


def generate_random_strings_firstPI(free_length):
	random_strings = []
	while(1):
		string = ''
		for i in range(free_length):
			rand_byte = random.randint(0,1)
			if rand_byte == 0:
				string += '0'
			elif rand_byte == 1:
				string += '1'
		if string not in random_strings:
			random_strings.append(string)
		if len(random_strings) == 8 or len(random_strings)==pow(2,free_length):
			break
	return random_strings

def minimum_in_list(a_list):
	mini_size = a_list[0]
	for a in a_list:
		if a < mini_size:
			mini_size = a
	return mini_size

def generate_random_strings_p(free_length, p):
	random_strings = []
	while(1):
		string = ''
		for i in range(free_length):
			rand_byte = random.randint(0,1)
			if rand_byte == 0:
				string += '0'
			elif rand_byte == 1:
				string += '1'
		if string not in random_strings:
			random_strings.append(string)
		a_list = [p, pow(2, free_length)]
		if len(random_strings) == minimum_in_list(a_list):
			break
	return random_strings


def expand_from_minterm_2_PI_firstPI(starting_string, input_size, oracle_path, converge, PIT):
	#print 'starting point:\t', starting_string
	hard_dc = []
	p_dc = 8
	if len(PIT)!=0:
		for i in range(len(PIT[0])):
			flag_dc = 1
			for pi in PIT:
				if pi[i] != '-':
					flag_dc = 0
					break
			if flag_dc == 1:
				hard_dc.append(i)
	soft_dc = []

	time1 = time.time()
	cube = []
	num_tested_minterm = 0
	for literal in starting_string:
		cube.append(literal)
	string_for_cube = ''
	for literal in cube:
		string_for_cube += literal
	#print 'intial cube', string_for_cube
	#print 'before expansion'
	for i in range(0,input_size):
		cube[i] = '?'
		string_for_cube = ''
		for literal in cube:
			string_for_cube += literal
		if i == 0:
			cmd = oracle_path
			for j in range(0, input_size):
				if j==0:
					if starting_string[j]=='1':
						cmd += ' 0'
					else:
						cmd += ' 1'
				else:
					cmd += ' '+starting_string[j] 
			cmd += ' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log'
			os.system(cmd)
			num_tested_minterm += 1
			fp = open('test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','r')
			data	= fp.readlines()[-1]
			fp.close()
			os.system('rm test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log')
			result = data.strip()
			if result == '1':
				minterm = cmd.replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(oracle_path,'').replace(' ','')
				#print minterm, 'ON_set'
				ON_set.append(minterm)
				cube[i] = '-'
				if i not in hard_dc:
					soft_dc.append(i)

			else:
				minterm = cmd.replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(oracle_path,'').replace(' ','')
				#print minterm, 'OFF_set'
				OFF_set.append(minterm)
				cube[i] = starting_string[i]
				if i in hard_dc:
					hard_dc.remove(i)

			cube_string = ''
			for literal in cube:
				cube_string += literal
		else:
			if i in hard_dc:
				random_strings =	generate_random_strings_p(cube.count('-'), 8)
				flag = True
				for rand_string in random_strings:
					cmd = oracle_path
					local_counter = 0
					for j in range(input_size):
						if j==i:
							if starting_string[i] == '0':
								cmd += ' 1'
							else:
								cmd += ' 0'
						else:
							if cube[j] == '-':
								cmd += ' '+rand_string[local_counter]
								local_counter += 1
							else:
								cmd += ' '+cube[j]
					cmd += ' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log'
					os.system(cmd)
					fp = open('test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log', 'r')
					data = fp.readlines()[-1]
					fp.close()
					os.system('rm test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log')
					result = data.strip()
					if result == '1':
						minterm = cmd.replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(oracle_path,'').replace(' ','')
						ON_set.append(minterm)
						#print minterm, 'ON_set'
						continue
					else:
						minterm = cmd.replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(oracle_path,'').replace(' ','')
						OFF_set.append(minterm)
						#print minterm, 'OFF_set'
						flag = False
						break 
				if flag == True:
					cube[i] = '-'
				elif flag == False:
					cube[i] = starting_string[i] 
					hard_dc.remove(i)
				cube_string = ''
				for literal in cube:
					cube_string += literal


			else:
				#free_length = cube.count('-')
				free_length = len(soft_dc)
				if free_length<3: 
					flag = True
					for j in range(0,pow(2, free_length)):
						string = int2string(j, free_length)
						local_counter = 0
						cmd = oracle_path
						for j in range(input_size):
							if j in hard_dc:
								if j==i:
									if starting_string[i] == '0':
										cmd += ' 1'
									else:
										cmd += ' 0'
								else:
									cmd += ' ' + str(random.randint(0,1))
							else:
								if j==i:
									if starting_string[i] == '0':
										cmd += ' 1'
									else:
										cmd += ' 0'
								else:
									if cube[j]=='-':
										cmd += ' '+string[local_counter]
										local_counter += 1
									else:
										cmd += ' '+cube[j]
						cmd += ' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log'
						#print cmd
						os.system(cmd)
						num_tested_minterm += 1
						file_name = 'test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log'
						#print file_name
						fp = open('test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','r')
						data = fp.readlines()
						#print data
						data = data[-1]
						fp.close()
						os.system('rm test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log')
						result = data.strip()
						if result == '1':
							minterm = cmd.replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(oracle_path,'').replace(' ','')
							ON_set.append(minterm)
							#print minterm, 'ON_set'
							continue
						else:
							minterm = cmd.replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(oracle_path,'').replace(' ','')
							OFF_set.append(minterm)
							#print minterm, 'OFF_set'
							flag = False
							break
					if flag == True:
						cube[i] = '-'
						if i not in hard_dc:
							soft_dc.append(i)
					elif flag == False:
						cube[i] = starting_string[i] 
						if i in hard_dc:
							hard_dc.remove(i)
					cube_string = ''
					for literal in cube:
						cube_string += literal
				else:
					flag = True
					random_strings = generate_random_strings_firstPI(free_length)
					for string in random_strings:
						local_counter = 0
						cmd = oracle_path
						for j in range(input_size):
							if j==i:
								if starting_string[i] == '0':
									cmd += ' 1'
								else:
									cmd += ' 0'
							else:
								if j in hard_dc:
									cmd += ' '+str(random.randint(0,1) )
								else:
									if cube[j]=='-':
										cmd += ' '+string[local_counter]
										local_counter += 1
									else:
										if cube[j] == '?':
											print('hhhh')
										cmd += ' '+cube[j]
						cmd += ' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log'
						os.system(cmd)
						num_tested_minterm += 1
						fp = open('test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','r')
						data = fp.readlines()[-1]
						fp.close()
						os.system('rm test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log')
						result = data.strip()
						if result == '1':	 
							minterm = cmd.replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(oracle_path,'').replace(' ','')
							#print cmd.replace(oracle_path,'').replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(' ',''), 'ON_set'
							ON_set.append(minterm)
							continue
						else:
							minterm = cmd.replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(oracle_path,'').replace(' ','')
							#print cmd.replace(oracle_path,'').replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(' ',''), 'OFF_set'
							OFF_set.append(minterm)
							flag = False
							break
					if flag == True:
						cube[i] = '-'
						if i not in hard_dc:
							soft_dc.append(i)
					elif flag == False:
						cube[i] = starting_string[i] 
						if i in hard_dc:
							hard_dc.remove(i)
					cube_string = ''
					for literal in cube:
						cube_string += literal 
	cube_string = ''
	for literal in cube:
		cube_string += literal
	exe_time_single_prediction = time.time()-time1
	#print 'num_tested_minterm:\t', num_tested_minterm
	print('found PI:\t', cube_string, '\t\t starting point:\t', starting_string, '\t\tnum of tested minterms:', num_tested_minterm,'\t exe_time_singlePI:', exe_time_single_prediction)
	return cube_string




def expand_from_minterm_2_PI(starting_string, input_size, oracle_path, converge, PIT):
	#print 'starting point:\t', starting_string
	hard_dc = []
	p_dc = 8
	if len(PIT)!=0:
		for i in range(len(PIT[0])):
			flag_dc = 1
			for pi in PIT:
				if pi[i] != '-':
					flag_dc = 0
					break
			if flag_dc == 1:
				hard_dc.append(i)
	soft_dc = []

	time1 = time.time()
	cube = []
	num_tested_minterm = 0
	for literal in starting_string:
		cube.append(literal)
	string_for_cube = ''
	for literal in cube:
		string_for_cube += literal
	#print 'intial cube', string_for_cube
	#print 'before expansion'
	for i in range(0,input_size):
		cube[i] = '?'
		string_for_cube = ''
		for literal in cube:
			string_for_cube += literal
		if i == 0:
			cmd = oracle_path
			for j in range(0, input_size):
				if j==0:
					if starting_string[j]=='1':
						cmd += ' 0'
					else:
						cmd += ' 1'
				else:
					cmd += ' '+starting_string[j] 
			cmd += ' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log'
			os.system(cmd)
			num_tested_minterm += 1
			fp = open('test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','r')
			data	= fp.readlines()[-1]
			fp.close()
			os.system('rm test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log')
			result = data.strip()
			if result == '1':
				minterm = cmd.replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(oracle_path,'').replace(' ','')
				#print minterm, 'ON_set'
				ON_set.append(minterm)
				cube[i] = '-'
				if i not in hard_dc:
					soft_dc.append(i)

			else:
				minterm = cmd.replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(oracle_path,'').replace(' ','')
				#print minterm, 'OFF_set'
				OFF_set.append(minterm)
				cube[i] = starting_string[i]
				if i in hard_dc:
					hard_dc.remove(i)

			cube_string = ''
			for literal in cube:
				cube_string += literal
		else:
			if i in hard_dc:
				random_strings =	generate_random_strings_p(cube.count('-'), 8)
				flag = True
				for rand_string in random_strings:
					cmd = oracle_path
					local_counter = 0
					for j in range(input_size):
						if j==i:
							if starting_string[i] == '0':
								cmd += ' 1'
							else:
								cmd += ' 0'
						else:
							if cube[j] == '-':
								cmd += ' '+rand_string[local_counter]
								local_counter += 1
							else:
								cmd += ' '+cube[j]
					cmd += ' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log'
					os.system(cmd)
					fp = open('test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log', 'r')
					data = fp.readlines()[-1]
					fp.close()
					os.system('rm test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log')
					result = data.strip()
					if result == '1':
						minterm = cmd.replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(oracle_path,'').replace(' ','')
						ON_set.append(minterm)
						#print minterm, 'ON_set'
						continue
					else:
						minterm = cmd.replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(oracle_path,'').replace(' ','')
						OFF_set.append(minterm)
						#print minterm, 'OFF_set'
						flag = False
						break 
				if flag == True:
					cube[i] = '-'
				elif flag == False:
					cube[i] = starting_string[i] 
					hard_dc.remove(i)
				cube_string = ''
				for literal in cube:
					cube_string += literal


			else:
				#free_length = cube.count('-')
				free_length = len(soft_dc)
				if free_length<3: 
					flag = True
					for j in range(0,pow(2, free_length)):
						string = int2string(j, free_length)
						local_counter = 0
						cmd = oracle_path
						for j in range(input_size):
							if j in hard_dc:
								if j==i:
									if starting_string[i] == '0':
										cmd += ' 1'
									else:
										cmd += ' 0'
								else:
									cmd += ' ' + str(random.randint(0,1))
							else:
								if j==i:
									if starting_string[i] == '0':
										cmd += ' 1'
									else:
										cmd += ' 0'
								else:
									if cube[j]=='-':
										cmd += ' '+string[local_counter]
										local_counter += 1
									else:
										cmd += ' '+cube[j]
						cmd += ' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log'
						#print cmd
						os.system(cmd)
						num_tested_minterm += 1
						file_name = 'test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log'
						#print file_name
						fp = open('test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','r')
						data = fp.readlines()
						#print data
						data = data[-1]
						fp.close()
						os.system('rm test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log')
						result = data.strip()
						if result == '1':
							minterm = cmd.replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(oracle_path,'').replace(' ','')
							ON_set.append(minterm)
							#print minterm, 'ON_set'
							continue
						else:
							minterm = cmd.replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(oracle_path,'').replace(' ','')
							OFF_set.append(minterm)
							#print minterm, 'OFF_set'
							flag = False
							break
					if flag == True:
						cube[i] = '-'
						if i not in hard_dc:
							soft_dc.append(i)
					elif flag == False:
						cube[i] = starting_string[i] 
						if i in hard_dc:
							hard_dc.remove(i)
					cube_string = ''
					for literal in cube:
						cube_string += literal
				else:
					flag = True
					random_strings = generate_random_strings(free_length)
					for string in random_strings:
						local_counter = 0
						cmd = oracle_path
						for j in range(input_size):
							if j==i:
								if starting_string[i] == '0':
									cmd += ' 1'
								else:
									cmd += ' 0'
							else:
								if j in hard_dc:
									cmd += ' '+str(random.randint(0,1) )
								else:
									if cube[j]=='-':
										cmd += ' '+string[local_counter]
										local_counter += 1
									else:
										if cube[j] == '?':
											print('hhhh')
										cmd += ' '+cube[j]
						cmd += ' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log'
						os.system(cmd)
						num_tested_minterm += 1
						fp = open('test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','r')
						data = fp.readlines()[-1]
						fp.close()
						os.system('rm test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log')
						result = data.strip()
						if result == '1':	 
							minterm = cmd.replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(oracle_path,'').replace(' ','')
							#print cmd.replace(oracle_path,'').replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(' ',''), 'ON_set'
							ON_set.append(minterm)
							continue
						else:
							minterm = cmd.replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(oracle_path,'').replace(' ','')
							#print cmd.replace(oracle_path,'').replace(' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','').replace(' ',''), 'OFF_set'
							OFF_set.append(minterm)
							flag = False
							break
					if flag == True:
						cube[i] = '-'
						if i not in hard_dc:
							soft_dc.append(i)
					elif flag == False:
						cube[i] = starting_string[i] 
						if i in hard_dc:
							hard_dc.remove(i)
					cube_string = ''
					for literal in cube:
						cube_string += literal 
	cube_string = ''
	for literal in cube:
		cube_string += literal
	exe_time_single_prediction = time.time()-time1
	#print 'num_tested_minterm:\t', num_tested_minterm
	print('found PI:\t', cube_string, '\t\t starting point:\t', starting_string, '\t\tnum of tested minterms:', num_tested_minterm,'\t exe_time_singlePI:', exe_time_single_prediction)
	return cube_string




def unshaded_part(PIT, input_vars_A):
	cnf = []
	for pi in PIT:
		clause = []
		for i in range(len(input_vars_A)):
			if pi[i]=='0':
				clause.append(net2int[input_vars_A[i]])
			elif pi[i]=='1':
				clause.append(-net2int[input_vars_A[i]])
		cnf.append(clause)
	return cnf

def build_predicted_circuit(PIT, input_size):
	input_vars_B = []
	for i in range(input_size):
		input_vars_B.append('b_'+str(i))
	outputs = ['y_pred']
	gates = []
	for in1 in input_vars_B:
		gate = in1.replace('b','c')+'=NOT('+in1+')'
		gates.append(gate)
	for i in range(len(PIT)):
		pi = PIT[i]
		wire_list = []
		j = 0
		while(j<input_size):
			if pi[j]!='-':
				break
			j += 1
		if pi[j]=='1':
			gate = 'w_'+str(i)+'_0=BUF('+input_vars_B[j]+')'
		elif pi[j]=='0':
			gate = 'w_'+str(i)+'_0=NOT('+input_vars_B[j]+')'
		wire_list.append('w_'+str(i)+'_0')
		gates.append(gate)
		j += 1
		while(j<input_size):
			if pi[j]=='-':
				j += 1
				continue
			elif pi[j]=='1':
				gate = 'w_'+str(i)+'_'+str(len(wire_list))+'=AND('+'w_'+str(i)+'_'+str(len(wire_list)-1)+','+input_vars_B[j]+')'
				wire_list.append('w_'+str(i)+'_'+str(len(wire_list)))
			elif pi[j]=='0':
				gate = 'w_'+str(i)+'_'+str(len(wire_list))+'=AND('+'w_'+str(i)+'_'+str(len(wire_list)-1)+','+input_vars_B[j].replace('b','c')+')'
				wire_list.append('w_'+str(i)+'_'+str(len(wire_list)))
			gates.append(gate)
			j += 1
		gate='comparator_'+str(i)+'=BUF('+wire_list[-1]+')'
		gates.append(gate)
	wire_list = []
	for i in range(len(PIT)):
		if i==0:
			gate = 'w_comparator_0=BUF(comparator_0)'
			gates.append(gate)
			wire_list.append('w_comparator_0')
			continue
		gate = 'w_comparator_'+str(len(wire_list))+'=OR('+wire_list[-1]+',comparator_'+str(i)+')'
		wire_list.append('w_comparator_'+str(len(wire_list)))
		gates.append(gate)
	gate = 'y_pred=BUF('+wire_list[-1]+')'		
	gates.append(gate)
	nodes = []
	for gate in gates:
		nodes.append(gate[:gate.find('=')])
	return input_vars_B, outputs, gates, nodes

def build_predicted_circuit_CNF(PIT, input_size, current_counter):
	inputs, outputs, gates, nodes = build_predicted_circuit(PIT, input_size)
	global net_counter
	for idx in range(current_counter+1, net_counter+1):
		if idx in int2net:
			in1 = int2net[idx]
			del int2net[idx]
			del net2int[in1]
	net_counter = current_counter

	for in1 in inputs+nodes:
		if in1 not in net2int:
			net_counter += 1
			net2int[in1] = net_counter
			int2net[net_counter] = in1
	CNF_predict = []
	for gate in gates:
		out = gate[:gate.find('=')]
		gate_type = gate[gate.find('=')+1:gate.find('(')]
		gate_inputs = gate[gate.find('(')+1:gate.find(')')].replace(' ','').split(',')
		if len(gate_inputs)==1:
			in1 = gate_inputs[0]
			if gate_type == 'NOT':
				CNF_predict.append([	 net2int[in1],	net2int[out] ])
				CNF_predict.append([	-net2int[in1], -net2int[out] ])
			elif gate_type == 'BUF':
				CNF_predict.append([	 net2int[in1], -net2int[out] ])
				CNF_predict.append([	-net2int[in1],	net2int[out] ])
		elif len(gate_inputs)==2:
			in1, in2 = gate_inputs
			if gate_type == 'AND':
				CNF_predict.append([	net2int[in1], -net2int[out] ])
				CNF_predict.append([	net2int[in2], -net2int[out] ])
				CNF_predict.append([ -net2int[in1], -net2int[in2],	net2int[out] ])
			elif gate_type == 'NAND':
				CNF_predict.append([	net2int[in1],	net2int[out] ])
				CNF_predict.append([	net2int[in2],	net2int[out] ])
				CNF_predict.append([ -net2int[in1], -net2int[in2], -net2int[out] ])
			elif gate_type == 'OR':
				CNF_predict.append([ -net2int[in1],	net2int[out] ])
				CNF_predict.append([ -net2int[in2],	net2int[out] ])
				CNF_predict.append([	net2int[in1],	net2int[in2], -net2int[out] ])
			elif gate_type == 'NOR':
				CNF_predict.append([ -net2int[in1], -net2int[out] ])
				CNF_predict.append([ -net2int[in2], -net2int[out] ])
				CNF_predict.append([	net2int[in1],	net2int[in2],	net2int[out] ])
			elif gate_type == 'XOR':
				CNF_predict.append([ -net2int[in1],	net2int[in2],	net2int[out] ])
				CNF_predict.append([	net2int[in1], -net2int[in2],	net2int[out] ])
				CNF_predict.append([	net2int[in1],	net2int[in2], -net2int[out] ])
				CNF_predict.append([ -net2int[in1], -net2int[in2], -net2int[out] ])
			elif gate_type == 'XNOR':
				CNF_predict.append([	net2int[in1], -net2int[in2], -net2int[out] ])
				CNF_predict.append([ -net2int[in1],	net2int[in2], -net2int[out] ])
				CNF_predict.append([ -net2int[in1], -net2int[in2],	net2int[out] ])
				CNF_predict.append([	net2int[in1],	net2int[in2],	net2int[out] ])
	return CNF_predict

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

def read_netlist(verilog_netlist):
	fp = open(verilog_netlist,'r')
	data = fp.readlines()
	fp.close()
	eof = len(data)
	num = 0
	gates = []
	nodes = []
	while(num<eof):
		line = data[num].strip()
		num += 1
		if len(line)==0 or line.startswith('//'):
			continue
		elif line.startswith('endmodule'):
			break
		while(line.find(';')==-1):
			line += data[num].strip()
			num += 1
		if line.startswith('input '):
			inputs = line.replace('input ','').replace(';','').replace(' ','').split(',')
		elif line.startswith('output '):
			outputs = line.replace('output ','').replace(';','').replace(' ','').split(',')
		elif line.find('.')!=-1:
			gate_cell = line.split(' ')[0]
			if gate_cell.find('XNOR')!=-1:
				gate_type = 'XNOR'
			elif gate_cell.find('XOR')!=-1:
				gate_type = 'XOR'
			elif gate_cell.find('NOR')!=-1:
				gate_type = 'NOR'
			elif gate_cell.find('NAND')!=-1:
				gate_type = 'NAND'
			elif gate_cell.find('AND')!=-1:
				gate_type = 'AND'
			elif gate_cell.find('OR')!=-1:
				gate_type = 'OR'
			elif gate_cell.find('BUF')!=-1:
				gate_type = 'BUF'
			elif gate_cell.find('INV')!=-1:
				gate_type = 'NOT'
			else:
				print(gate_cell)
			gate_inputs_save = line[line.find('(')+1:line.find(';')-1].replace(' ','').split(',')
			gate_output = gate_inputs_save[-1]
			gate_inputs_save.remove(gate_output)
			gate_output = gate_output[gate_output.find('(')+1:gate_output.find(')')]
			if gate_output.startswith('\\'):
				gate_output = gate_output[gate_output.find('/')+1:]
			gate_inputs = []
			for in1 in gate_inputs_save:
				in1 = in1[in1.find('(')+1:in1.find(')')]
				if in1.startswith('\\'):
					in1 = in1[in1.find('/')+1:]
				gate_inputs.append(in1)
			gate = gate_output+'='+gate_type+'('
			for in1 in gate_inputs:
				gate+=in1+','
			gate+='#'
			gate = gate.replace(',#',')')
			gates.append(gate)
			nodes.append(gate_output)
	return inputs, outputs, gates, nodes

def constraint_bench2cnf(inputs, outputs, gates, nodes):
	CNF_HD = []
	global net_counter
	for in1 in inputs+nodes:
		if in1 not in net2int:
			net_counter += 1
			int2net[net_counter] = in1
			net2int[in1] = net_counter
	for gate in gates:
		out = gate[:gate.find('=')]
		gate_type = gate[gate.find('=')+1:gate.find('(')]
		gate_inputs = gate[gate.find('(')+1:gate.find(')')].replace(' ','').split(',')
		if len(gate_inputs)==1:
			in1 = gate_inputs[0]
			if gate_type == 'NOT':
				CNF_HD.append([	 net2int[in1],	net2int[out] ])
				CNF_HD.append([	-net2int[in1], -net2int[out] ])
			elif gate_type == 'BUF':
				CNF_HD.append([	 net2int[in1], -net2int[out] ])
				CNF_HD.append([	-net2int[in1],	net2int[out] ])
		elif len(gate_inputs)==2:
			in1, in2 = gate_inputs
			if gate_type == 'AND':
				CNF_HD.append([	net2int[in1], -net2int[out] ])
				CNF_HD.append([	net2int[in2], -net2int[out] ])
				CNF_HD.append([ -net2int[in1], -net2int[in2],	net2int[out] ])
			elif gate_type == 'NAND':
				CNF_HD.append([	net2int[in1],	net2int[out] ])
				CNF_HD.append([	net2int[in2],	net2int[out] ])
				CNF_HD.append([ -net2int[in1], -net2int[in2], -net2int[out] ])
			elif gate_type == 'OR':
				CNF_HD.append([ -net2int[in1],	net2int[out] ])
				CNF_HD.append([ -net2int[in2],	net2int[out] ])
				CNF_HD.append([	net2int[in1],	net2int[in2], -net2int[out] ])
			elif gate_type == 'NOR':
				CNF_HD.append([ -net2int[in1], -net2int[out] ])
				CNF_HD.append([ -net2int[in2], -net2int[out] ])
				CNF_HD.append([	net2int[in1],	net2int[in2],	net2int[out] ])
			elif gate_type == 'XOR':
				CNF_HD.append([ -net2int[in1],	net2int[in2],	net2int[out] ])
				CNF_HD.append([	net2int[in1], -net2int[in2],	net2int[out] ])
				CNF_HD.append([	net2int[in1],	net2int[in2], -net2int[out] ])
				CNF_HD.append([ -net2int[in1], -net2int[in2], -net2int[out] ])
			elif gate_type == 'XNOR':
				CNF_HD.append([	net2int[in1], -net2int[in2], -net2int[out] ])
				CNF_HD.append([ -net2int[in1],	net2int[in2], -net2int[out] ])
				CNF_HD.append([ -net2int[in1], -net2int[in2],	net2int[out] ])
				CNF_HD.append([	net2int[in1],	net2int[in2],	net2int[out] ])
	return CNF_HD

	


def build_constraint_CNF(input_size, d):
	if 'n_'+str(input_size)+'_d_'+str(d) in Constraint_CNFs:
		#return Constraint_CNFs['n_'+str(n)+'_d_'+str(d)]
		return 0
	if not os.path.isdir('../middle_process/RTL_constraint/n_'+str(input_size)+'_d_'+str(d)+'/'):
		os.system('mkdir ../middle_process/RTL_constraint/n_'+str(input_size)+'_d_'+str(d)+'/')
	if not os.path.isfile('../middle_process/RTL_constraint/n_'+str(input_size)+'_d_'+str(d)+'/constraint_netlist.v'):
		os.system('cp rtl.tcl ../middle_process/RTL_constraint/n_'+str(input_size)+'_d_'+str(d)+'/.')
		write_RTL(input_size, d)
		os.system('cd ../middle_process/RTL_constraint/n_'+str(input_size)+'_d_'+str(d)+'/; dc_shell -f rtl.tcl > dc.log')
	inputs, outputs, gates, nodes = read_netlist('../middle_process/RTL_constraint/n_'+str(input_size)+'_d_'+str(d)+'/constraint_netlist.v')
	Constraint_CNFs['n_'+str(input_size)+'_d_'+str(d)] = constraint_bench2cnf(inputs, outputs, gates, nodes)
	return 1

def construct_predicted_circuit(inputs, outputs, inputs_pred, outputs_pred, gates_pred, bm_name):
	fp = open('../middle_process/predicted_circuit/'+bm_name+'_converge_'+str(converge)+'.bench','w')
	for in1 in inputs:
		fp.write('INPUT('+in1+')\n')
	for out in outputs:
		fp.write('OUTPUT('+out+')\n')
	for i in range(len(inputs)):
		in1 = inputs[i]
		in2 = inputs_pred[i]
		gate = in2+'=BUF('+in1+')'
		fp.write(gate+'\n')
	for gate in gates_pred:
		fp.write(gate+'\n')
	for i in range(len(outputs)):
		out1 = outputs[i]
		out2 = outputs_pred[i]
		gate = out1+'=BUF('+out2+')'
		fp.write(gate+'\n')
	fp.close()

def construct_predicted_pla(inputs, outputs, PIT, inputs_size, bm_name):
	fp = open('../middle_process/predicted_circuit/'+bm_name+'_converge_'+str(converge)+'.pla','w')
	fp.write('.i '+str(len(inputs))+'\n')
	fp.write('.o 1\n')
	line = '.ilb'
	for in1 in inputs:
		line += ' '+in1
	fp.write(line+'\n')
	fp.write('.ob '+outputs[0]+'\n')
	fp.write('.p '+str(len(PIT))+'\n')
	for pi in PIT:
		fp.write(pi+' 1\n')
	fp.write('.e')
	fp.close()

def build_miter_circuit(inputs, outputs, gates, inputs_pred, outputs_pred, gates_pred, bm_name):
	if not os.path.isdir('../middle_process/miter_circuit_accuracy/'+bm_name+'_converge_'+str(converge)):
		os.system('mkdir ../middle_process/miter_circuit_accuracy/'+bm_name+'_converge_'+str(converge))
	fp1 = open('../middle_process/miter_circuit_accuracy/'+bm_name+'_converge_'+str(converge)+'/miter_xor.bench','w')
	fp2 = open('../middle_process/miter_circuit_accuracy/'+bm_name+'_converge_'+str(converge)+'/miter_xnor.bench','w')
	
	for in1 in inputs:
		fp1.write('INPUT('+in1+')\n')
		fp2.write('INPUT('+in1+')\n')
	fp1.write('OUTPUT(miter_result)\n')
	fp2.write('OUTPUT(miter_result)\n')
	for i in range(len(inputs)):
		in1 = inputs[i]
		in2 = inputs_pred[i]
		gate = in2+'=BUF('+in1+')'
		fp1.write(gate+'\n')
		fp2.write(gate+'\n')
	for gate in gates+gates_pred:
		fp1.write(gate+'\n')
		fp2.write(gate+'\n')
	gate1 = 'miter_result = XOR('+outputs[0]+','+outputs_pred[0]+')'
	fp1.write(gate1+'\n')
	gate2 = 'miter_result = XNOR('+outputs[0]+','+outputs_pred[0]+')'
	fp2.write(gate2+'\n')
	fp1.close()
	fp2.close()	
	
	#cmd = 'cd ../middle_process/miter_circuit_accuracy/'+bm_name+'_converge_'+str(converge)+'/; ~/tool/abc1/abc -c "read_bench miter_xor.bench; collapse; write_pla miter_xor.pla"'
	#os.system(cmd)
	#cmd = 'cd ../middle_process/miter_circuit_accuracy/'+bm_name+'_converge_'+str(converge)+'/; ~/tool/abc1/abc -c "read_bench miter_xnor.bench; collapse; write_pla miter_xnor.pla"'
	#os.system(cmd)	

 

def string_intersect(aaa,bbb):
	string = ''
	for i in range(len(aaa)):
		a = aaa[i]
		b = bbb[i]
		if a=='-':
			string += b
		elif a=='1':
			if b=='0':
				return None
			else:
				string += a
		elif a=='0':
			if b=='1':
				return None	
			else:
				string += a
	return string

def count_error(bm_name, input_size):
	fp = open('../middle_process/miter_circuit_accuracy/'+bm_name+'_converge_'+str(converge)+'/disjoint_xor.pla','r')
	data = fp.readlines()
	fp.close()
	eof = len(data)
	num = 0
	while(num<eof):
		line = data[num].strip()
		num += 1
		if line.startswith('.p '):
			break
	miter_pla = []
	while(num<eof):
		line = data[num].strip()
		num += 1
		if line.find('.e')!=-1:
			break
		miter_pla.append(line.split(' ')[0])

	n_onset = 0

	for i in range(len(miter_pla)):
		pi = miter_pla[i]
		n_onset += pow(2,pi.count('-'))

	print('error rate:\t'+str(100.0*n_onset/pow(2,input_size))+'%')

def random_cnf(CNF_0):
	global int2net
	global net2int

	CNF_0_save = CNF_0
	int2net_save = int2net
	net2int_save = net2int
	
	CNF_0_temp = []
	int2net_temp = {}
	net2int_temp = {}
	
	before_sorting = []
	for key in int2net_save:
		before_sorting.append(key)
	after_sorting = random.sample( before_sorting, len(before_sorting)	)

	key2key_ = {}
	key_2key = {}
	i = 0
	for key in int2net_save:
		key_ = after_sorting[i]
		i += 1
		key2key_[key] = key_
		key_2key[key_] = key

		net = int2net_save[key]
		int2net_temp[key_] = net
		net2int_temp[net] = key_

	for clause in CNF_0_save:
		clause_ = []
		for literal in clause:
			if abs(literal) in int2net_save:
				if literal > 0:
				 clause_.append(key2key_[literal])
				elif literal < 0:
				 clause_.append(-key2key_[-literal])
			else:
				clause_.append(literal)
		CNF_0_temp.append(clause_)
	return CNF_0_temp, int2net_temp, net2int_temp
	
def before_force_0_exit(bm, converge, inputs, outputs):
	fp = open('../middle_process/predicted_circuit/'+bm+'_converge_'+str(converge)+'.pla','w')
	line = '.i '+str(len(inputs))+'\n'
	fp.write(line)
	line = '.o 1\n'
	fp.write(line)
	line = 'ilb'
	for in1 in inputs:
		line += ' '+in1
	line += '\n'
	fp.write(line)
	line = '.ob '+outputs[0]+'\n'
	fp.write(line)
	line = '.p 0\n'
	fp.write(line)
	fp.write('.e')
	fp.close()

	fp = open('../middle_process/predicted_circuit/'+bm+'_converge_'+str(converge)+'.bench','w')
	for in1 in inputs:
		fp.write('INPUT('+in1+')\n')
	for out in outputs:
		fp.write('OUTPUT('+out+')\n')
	line = outputs[0]+'=XOR('+inputs[0]+','+inputs[0]+')\n'
	fp.write(line)
	fp.close()

	#if not os.path.isdir('../middle_process/miter_circuit_accuracy/'+bm+'_converge_'+str(converge)+'/'):
	#	os.system('mkdir ../middle_process/miter_circuit_accuracy/'+bm+'_converge_'+str(converge)+'/')

	#fp = open('../middle_process/miter_circuit_accuracy/'+bm+'_converge_'+str(converge)+'/miter_xor.bench','w')

	
def before_force_1_exit(bm, converge, inputs, outputs):
	fp = open('../middle_process/predicted_circuit/'+bm+'_converge_'+str(converge)+'.pla','w')
	line = '.i '+str(len(inputs))+'\n'
	fp.write(line)
	line = '.o 1\n'
	fp.write(line)
	line = 'ilb'
	for in1 in inputs:
		line += ' '+in1
	line += '\n'
	fp.write(line)
	line = '.ob '+outputs[0]+'\n'
	fp.write(line)
	line = '.p 0\n'
	fp.write(line)
	fp.write('.e')
	fp.close()

	fp = open('../middle_process/predicted_circuit/'+bm+'_converge_'+str(converge)+'.bench','w')
	for in1 in inputs:
		fp.write('INPUT('+in1+')\n')
	for out in outputs:
		fp.write('OUTPUT('+out+')\n')
	line = outputs[0]+'=XNOR('+inputs[0]+','+inputs[0]+')\n'
	fp.write(line)
	fp.close()

	#if not os.path.isdir('../middle_process/miter_circuit_accuracy/'+bm+'_converge_'+str(converge)+'/'):
	#	os.system('mkdir ../middle_process/miter_circuit_accuracy/'+bm+'_converge_'+str(converge)+'/')

	#fp = open('../middle_process/miter_circuit_accuracy/'+bm+'_converge_'+str(converge)+'/miter_xor.bench','w')





def main():
	oracle_path = sys.argv[1]
	global converge
	converge = int(sys.argv[2])
	d_0 = int(sys.argv[3])
	
	second_constraint = float(sys.argv[4])
	
	global bm_name
	bm_name = oracle_path.split('/')[-1]
	bench_path = oracle_path+'.bench'
	inputs, outputs, gates = read_bench(bench_path)
	input_size = len(inputs)
	
	start_time = time.time()
	
	input_vars_A = []
	for i in range(input_size):
		input_vars_A.append('a_'+str(i))

	
	start_time = time.time()

	'''
	if pow(2, input_size)<budget:
		budget = pow(2, input_size)
	'''
	PIT = []

	
	first_ON_string = first_random_minterm(input_size, oracle_path, converge)
	if first_ON_string == None:
		before_force_0_exit(bm_name, converge, inputs, outputs)
		exit(1)

	PI = expand_from_minterm_2_PI_firstPI(first_ON_string, input_size, oracle_path, converge, PIT)
	
	if PI.count('0')+PI.count('1')==0:
		before_force_1_exit(bm_name, converge, inputs, outputs)
		exit(1)

	PIT.append(PI)
	
	

	global int2net, net2int, net_counter
	int2net = {}
	net2int = {}
	net_counter = 0

	for in1 in input_vars_A:
		net_counter += 1
		int2net[net_counter] = in1
		net2int[in1] = net_counter
	
	d = d_0

	counter_converge = 0

	#while(counter_converge<converge):
	while(1):
		if time.time()-start_time > second_constraint:
			break
		#print PIT
		CNF_0 = []
		CNF_unshaded = unshaded_part(PIT, input_vars_A)
		CNF_0.extend(CNF_unshaded)
		flag = build_constraint_CNF(input_size,d)
		CNF_0.extend(Constraint_CNFs['n_'+str(input_size)+'_d_'+str(d)])
		if flag == 1:
			current_counter = net_counter
		CNF_predict = build_predicted_circuit_CNF(PIT, input_size, current_counter)
		CNF_0.extend(CNF_predict)

		#if time.time() - start_time > second_constraint:
		#	break
		counter_converge = 0
		while(counter_converge<converge):
			if time.time() - start_time > second_constraint:
				break
			CNF_0_temp, int2net_temp, net2int_temp = random_cnf(CNF_0)
			solution = pycosat.solve(CNF_0_temp)
			if solution=='UNSAT':
				print('d:\t', d)
				d += 1
				print('UNSAT break')
				break
			tobe_tested_minterm = ''
			for in1 in input_vars_A:
				if net2int_temp[in1] in solution:
					tobe_tested_minterm += '1'
				elif -net2int_temp[in1] in solution:
					tobe_tested_minterm += '0'
				else:
					print('????')
			if tobe_tested_minterm in ON_set:
				print('counter_converge:\t', counter_converge)
				counter_converge = 0
				PI = expand_from_minterm_2_PI(tobe_tested_minterm, input_size, oracle_path, converge, PIT)
				if len(PI.replace('-',''))==0:
					clause = []
					for in1 in input_vars_A:
						if net2int[in1] in solution:
							clause.append(-net2int[in1])
						elif -net2int[in1] in solution:
							clause.append(net2int[in1])
					CNF_0.append(clause)
					continue
				PIT.append(PI)
				#print 'find a PI, next, break'
				d = d_0
				break
			elif tobe_tested_minterm in OFF_set:
				counter_converge += 1
				clause = []
				for in1 in input_vars_A:
					if net2int[in1] in solution:
						clause.append(-net2int[in1])
					elif -net2int[in1] in solution:
						clause.append(net2int[in1])
				CNF_0.append(clause)
			else:
				test_minterm = ''
				for literal in tobe_tested_minterm:
					test_minterm += ' '+literal
				cmd = oracle_path+' '+test_minterm+' > test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log'
				os.system(cmd)
				fp = open('test_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'.log','r')
				data = fp.readlines()
				fp.close()
				response = int(data[-1].strip())
				if response == 1:
					print('counter_converge:\t', counter_converge)
					counter_converge = 0
					ON_set.append(tobe_tested_minterm)
					PI = expand_from_minterm_2_PI(tobe_tested_minterm, input_size, oracle_path, converge, PIT)
					if len(PI.replace('-',''))==0:
						clause = []
						for in1 in input_vars_A:
							if net2int[in1] in solution:
								clause.append(-net2int[in1])
							elif -net2int[in1] in solution:
								clause.append(net2int[in1])
						CNF_0.append(clause)
						continue
					PIT.append(PI)
					#print 'find a PI, next, break'
					d = d_0
					break
				elif response == 0:
					counter_converge += 1
					OFF_set.append(tobe_tested_minterm)
					clause = []
					for in1 in input_vars_A:
						if net2int[in1] in solution:
							clause.append(-net2int[in1])
						elif -net2int[in1] in solution:
							clause.append(net2int[in1])
					CNF_0.append(clause)

				else:
					print('???')
		if counter_converge>=converge:
			d+=1
		
		if time.time() - start_time > second_constraint:
			break

		max_dc = -1
		for pi in PIT:
			if pi.count('-')>max_dc :
				max_dc = pi.count('-')

		if d > input_size:
			print('cannot find more')
			break	


	print('\n\n\n\n')
	print('final predicted circuit PIT')
	print(PIT)

	end_time = time.time() - start_time
	
	print('exe time:', end_time)
	
	inputs_pred, outputs_pred, gates_pred, nodes_pred = build_predicted_circuit(PIT, input_size)
	construct_predicted_circuit(inputs, outputs, inputs_pred, outputs_pred, gates_pred, bm_name)
	construct_predicted_pla(inputs, outputs, PIT, input_size, bm_name)
	
	cmd = '../original_bench/oracle/abc_tool/abc -c "cec ../middle_process/predicted_circuit/'+bm_name+'_converge_'+str(converge)+'.bench '+oracle_path+'.bench" > abc_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'_d0_'+str(d_0)+'_2times_'+str(second_constraint)+'.log'
	os.system(cmd)

	fp = open('abc_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'_d0_'+str(d_0)+'_2times_'+str(second_constraint)+'.log','r')
	data = fp.readlines()[-1]
	fp.close()
	os.system('rm abc_'+oracle_path.split('/')[-1]+'_converge_'+str(converge)+'_d0_'+str(d_0)+'_2times_'+str(second_constraint)+'.log')
	print(data)

	if data.find('equivalent')!=-1:
		print('equivalent!')
	else:
		build_miter_circuit(inputs, outputs, gates, inputs_pred, outputs_pred, gates_pred, bm_name)
	
	
	

main()

