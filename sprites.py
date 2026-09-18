import lzma,json,bisect,struct,io,os
from PIL import Image
A='/home/claude/client/assets/'
def load_sheet(fn):
    b=open(A+fn,'rb').read(); i=0
    while b[i]==0: i+=1
    i+=5
    while b[i]&0x80: i+=1
    i+=1
    props=b[i]; dict_size=struct.unpack('<I',b[i+1:i+5])[0]; i+=13
    lc=props%9; r=props//9; lp=r%5; pb=r//5
    d=lzma.LZMADecompressor(format=lzma.FORMAT_RAW,filters=[{'id':lzma.FILTER_LZMA1,'dict_size':dict_size,'lc':lc,'lp':lp,'pb':pb}])
    raw=d.decompress(b[i:])
    return Image.open(io.BytesIO(raw)).convert('RGBA')
cat=[e for e in json.load(open(A+'catalog-content.json')) if e['type']=='sprite']
cat.sort(key=lambda e:e['firstspriteid']); firsts=[e['firstspriteid'] for e in cat]
SIZE={0:(32,32),1:(32,64),2:(64,32),3:(64,64)}
_cache={}
def get_sprite(sid):
    e=cat[bisect.bisect_right(firsts,sid)-1]
    if e['file'] not in _cache: _cache[e['file']]=load_sheet(e['file'])
    sh=_cache[e['file']]; w,h=SIZE[e['spritetype']]; per=sh.width//w
    k=sid-e['firstspriteid']; x=(k%per)*w; y=(k//per)*h
    return sh.crop((x,y,x+w,y+h))
if __name__=='__main__':
    objs={int(k):v for k,v in json.load(open('/home/claude/objs.json')).items()}
    im=Image.new('RGBA',(32*6,64),(60,60,60,255))
    for n,i in enumerate([7414,3031,3043,5917,3432,3281]):
        s=get_sprite(objs[i]['sprites'][0]); print(i,objs[i]['name'],s.size, s.getpixel((0,0)))
        im.paste(s,(n*32,0),s)
    im=im.resize((im.width*3,im.height*3),Image.NEAREST); im.save('/home/claude/test.png')
