import subprocess
outfile = open('out.txt','w')
errfile = open('err.txt','w')
command = 'cd ~/ncap/neurocaas/ncap_iac/user_profiles/iac_utils && ./deploy.sh /home/ubuntu/ncap/neurocaas/ncap_iac/user_profiles/new-iam-1596421795109-c-0'
process = subprocess.Popen([command],
                stdout=outfile, 
                stderr=errfile,
                shell=True)
process.communicate()
