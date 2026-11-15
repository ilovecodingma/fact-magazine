
import sys,json,base64,urllib.request,os
d=os.path.dirname(os.path.abspath(__file__)); tok=open(d+'/token.txt').read().strip()
cmd=json.loads(sys.argv[1])
req=urllib.request.Request('http://127.0.0.1:8765/cmd',json.dumps(cmd).encode(),{'X-Tok':tok})
r=json.loads(urllib.request.urlopen(req,timeout=cmd.get('timeout',90)+10).read())
if 'data' in r:
    out=cmd.get('out',d+'/shot.png'); open(out,'wb').write(base64.b64decode(r.pop('data'))); r['saved']=out
print(json.dumps(r,ensure_ascii=False))
