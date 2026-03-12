import sys
import os

def main():
  original_oracle_bench = sys.argv[1]
  bm_bench = original_oracle_bench.split('/')[-1]
  cmd1 = 'cp '+original_oracle_bench + ' .'
  os.system(cmd1)
  cmd2 = 'python3 new_gates.py '+bm_bench
  os.system(cmd2)
  
  #exit(1)
  cmd3 = 'python3 prepare.py '+bm_bench
  os.system(cmd3)
  cmd4 = 'python3 split.py oracle.bench'
  os.system(cmd4)



main()
