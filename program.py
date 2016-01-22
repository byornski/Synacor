from __future__ import print_function
import struct
import sys
    
class prog:

    #All calculations are to be modulo this number
    __mod = 32768
    
    def __init__(self,filename):
        '''Read filename as a program into memory'''
        with open(filename,"rb") as f:
            d = f.read()
        self.data = map(''.join, zip(*[iter(d)]*2))
        self.max_pos = len(self.data) - 1

        self.position = 0
        
        self.registers = [0]*8
        self.stack = []

        
    def run(self):
        '''Run the program in memory'''
        #Iterate over operations in program order
        for op in self:
            self.performOp(op)

    def performOp(self,op):
        if op==0: # END
            return
        elif op==1: #set
            reg,val = self.getNext('RV')
            self.set(reg,val)
        elif op==2: #push
            a = self.getNext('V')
            self.push(a)
        elif op==3: #pop
            a = self.getNext('R')
            self.set(a,self.pop())
        elif op==4: #eq - a<= b==c
            a,b,c = self.getNext('RVV')
            res = 1 if b==c else 0
            self.set(a,res)
        elif op==5: #gt
            a,b,c = self.getNext('RVV')
            res = 1 if b>c else 0
            self.set(a,res)
        elif op==6: #jmp
            target = self.getNext('V')
            self.jmp(target)
        elif op==7: #JNZ
            test,target = self.getNext('VV')
            if (test != 0):
                self.jmp(target)
        elif op==8: #JEZ 
            test,target = self.getNext('VV')
            if (test == 0):
                self.jmp(target)
        elif op==9: #a <= b+c
            a,b,c = self.getNext('RVV')
            self.set(a,(b+c)%self.__mod)
        elif op==10: #mult
            a,b,c = self.getNext('RVV')
            self.set(a,(b*c)%self.__mod)
        elif op==11: #mod
            a,b,c = self.getNext('RVV')
            self.set(a,b%c)
        elif op==12: #Binary and
            a,b,c = self.getNext('RVV')
            self.set(a,b&c)
        elif op==13: #binary or
            a,b,c = self.getNext('RVV')
            self.set(a,b|c)
        elif op==14:
            a,b = self.getNext('RV')
            self.set(a,~b%self.__mod)
        elif op==15: #rmem
            a,b = self.getNext('RV')
            self.set(a,self.rmem(b))
        elif op==16: #wmem
            a,b = self.getNext('VV')
            self.wmem(a,b)
        elif op==17:
            target = self.getNext('V')
            self.push(self.Pos())
            self.jmp(target)
        elif op==18:
            target = self.pop()
            self.jmp(target)
        elif op==19: # PRINT CHAR
            s = self.getNext('V')
            print(chr(s),end="")
        elif op==20:
            target = self.getNext('R')
            st = sys.stdin.read(1)
            self.set(target,ord(st))
        elif op==21: #NOOP
            pass 
        else:
            raise Exception("Unknown Op", op, self.position)
        
        
    #Register interaction
    def set(self,reg,val):
        """Set the value of a register"""
        self.registers[reg] = val

    def get(self,reg):
        """Get the value of a register"""
        return self.registers[reg]

    #Stack interactions
    def push(self,x):
        """Put something on to the stack"""
        self.stack.append(x)

    def pop(self):
        """Get the top element of the stack"""
        return self.stack.pop()

    #Direct memory access
    def rmem(self,loc):
        '''Read memory at location'''
        return self._unpack(self.data[loc])

    def wmem(self,loc,val):
        '''Write memory at location'''
        self.data[loc] = self._pack(val)

    #Iterator for program data
    def next(self):
        '''Get the next line from the program at the current position'''
        stri = self.data[self.position]
        byte = self._unpack(stri)
        self.position += 1
        return byte

    def __iter__(self):
        return self

    #Operand reading instructions
    def getNext(self,vals_desired):
        '''Return the following data blocks as either register numbers or resolved memory values'''
        ret = [self._nextReg() if v == "R" else self._nextValue() for v in vals_desired]
        if len(ret) == 1:
            return ret[0]
        else:
            return ret
        
    def _nextValue(self):
        """Resolve and return the next item in memory"""
        x = self.next()
        if (x >= 0):
            return x
        else:
            return self.get(self._register_number(x)) 

    def _nextReg(self):
        '''Get the next data block as a register number'''
        return self._register_number(self.next())

    def _register_number(self,v):
        """Convert register numbers into indexes"""
        return v + 32768        
        
    #Binary format conversion
    def _pack(self,x):
        '''Pack data block into program format'''
        return struct.pack("<h",x)
    
    def _unpack(self,x):
        '''Unpack data block from program format'''
        return struct.unpack("<h",x)[0]
    
    #Jump Instructions    
    def jmp(self,pos):
        '''Move instruction pointer to pos'''
        self.position = pos 

    def Pos(self):
        '''Return the current instruction pointer'''
        return self.position
    
#prog('challenge.bin').run()


