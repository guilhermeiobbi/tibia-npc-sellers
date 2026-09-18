import base64,os
t=open('template.html',encoding='utf-8').read()
data=open('data.json',encoding='utf-8').read().replace('</','<\\/')
atlas=base64.b64encode(open('atlas.webp','rb').read()).decode()
t=t.replace('/*ATLAS*/','.spr{background-image:url(data:image/webp;base64,'+atlas+')}').replace('/*DATA*/',data)
os.makedirs('/mnt/user-data/outputs/tibia-onde-vender',exist_ok=True)
open('/mnt/user-data/outputs/tibia-onde-vender/index.html','w',encoding='utf-8').write(t)
print(len(t)//1024,'KB')
