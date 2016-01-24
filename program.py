from __future__ import print_function
import struct
import sys
    
class prog:
    
    def __init__(self,filename):
        '''Read filename as a program into memory'''
        with open(filename,"rb") as f:
            d = f.read()
        self.data = map(''.join, zip(*[iter(d)]*2))
        self.max_pos = len(self.data) - 1

        self.position = 0
        self.registers = [0]*8
        self.stack = []

        self.ops = operations(self)
        
        
    def run(self):
        '''Run the program in memory'''
        #Iterate over operations in program order
        for op in self:
            cont = self.ops.performOp(op)
            if not cont: break
    
    
    def setReg(self):
        reg,val = self.getNext('RV')
        self.set(reg,val)
        
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




class operations:
    
    #All calculations are to be modulo this number
    __mod = 32768

    def __init__(self,target):
        self.parent = target
            
    def performOp(self,op):

        operation_dictionary = {
            1: self._set,
            2: self._push,
            3: self._pop,
            4: self._eq,
            5: self._gt,
            6: self._jmp,
            7: self._jnz,
            8: self._jez,
            9: self._add,
            10: self._mult,
            11: self._mod,
            12: self._and,
            13: self._or,
            14: self._not,
            15: self._rmem,
            16: self._wmem,
            17: self._call,
            18: self._ret,
            19: self._out,
            20: self._in,
            21: self._noop
        }        

        #Check for final instruction END
        if op==0: # END
            return False


        if op in operation_dictionary:
            operation_dictionary[op]()

        else:
            raise Exception("Unknown Op", op, self.parent.position)
        return True


    
    #operations
    def _set(self): #1
        reg,val = self.parent.getNext('RV')
        self.parent.set(reg,val)
    

    def _push(self): #2
        a = self.parent.getNext('V')
        self.parent.push(a)


    def _pop(self): #3
        a = self.parent.getNext('R')
        self.parent.set(a,self.parent.pop())
        
    def _eq(self): #4
        a,b,c = self.parent.getNext('RVV')
        res = 1 if b==c else 0
        self.parent.set(a,res)

    def _gt(self): #5
        a,b,c = self.parent.getNext('RVV')
        res = 1 if b>c else 0
        self.parent.set(a,res)
        
    def _jmp(self): #6
        target = self.parent.getNext('V')
        self.parent.jmp(target)
        
    def _jnz(self): #7
        test,target = self.parent.getNext('VV')
        if (test != 0):
            self.parent.jmp(target)

    def _jez(self): #8
        test,target = self.parent.getNext('VV')
        if (test == 0):
            self.parent.jmp(target)
            
    def _add(self): #9
        a,b,c = self.parent.getNext('RVV')
        self.parent.set(a,(b+c)%self.__mod)

    def _mult(self): #10
        a,b,c = self.parent.getNext('RVV')
        self.parent.set(a,(b*c)%self.__mod)

    def _mod(self): #11
        a,b,c = self.parent.getNext('RVV')
        self.parent.set(a,b%c)

    def _and(self): #12
        a,b,c = self.parent.getNext('RVV')
        self.parent.set(a,b&c)

    def _or(self): #13
        a,b,c = self.parent.getNext('RVV')
        self.parent.set(a,b|c)

    def _not(self): #14
        a,b = self.parent.getNext('RV')
        self.parent.set(a,~b%self.__mod)

    def _rmem(self): #15
        a,b = self.parent.getNext('RV')
        self.parent.set(a,self.parent.rmem(b))

    def _wmem(self): #16
        a,b = self.parent.getNext('VV')
        self.parent.wmem(a,b)
        
    def _call(self): #17
        target = self.parent.getNext('V')
        self.parent.push(self.parent.Pos())
        self.parent.jmp(target)

    def _ret(self): #18
        target = self.parent.pop()
        self.parent.jmp(target)

    def _out(self): #19
        s = self.parent.getNext('V')
        print(chr(s),end="")
        
    def _in(self): #20
        target = self.parent.getNext('R')
        st = sys.stdin.read(1)
        self.parent.set(target,ord(st))

    def _noop(self): #21
        pass

    
#prog('challenge.bin').run()




    

        


