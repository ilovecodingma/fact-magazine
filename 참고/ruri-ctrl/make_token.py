# 접근 토큰을 새로 만들어 token.txt(서버·클라이언트용)와 token.js(확장용)에 같이 적는다.
import secrets, os
d = os.path.dirname(os.path.abspath(__file__))
t = secrets.token_hex(16)
open(os.path.join(d, 'token.txt'), 'w').write(t)
open(os.path.join(d, 'token.js'), 'w').write("const TOK='%s';\n" % t)
print('토큰을 새로 만들었습니다. 확장을 chrome://extensions 에서 새로고침하세요.')
