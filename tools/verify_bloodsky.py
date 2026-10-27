#!/usr/bin/env python3
"""Static integrity check; this DOES NOT confirm the application runs on Android."""
import os,zipfile,struct,hashlib,json,zlib
from pathlib import Path
from dex_patch import Dex,PATCHES,APK
from axml_inspect import pool
from arsc_patch import U16,U32
signed=Path(os.environ.get("BLOODSKY_SIGNED_APK","out/BLOODSKY-QA.apk"))
report_path=Path(os.environ.get("BLOODSKY_VERIFY_REPORT","out/static-verification.json"))
modified={"classes.dex","classes2.dex","resources.arsc",
"res/layout/main_menu.xml","res/layout/dialog_choose_import_source.xml",
"res/layout/dialog_modbus_slave.xml"}
with zipfile.ZipFile(APK) as o, zipfile.ZipFile(signed) as z:
 assert o.testzip() is None and z.testzip() is None
 existing=set(o.namelist())
 excluded={n for n in existing if n.startswith("META-INF/") and n.upper().endswith((".SF",".RSA",".DSA",".EC","MANIFEST.MF"))}
 assert existing-excluded<=set(z.namelist())
 for name in existing-excluded-modified:
  assert o.read(name)==z.read(name),("unplanned file change",name)
 assert {n for n in modified if o.read(n)!=z.read(n)}==modified
 count=0
 for name,edits in PATCHES.items():
  old=Dex(o.read(name));new=Dex(z.read(name))
  assert old.mids==new.mids and set(old.methods)==set(new.methods)
  assert hashlib.sha1(new.b[32:]).digest()==new.b[12:32]
  assert zlib.adler32(new.b[12:])&0xffffffff==struct.unpack_from("<I",new.b,8)[0]
  editkeys=set()
  for klass,method,descriptor,mode in edits:
   key=(klass,method,descriptor);editkeys.add(key)
   off,_=old.methods[key];new_off,_=new.methods[key]
   assert off and new_off==off
   assert old.b[off:off+16]==new.b[off:off+16]
   prefix=bytes(new.b[off+16:off+20])
   if mode=="true":assert prefix==b"\x12\x10\x0f\x00"
   if mode=="false":assert prefix==b"\x12\x00\x0f\x00"
   if mode=="void":assert prefix[:2]==b"\x0e\x00"
   count+=1
  for key,(off,_) in old.methods.items():
   if off==0 or key in editkeys:continue
   size=struct.unpack_from("<I",old.b,off+12)[0]
   assert size==struct.unpack_from("<I",new.b,off+12)[0]
   assert old.b[off:off+16+size*2]==new.b[off:off+16+size*2],key
 assert count==15
 assert pool(z.read("resources.arsc"),12).count("BLOODSKY")>=2
 for path,target in {
  "res/layout/main_menu.xml":0x7f0901f7,
  "res/layout/dialog_modbus_slave.xml":0x7f0900d6,
  "res/layout/dialog_choose_import_source.xml":0x7f09020a}.items():
  data=z.read(path);assert U16(data,0)==3 and U32(data,4)==len(data)
  off=8;names=[];resource_ids=[];seen=0
  while off<len(data):
   typ=U16(data,off);size=U32(data,off+4)
   assert size>0
   if typ==1:names=pool(data,off)
   if typ==0x180:resource_ids=[U32(data,off+8+4*j) for j in range((size-8)//4)]
   if typ==0x102:
    a=off+16;start=U16(data,a+8);stride=U16(data,a+10);n=U16(data,a+12)
    id_value=None;visibility=None;attribute_resource_ids=[]
    for i in range(n):
     at=a+start+i*stride
     idx=U32(data,at+4)
     name=names[idx]
     attribute_resource_ids.append(resource_ids[idx] if idx<len(resource_ids) else 0)
     if name=="id":id_value=U32(data,at+16)
     if name=="visibility":visibility=U32(data,at+16)
    if id_value==target:
     assert attribute_resource_ids==sorted(attribute_resource_ids),(path,"attributes out of Android resource ID order")
     assert 0x010100dc in attribute_resource_ids
     expected_visibility=1 if target==0x7f0901f7 else 2
     assert visibility==expected_visibility,(path,id_value,visibility)
     seen+=1
   off+=size
  assert off==len(data) and seen==1,path
result={"status":"STATIC_CHECK_PASS_NOT_ANDROID_ACCEPTANCE","changed_files":sorted(modified),
"patched_dex_methods":count,"original_sha256":hashlib.sha256(APK.read_bytes()).hexdigest(),
"signed_sha256":hashlib.sha256(signed.read_bytes()).hexdigest(),
"android_runtime_test":"NOT_RUN_BY_STATIC_VERIFIER"}
report_path.parent.mkdir(parents=True,exist_ok=True)
report_path.write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
