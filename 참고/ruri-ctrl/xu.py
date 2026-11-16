# 파일 올리기 보조: python xu.py <탭번호> <파일경로>  (경로의 역슬래시 이스케이프 문제를 피함)
import json, subprocess, sys, os
d = os.path.dirname(os.path.abspath(__file__))
cmd = {"op": "upload", "tab": int(sys.argv[1]), "selector": "input[type=file]", "files": [sys.argv[2]], "timeout": 30}
print(subprocess.run(['python', '-X', 'utf8', 'x.py', json.dumps(cmd)], capture_output=True, text=True, cwd=d).stdout)
