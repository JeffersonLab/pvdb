import subprocess

DPSH="/adaqfs/home/apar/scripts/printRunStatus"
cmds = [DPSH, 'EB1']
cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE).stdout.read().strip()
nevts = cond_out.split()[2]
print nevts

