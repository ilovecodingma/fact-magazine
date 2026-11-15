import sys,json,subprocess
tab=int(sys.argv[1]); code=open(sys.argv[2],encoding='utf-8').read()
cmd=json.dumps({"op":"eval","tab":tab,"code":code,"timeout":60})
print(subprocess.run(['python','-X','utf8','x.py',cmd],capture_output=True,text=True,cwd=__import__('os').path.dirname(__import__('os').path.abspath(__file__))).stdout)
