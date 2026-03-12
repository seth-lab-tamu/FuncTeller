import sys
import os
import glob

def main():
	bench = sys.argv[1]
	for single_cone in glob.glob(bench.replace('.bench','_*.bench')):
		bm = single_cone.split('/')[-1].replace('.bench','')
		if not os.path.isfile(bm):
			cmd = 'python3 create_oracle.py '+single_cone+' &'
			os.system(cmd)


main()



# python run_create_oracles.py ./split_to_cone/c880.bench
