import struct,zipfile,os
APK=os.environ.get('BLOODSKY_ORIGINAL_APK','/mnt/data/original.apk')
def u16(b,p):return struct.unpack_from('<H',b,p)[0]
def u32(b,p):return struct.unpack_from('<I',b,p)[0]
def dec_len8(b,p):
 v=b[p];p+=1
 if v&0x80:v=((v&0x7f)<<8)|b[p];p+=1
 return v,p

def pool(b,o):
 assert u16(b,o)==1
 h=u16(b,o+2);n=u32(b,o+8);flags=u32(b,o+16);st=u32(b,o+20)
 strs=[]
 for i in range(n):
  p=o+st+u32(b,o+h+4*i)
  if flags&256:
   l,p=dec_len8(b,p);m,p=dec_len8(b,p)
   value=b[p:p+m].decode('utf-8','replace')
  else:
   l=u16(b,p);p+=2
   if l&0x8000:l=(l&0x7fff)<<16|u16(b,p);p+=2
   value=b[p:p+l*2].decode('utf-16le','replace')
  strs.append(value)
 return strs

def inspect(path):
 with zipfile.ZipFile(APK) as z:b=z.read(path)
 p=8;strs=[];items=[]
 while p<len(b):
  typ=u16(b,p);hdr=u16(b,p+2);n=u32(b,p+4)
  if typ==1:strs=pool(b,p)
  if typ==0x102:
   ext=p+16; nameidx=u32(b,ext+4)
   attrstart=u16(b,ext+8);attrsize=u16(b,ext+10);acount=u16(b,ext+12)
   attrs=[]
   for j in range(acount):
    k=ext+attrstart+j*attrsize
    aid=u32(b,k+4);raw=u32(b,k+8);dtype=b[k+15];data=u32(b,k+16)
    attrs.append((k,strs[aid],strs[raw] if raw<0xffffffff else '',hex(dtype),hex(data)))
   items.append((strs[nameidx],attrs))
  p+=n
 assert p==len(b)
 print('XML',path,'strings',len(strs),'visibilityidx',strs.index('visibility') if 'visibility' in strs else None)
 for name,attrs in items:
  if any('ll_download' in str(a) or 'chKaScadaCloud' in str(a) or a[1]=='visibility' for a in attrs):
   print('NODE',name)
   for a in attrs:print(' ',a)
 return strs,items
if __name__=='__main__':
 for path in ['res/layout/dialog_choose_import_source.xml','res/layout/dialog_modbus_slave.xml','res/layout/main_menu.xml']:
  inspect(path)
