import glob,json
def varint(b,i):
    r=0;s=0
    while True:
        x=b[i];i+=1;r|=(x&0x7f)<<s;s+=7
        if not x&0x80: return r,i
def fields(b):
    i=0;n=len(b)
    while i<n:
        k,i=varint(b,i);f,w=k>>3,k&7
        if w==0: v,i=varint(b,i)
        elif w==2:
            l,i=varint(b,i);v=b[i:i+l];i+=l
        elif w==5: v=b[i:i+4];i+=4
        elif w==1: v=b[i:i+8];i+=8
        else: raise Exception('wt %d'%w)
        yield f,w,v
data=open(glob.glob('/home/claude/client/assets/appearances-*.dat')[0],'rb').read()
objs={}
for f,w,v in fields(data):
    if f!=1: continue
    oid=None;name=None;sprites=None;info=None
    for f2,w2,v2 in fields(v):
        if f2==1: oid=v2
        elif f2==4: name=bytes(v2).decode('utf-8','ignore')
        elif f2==2 and sprites is None:
            for f3,w3,v3 in fields(v2):
                if f3==3:
                    ids=[];pw=ph=pd=ly=1
                    for f4,w4,v4 in fields(v3):
                        if f4==5:
                            if w4==0: ids.append(v4)
                            else:
                                j=0
                                while j<len(v4):
                                    x,j=varint(v4,j);ids.append(x)
                        elif f4==1:pw=v4
                        elif f4==2:ph=v4
                        elif f4==3:pd=v4
                        elif f4==4:ly=v4
                    sprites=ids;info=(pw,ph,pd,ly)
    objs[oid]=dict(name=name,sprites=sprites,info=info)
print(len(objs))
for t in (3031,7414,3043,3035,5917):
    print(t,objs.get(t))
json.dump(objs,open('/home/claude/objs.json','w'))
