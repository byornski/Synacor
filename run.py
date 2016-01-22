#!/usr/bin/env python
from __future__ import print_function
import struct
import sys


def run(mp):
    op = mp.GetNext()

    mod = 32768
    
    while(op):

        if op==0: # END
            return
        elif op==1: #set
            reg,val = mp.GetRV()
            mp.set(reg,val)
        elif op==2: #push
            a = mp.GetV()
            mp.push(a)
        elif op==3: #pop
            a = mp.GetR()
            mp.set(a,mp.pop())
        elif op==4: #eq - a<= b==c
            a,b,c = mp.GetRVV()
            res = 1 if b==c else 0
            mp.set(a,res)
        elif op==5: #gt
            a,b,c = mp.GetRVV()
            res = 1 if b>c else 0
            mp.set(a,res)
        elif op==6: #jmp
            target = mp.GetV()
            mp.JumpTo(target)
        elif op==7: #JNZ
            test,target = mp.GetVV()
            if (test != 0):
                mp.JumpTo(target)
        elif op==8: #JEZ 
            test,target = mp.GetVV()
            if (test == 0):
                mp.JumpTo(target)
        elif op==9: #a <= b+c
            a,b,c = mp.GetRVV()
            mp.set(a,(b+c)%mod)
        elif op==10: #mult
            a,b,c = mp.GetRVV()
            mp.set(a,(b*c)%mod)
        elif op==11: #mod
            a,b,c = mp.GetRVV()
            mp.set(a,b%c)
        elif op==12: #Binary and
            a,b,c = mp.GetRVV()
            mp.set(a,b&c)
        elif op==13: #binary or
            a,b,c = mp.GetRVV()
            mp.set(a,b|c)
        elif op==14:
            a,b = mp.GetRV()
            mp.set(a,~b%mod)
        elif op==15: #rmem
            a,b = mp.GetRV()
            mp.set(a,mp.rmem(b))
        elif op==16: #wmem
            a,b = mp.GetVV()
            mp.wmem(a,b)
        elif op==17:
           target = mp.GetV()
           mp.push(mp.Pos())
           mp.JumpTo(target)
        elif op==18:
            target = mp.pop()
            mp.JumpTo(target)
        elif op==19: # PRINT CHAR
            s = mp.GetNextValue()
            print(chr(s),end="")
        elif op==20:
            target = mp.GetR()
            st = sys.stdin.read(1)
            mp.set(target,ord(st))
        elif op==21: #NOOP
            pass 
        else:
            pass
            raise Exception("Unknown Op", op, mp.position)
        op = mp.GetNext()


    
class prog:
    def __init__(self,filename):
        with open(filename,"rb") as f:
            d = f.read()

        self.data = map(''.join, zip(*[iter(d)]*2))

        self.position = 0
        self.max_pos = len(self.data) - 1
        self.registers = [0]*8
        self.stack = []

    def set(self,reg,val):
        self.registers[reg] = val

    def get(self,reg):
        return self.registers[reg]

    def push(self,x):
        self.stack.append(x)

    def pop(self):
        return self.stack.pop()
        
    def GetNextValue(self):
        x = self.GetNext()
        if (x >= 0):
            return x
        else:
            return self.get(self.register_number(x)) 

    def register_number(self,v):
        return v + 32768        
        
    def GetNextReg(self):
        return self.register_number(self.GetNext())
        
    def rmem(self,loc):
        return self._unpack(self.data[loc])

    def wmem(self,loc,val):
        self.data[loc] = self._pack(val)

    def _pack(self,x):
        return struct.pack("<h",x)

    
    def _unpack(self,x):
        return struct.unpack("<h",x)[0]
    
    def GetNext(self):
        stri = self.data[self.position]
        byte = self._unpack(stri)
        self.position += 1
        return byte

    def GetR(self):
        return self.GetNextReg()

    def GetV(self):
        return self.GetNextValue()
    
    def GetRV(self):
        return self.GetNextReg(), self.GetNextValue()
    
    def GetVV(self):
        return self.GetNextValue(), self.GetNextValue()
    
    def GetRVV(self): #Get Reg val val tuple
        return self.GetNextReg(), self.GetNextValue(), self.GetNextValue()
    
    def JumpTo(self,pos):
        self.position = pos 

    def Pos(self):
        return self.position
mp = prog('challenge.bin')

run(mp)

