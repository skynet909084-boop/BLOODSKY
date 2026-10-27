#!/usr/bin/env python3
"""Safe scoped Android resources.arsc changes for the decoded Craft 1.0.7 reference.
Rewrites string pool offsets, preserving all resource IDs, and shrinks chooseNewConnection from 4 to 3 values.
"""
import struct
from axml_inspect import pool
U16=lambda b,p:struct.unpack_from('<H',b,p)[0]
U32=lambda b,p:struct.unpack_from('<I',b,p)[0]
def short(n):
 if n < 0x80:return bytes([n])
 if n < 0x8000:return bytes([0x80|(n>>8),n&255])
 raise ValueError('length')

def change_global_pool(raw,replacements):
 assert U16(raw,0)==1 and U16(raw,2)==28
 n=U32(raw,8);styles=U32(raw,12);flags=U32(raw,16);starts=U32(raw,20)
 assert flags&0x100
 names=pool(raw,0)
 positions=[U32(raw,28+4*i) for i in range(n)]
 assert len(names)==n and len(set(positions))==n and positions==sorted(positions)
 entries=[];matched={s:0 for s in replacements}
 styles_start=U32(raw,24)
 data=raw[starts:styles_start if styles_start else len(raw)]
 styles_data=raw[styles_start:] if styles_start else b''
 for i,s in enumerate(names):
  old=data[positions[i]:positions[i+1] if i+1<n else len(data)]
  if s in replacements:
   new=replacements[s].encode('utf-8')
   old=short(len(replacements[s]))+short(len(new))+new+b'\0'
   matched[s]+=1
  entries.append(old)
 for s,count in matched.items():assert count==1,(s,count)
 offsets=[];q=0
 for x in entries:offsets.append(q);q+=len(x)
 payload=b''.join(entries)
 payload+=b'\0'*(-len(payload)%4)
 out=bytearray(raw[:28]+b''.join(struct.pack('<I',o) for o in offsets)+raw[28+4*n:starts]+payload+styles_data)
 if styles_start:struct.pack_into('<I',out,24,starts+len(payload))
 struct.pack_into('<I',out,4,len(out))
 assert pool(out,0)[names.index('KaScada')]=='BLOODSKY'
 return bytes(out)

def patch(data):
 b=bytes(data);assert U16(b,0)==2 and U16(b,2)==12 and U32(b,4)==len(b)
 table=bytearray(b[:12]);p=12;parts=[];report=[]
 while p<len(b):
  t=U16(b,p);h=U16(b,p+2);sz=U32(b,p+4);raw=b[p:p+sz]
  if t==1:
   raw=change_global_pool(raw,{'KaScada':'BLOODSKY','KaScada Smart Craft':'BLOODSKY'})
   report.append('App name and home-screen title changed in global resource string pool')
  elif t==0x200:
   pkg=bytearray(raw);q=h;changed=0
   while q<len(pkg):
    subtype=U16(pkg,q);header=U16(pkg,q+2);size=U32(pkg,q+4)
    if subtype==0x201 and pkg[q+8]==3:
     entries=U32(pkg,q+12);data_off=U32(pkg,q+16)
     if entries>5:
      offset=U32(pkg,q+header+20)
      if offset != 0xffffffff:
       entry=q+data_off+offset
       esz,flags,key=struct.unpack_from('<HHI',pkg,entry)
       if esz==16 and flags&1:
        count=U32(pkg,entry+12)
        assert count==4,(entry,count)
        # Original three allowed transport choices: WiFi, Bluetooth, USB.
        struct.pack_into('<I',pkg,entry+12,3)
        changed+=1
    q+=size
   assert q==len(pkg) and changed==2,changed
   raw=bytes(pkg);report.append('Removed 4th KaScada Cloud item from chooseNewConnection array in 2 resource configurations')
  parts.append(raw);p+=sz
 assert p==len(b)
 result=bytearray(table+b''.join(parts));struct.pack_into('<I',result,4,len(result))
 assert U32(result,4)==len(result)
 return bytes(result),report
if __name__=='__main__':
 import zipfile
 with zipfile.ZipFile('/mnt/data/KaScada Smart Craft 1.0.7 (08.02.2026)(1).apk') as z:
  b,r=patch(z.read('resources.arsc'))
 print(len(b),r)
