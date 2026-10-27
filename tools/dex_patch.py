#!/usr/bin/env python3
"""Fixed-size method body changes in original Dex; does not rebuild resource XML."""
import hashlib, struct, zlib, zipfile, pathlib, argparse, json, os
APK=pathlib.Path(os.environ.get('BLOODSKY_ORIGINAL_APK','/mnt/data/KaScada Smart Craft 1.0.7 (08.02.2026)(1).apk'))
OUT=pathlib.Path(os.environ.get('BLOODSKY_UNSIGNED_APK','/mnt/data/BLOODSKY-Craft107-experimental-unsigned.apk'))
EXPECTED='11464db76f59393ccf698f57e60af1756756ffc78cb315d43052ae92adb50d4f'
def u2(b,o): return struct.unpack_from('<H',b,o)[0]
def u4(b,o): return struct.unpack_from('<I',b,o)[0]
def leb(b,o):
 v=s=0
 for i in range(5):
  x=b[o+i];v|=(x&0x7f)<<s;s+=7
  if x<128:return v,o+i+1
 raise ValueError('invalid uleb')
class Dex:
 def __init__(self,data):
  self.b=bytearray(data);b=self.b
  assert b[:3]==b'dex' and u4(b,32)==len(b)
  n,o=u4(b,56),u4(b,60);self.strings=[]
  for j in range(n):
   p=u4(b,o+4*j);_,p=leb(b,p);end=b.index(0,p)
   self.strings.append(bytes(b[p:end]).decode('utf-8','replace'))
  n,o=u4(b,64),u4(b,68);self.types=[self.strings[u4(b,o+4*j)] for j in range(n)]
  n,o=u4(b,72),u4(b,76);self.protos=[]
  for j in range(n):
   k=o+12*j;ret=self.types[u4(b,k+4)];params=u4(b,k+8)
   ps=''.join(self.types[u2(b,params+4+2*e)] for e in range(u4(b,params))) if params else ''
   self.protos.append('('+ps+')'+ret)
  n,o=u4(b,88),u4(b,92);self.mids=[]
  for j in range(n):
   k=o+8*j;self.mids.append((self.types[u2(b,k)],self.strings[u4(b,k+4)],self.protos[u2(b,k+2)]))
  n,o=u4(b,96),u4(b,100);self.methods={}
  for j in range(n):
   k=o+j*32;klass=self.types[u4(b,k)];p=u4(b,k+24)
   if not p:continue
   sf,p=leb(b,p);inf,p=leb(b,p);dm,p=leb(b,p);vm,p=leb(b,p)
   for _ in range(sf+inf):_,p=leb(b,p);_,p=leb(b,p)
   for nn in [dm,vm]:
    idx=0
    for _ in range(nn):
     delta,p=leb(b,p);idx+=delta;access,p=leb(b,p);code,p=leb(b,p)
     c,name,proto=self.mids[idx];assert c==klass,(c,klass)
     self.methods[(c,name,proto)]=(code,access)
  self.edits=[]
 def get(self,c,n,s):return self.methods.get((c,n,s))
 def patch(self,c,n,s,mode):
  found=self.get(c,n,s)
  if not found:raise KeyError((c,n,s))
  code,acc=found
  if not code:raise ValueError((c,n,s,'no code'))
  b=self.b;old_insns=u4(b,code+12);regs=u2(b,code)
  if mode=='void':ins=[0x000e]
  elif mode=='true':ins=[0x1012,0x000f]
  elif mode=='false':ins=[0x0012,0x000f]
  else:raise ValueError(mode)
  if old_insns<len(ins) or regs<(1 if len(ins)>1 else 0):raise ValueError((c,n,s,old_insns,regs))
  width1={0x00,0x01,0x04,0x07,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0x12,0x1d,0x1e,0x21,0x27,0x28}
  width2=set([0x02,0x05,0x08,0x13,0x15,0x16,0x19,0x1a,0x1c,0x1f,0x20,0x22,0x23,0x29]+list(range(0x2d,0x3e))+list(range(0x44,0x6e))+list(range(0x90,0xb0))+list(range(0xd0,0xe3)))
  width3=set([0x03,0x06,0x09,0x14,0x17,0x1b,0x24,0x25,0x26,0x2a,0x2b,0x2c]+list(range(0x6e,0x73))+list(range(0x74,0x79)))
  width1.update(range(0x7b,0x90));width1.update(range(0xb0,0xd0))
  prefix=0
  while prefix<len(ins):
   opcode=b[code+16+prefix*2]
   if opcode in width1:w=1
   elif opcode in width2:w=2
   elif opcode in width3:w=3
   elif opcode==0x18:w=5
   else:raise ValueError(('unsupported first instruction',c,n,s,hex(opcode)))
   prefix+=w
  assert old_insns>=prefix
  struct.pack_into('<'+'H'*prefix,b,code+16,*(ins+[0]*(prefix-len(ins))))
  self.edits.append({'class':c,'method':n+s,'mode':mode,'code_offset':code,'original_code_units':old_insns,'patched_prefix_code_units':prefix})
 def output(self):
  b=self.b;b[12:32]=hashlib.sha1(b[32:]).digest()
  struct.pack_into('<I',b,8,zlib.adler32(b[12:])&0xffffffff)
  assert hashlib.sha1(b[32:]).digest()==b[12:32]
  assert zlib.adler32(b[12:])&0xffffffff==u4(b,8)
  return bytes(b)
C='Lru/himik/nightscream/kascada/'
PATCHES={
 'classes.dex':[
 (C+'mbCanvas;','K','(Landroid/view/View;)Z','true'),
 (C+'mbCanvas;','Q','(Landroid/content/DialogInterface;I)V','void'),
 (C+'q/f/b;','e','()V','void'),
 (C+'Connections/Cloud/CloudConnector;','run','()V','void'),
 (C+'Connections/Cloud/a;','run','()V','void'),
 (C+'Connections/Cloud/b;','run','()V','void'),
 (C+'Bd/Export/ExportPresenter;','uploadProjectToServer','(Ljava/lang/String;Ljava/io/File;Ljava/lang/String;)V','void'),
 (C+'Bd/Export/ExportPresenter;','onClickQr','(Lk/a/a/a;)V','void'),
 (C+'Bd/Export/ProjectExportActivity;','checkLicense','()Z','true')],
 'classes2.dex':[
 (C+'Utils/l;','d','()V','void'),
 (C+'Utils/l;','f','()Z','true'),
 (C+'Utils/l;','k','()Z','true'),
 (C+'Utils/l;','l','()Z','true'),
 (C+'Utils/l;','p','(Ljava/lang/String;)Z','true'),
 (C+'Firebase/MyFirebaseMessagingService;','q','(Lcom/google/firebase/messaging/s0;)V','void')]}
def main():
 assert hashlib.sha256(APK.read_bytes()).hexdigest()==EXPECTED
 OUT.parent.mkdir(parents=True,exist_ok=True)
 orig=zipfile.ZipFile(APK);patched={};report=[]
 for name,items in PATCHES.items():
  d=Dex(orig.read(name))
  for c,n,s,mode in items:d.patch(c,n,s,mode)
  patched[name]=d.output();report+=d.edits
 from arsc_patch import patch as arsc_patch
 from axml_patch import patch as axml_patch
 data,other=arsc_patch(orig.read('resources.arsc'));patched['resources.arsc']=data
 xml_targets={'res/layout/dialog_choose_import_source.xml':[0x7f09020a],
 'res/layout/dialog_modbus_slave.xml':[0x7f0900d6],
 'res/layout/main_menu.xml':[0x7f0901f7]}
 for file,ids in xml_targets.items():
  output,changes=axml_patch(orig.read(file),ids);patched[file]=output
  other.extend([file+': '+x['element']+' visibility=gone' for x in changes])
 with zipfile.ZipFile(OUT,'w') as z:
  for inf in orig.infolist():
   if inf.filename.startswith('META-INF/') and inf.filename.upper().endswith(('.SF','.RSA','.DSA','.EC','MANIFEST.MF')):continue
   z.writestr(inf,patched.get(inf.filename,orig.read(inf.filename)))
 with zipfile.ZipFile(OUT) as z:
  for name,items in PATCHES.items():
   d=Dex(z.read(name))
   for c,n,s,_ in items:assert d.get(c,n,s),(c,n,s)
  assert z.testzip() is None
 pathlib.Path(os.environ.get('BLOODSKY_PATCH_LOG','/mnt/data/BLOODSKY_Craft107_dex_change_log.json')).write_text(json.dumps({'dex':report,'resources':other},indent=2),encoding='utf-8')
 from axml_inspect import pool
 with zipfile.ZipFile(OUT) as z:
  a=z.read('resources.arsc');assert pool(a,12).count('BLOODSKY')>=2
  for file in xml_targets:assert pool(z.read(file),8)
 print('resource patching',other)
 print('patched methods',len(report),'APK',OUT,OUT.stat().st_size,'sha256',hashlib.sha256(OUT.read_bytes()).hexdigest())
if __name__=='__main__':main()
