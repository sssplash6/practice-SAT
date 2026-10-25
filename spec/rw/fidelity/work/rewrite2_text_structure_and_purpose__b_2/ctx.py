import re,sys
txt=open(sys.argv[1],encoding='utf-8').read().replace('\r','')
m=re.search(r'\*\*\* ?START OF.*?\*\*\*', txt); txt=txt[m.end():] if m else txt; txt=txt.split('*** END OF')[0]
paras=[re.sub(r'\s+',' ',p).strip() for p in txt.split('\n\n')]
a,b=int(sys.argv[2]),int(sys.argv[3])
for i in range(a,b): print('#',i,paras[i]); print()
