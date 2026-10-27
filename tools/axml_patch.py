#!/usr/bin/env python3
"""Insert sorted android:visibility=gone attributes into binary Android XML.
Changes selected elements only; leaves unrelated layouts untouched.
"""
import struct
from axml_inspect import pool
U16=lambda b,p:struct.unpack_from('<H',b,p)[0]
U32=lambda b,p:struct.unpack_from('<I',b,p)[0]
def pack16(x):return struct.pack('<H',x)
def pack32(x):return struct.pack('<I',x)
ANDROID_VISIBILITY_ID=0x010100dc
ANDROID_NS='http://schemas.android.com/apk/res/android'

def patch(data, target_ids):
 b=bytes(data);assert U16(b,0)==3 and U32(b,4)==len(b)
 parts=[];p=8;str_idx=None;strings=None
 while p<len(b):
  typ=U16(b,p);size=U32(b,p+4)
  assert size>0,(p,typ,size)
  raw=b[p:p+size];parts.append((typ,raw))
  if typ==1:
   str_idx=len(parts)-1;strings=pool(raw,0)
  p+=size
 assert p==len(b) and strings is not None
 visidx = strings.index('visibility') if 'visibility' in strings else len(strings)
 nsidx=strings.index(ANDROID_NS)
 resource_map=next(raw for typ,raw in parts if typ==0x180)
 resource_count=(len(resource_map)-8)//4
 need_new_string=visidx==len(strings)
 new=[];ids_seen=set();report=[]
 for typ,raw in parts:
  if typ==0x102:
   ext=16;astart=U16(raw,ext+8);asz=U16(raw,ext+10);acount=U16(raw,ext+12)
   attrs=[];rid=None; existing=False
   for j in range(acount):
    offset=ext+astart+asz*j
    nameidx=U32(raw,offset+4);dt=raw[offset+15];value=U32(raw,offset+16)
    if strings[nameidx]=='id' and dt==1: rid=value
    if nameidx==visidx:existing=True
   if rid in target_ids:
    assert not existing,(hex(rid),'already visibility')
    assert len(raw)==ext+astart+asz*acount,(hex(rid),'unexpected tail',len(raw),ext+astart+asz*acount)
    attr=pack32(nsidx)+pack32(visidx)+pack32(0xffffffff)+pack16(8)+bytes([0,0x10])+pack32(8)
    assert len(attr)==20 and asz==20
    # Android binary XML attribute entries must be ordered by resource ID.
    # Appending visibility after layout attributes leaves it ignored on API 30.
    existing_ids=[]
    for j in range(acount):
     idx=U32(raw,ext+astart+asz*j+4)
     existing_ids.append(U32(resource_map,8+idx*4) if idx<resource_count else 0)
    assert existing_ids==sorted(existing_ids),(hex(rid),existing_ids)
    insert_at=next((j for j,x in enumerate(existing_ids) if x>ANDROID_VISIBILITY_ID),acount)
    insert_pos=ext+astart+asz*insert_at
    obj=bytearray(raw[:insert_pos]+attr+raw[insert_pos:])
    # idIndex/classIndex/styleIndex are 1-based indices into attributes.
    for header_off in (ext+14,ext+16,ext+18):
     old=U16(obj,header_off)
     if old>insert_at:struct.pack_into('<H',obj,header_off,old+1)
    struct.pack_into('<H',obj,ext+12,acount+1)
    struct.pack_into('<I',obj,4,len(obj))
    raw=bytes(obj); ids_seen.add(rid);report.append({'id':hex(rid),'element':strings[U32(raw,ext+4)],'new':'visibility=gone'})
  new.append((typ,raw))
 assert ids_seen==set(target_ids),(sorted(map(hex,ids_seen)),sorted(map(hex,target_ids)))
 if need_new_string:
  typ,raw=new[str_idx]
  assert U16(raw,2)==28 and U32(raw,12)==0 and U32(raw,24)==0
  # String pool: offsets at 28; data at stringsStart; the existing data blob is kept byte-for-byte.
  n=U32(raw,8);offset=U32(raw,20);flags=U32(raw,16)
  assert n==len(strings) and flags&0x100
  new_string=b'visibility';suffix=bytes([len(new_string),len(new_string)])+new_string+b'\0'
  off=raw[offset:]
  append_offset=len(off)
  contents=raw[:28]+raw[28:28+4*n]+pack32(append_offset)+off+suffix
  contents+=b'\0'*((-len(contents))%4)
  arr=bytearray(contents)
  struct.pack_into('<I',arr,4,len(arr))
  struct.pack_into('<I',arr,8,n+1)
  struct.pack_into('<I',arr,20,offset+4)
  new[str_idx]=(typ,bytes(arr))
  # Enlarge resource map so that new attribute's string index has Android's visibility resource id.
  rm_idx=next(i for i,(t,_) in enumerate(new) if t==0x180)
  rm=new[rm_idx][1]; count=(len(rm)-8)//4
  assert count<=visidx
  payload=rm[8:]+bytes(4*(visidx-count))+pack32(ANDROID_VISIBILITY_ID)
  rm=rm[:4]+pack32(8+len(payload))+payload
  new[rm_idx]=(0x180,rm)
 else:
  rm=next(raw for typ,raw in new if typ==0x180)
  assert U32(rm,8+4*visidx)==ANDROID_VISIBILITY_ID,hex(U32(rm,8+4*visidx))
 total=8+sum(len(r) for _,r in new)
 output=pack16(3)+pack16(8)+pack32(total)+b''.join(r for _,r in new)
 assert len(output)==total
 return output,report

if __name__=='__main__':
 import zipfile
 with zipfile.ZipFile('/mnt/data/KaScada Smart Craft 1.0.7 (08.02.2026)(1).apk') as z:
  for file,ids in {'res/layout/dialog_choose_import_source.xml':[0x7f09020a], 'res/layout/dialog_modbus_slave.xml':[0x7f0900d6],'res/layout/main_menu.xml':[0x7f0901f7]}.items():
   b,info=patch(z.read(file),ids)
   assert pool(b,8)
   print(file,len(b),info)
