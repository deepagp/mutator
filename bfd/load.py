#!/bin/python3
from enum import Enum


class sh_type_e:
    SHT_NULL = 0x0
    SHT_PROGBITS = 0x1
    SHT_SYMTAB = 0x2
    SHT_STRTAB = 0x3
    SHT_RELA = 0x4
    SHT_HASH = 0x5
    SHT_DYNAMIC = 0x6
    SHT_NOTE = 0x7
    SHT_NOBITS = 0x8
    SHT_REL = 0x9
    SHT_SHLIB = 0xa
    SHT_DYNSYM = 0xb
    SHT_INIT_ARRAY = 0xe
    SHT_FINI_ARRAY = 0xf
    SHT_PREINIT = 0x10
    SHT_GROUP = 0x11
    SHT_SYMTAB_SHNDX = 0x12
    SHT_NUM = 0x13
    SHT_LOOS = 0x60000000


class sh_flags_e:
    SHF_WRITE = 0x1
    SHF_ALLOC = 0x2
    SHF_EXECINSTR = 0x4
    SHF_MERGE = 0x10
    SHF_STRINGS = 0x20
    SHF_INFO_LINK = 0x40
    SHF_LINK_ORDER = 0x80
    SHF_OS_NONCONFORMING = 0x100
    SHF_GROUP = 0x200
    SHF_TLS = 0x400
    SHF_MASKOS = 0x0ff00000
    SHF_MASKPROC = 0xf0000000
    SHF_ORDERED = 0x4000000
    SHF_EXCLUDE = 0x8000000


class p_type_e:
    PT_NULL = 0x0
    PT_LOAD = 0x1
    PT_DYNAMIC = 0x2
    PT_INTERP = 0x3
    PT_NOTE = 0x4
    PT_SHLIB = 0x5
    PT_PHDR = 0x6
    PT_LOOS = 0x60000000
    PT_HIOS = 0x6FFFFFFF
    PT_LOPROC = 0x70000000
    PT_HIPROC = 0x7FFFFFFF


class Colors:
    purple = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    grey = '\033[1;37m'
    darkgrey = '\033[1;30m'
    cyan = '\033[1;36m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def openSO_r(path):
    so = open(path, "rb")
    return so


def openSO_w(path):
    so = open(path, "wb")
    return so


class ELFHDR():
    def __init__(self, ei_mag, ei_class, ei_data, ei_version, ei_osabi, ei_abiversion,
                 ei_pad, e_type, e_machine, e_version, e_entry, e_phoff,
                 e_shoff, e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize,
                 e_shnum, e_shstrndx):
        self.ei_mag = ei_mag
        self.ei_class = ei_class
        self.ei_data = ei_data
        self.ei_version = ei_version
        self.ei_osabi = ei_osabi
        self.ei_abiversion = ei_abiversion
        self.ei_pad = ei_pad
        self.e_type = e_type
        self.e_machine = e_machine
        self.e_version = e_version
        self.e_entry = e_entry
        self.e_phoff = e_phoff
        self.e_shoff = e_shoff
        self.e_flags = e_flags
        self.e_ehsize = e_ehsize
        self.e_phentsize = e_phentsize
        self.e_phnum = e_phnum
        self.e_shentsize = e_shentsize
        self.e_shnum = e_shnum
        self.e_shstrndx = e_shstrndx


class PHDR():
    def __init__(self, p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz,
                 p_memsz, p_flags2, p_align):
        self.p_type = p_type
        self.p_flags = p_flags
        self.p_offset = p_offset
        self.p_vaddr = p_vaddr
        self.p_paddr = p_paddr
        self.p_filesz = p_filesz
        self.p_memsz = p_memsz
        self.p_flags2 = p_flags2
        self.p_align = p_align


class SHDR():
    def __init__(self, sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size,
                 sh_link, sh_info, sh_addralign, sh_entsize):
        self.sh_name = sh_name
        self.sh_type = sh_type
        self.sh_flags = sh_flags
        self.sh_addr = sh_addr
        self.sh_offset = sh_offset
        self.sh_size = sh_size
        self.sh_link = sh_link
        self.sh_info = sh_info
        self.sh_addralign = sh_addralign
        self.sh_entsize = sh_entsize


class Symbol_Table_Entry64():
    def __init__(self, st_name, st_info, st_other, st_shndx, st_value, st_size):
        self.st_name = st_name
        self.st_info = st_info
        self.st_other = st_other
        self.st_shndx = st_shndx
        self.st_value = st_value
        self.st_size = st_size


class ELF(object):
    def __init__(self, so):
        self.so = so
        self.so.seek(0, 0)
        self.elfhdr = ELFHDR(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
        self.phdr = []
        self.shhdr = []
        self.size = int()
        self.ste = []

    def init(self, size):
        self.size = size
        self.read_ELF_H(size)
        self.so.seek(int.from_bytes(self.elfhdr.e_phoff, byteorder="little", signed=False))
        phnum = int.from_bytes(self.elfhdr.e_phnum, byteorder="little", signed=False)
        for i in range(0, phnum):
            self.read_PHDR(size)
        self.so.seek(int.from_bytes(self.elfhdr.e_shoff, byteorder="little", signed=False))
        shnum = int.from_bytes(self.elfhdr.e_shnum, byteorder="little", signed=False)
        for i in range(0, shnum):
            self.read_SHDR(size)
        self.read_SHDR(size)

    # 32 or 64
    def read_ELF_H(self, size):
        self.elfhdr.ei_mag = self.so.read(4)
        self.elfhdr.ei_class = self.so.read(1)
        self.elfhdr.ei_data = self.so.read(1)
        self.elfhdr.ei_version = self.so.read(1)
        self.elfhdr.ei_osabi = self.so.read(1)
        self.elfhdr.ei_abiversion = self.so.read(1)
        self.elfhdr.ei_pad = self.so.read(7)
        self.elfhdr.e_type = self.so.read(2)
        self.elfhdr.e_machine = self.so.read(2)
        self.elfhdr.e_version = self.so.read(4)
        if size == 32: self.elfhdr.e_entry = self.so.read(4)
        elif size == 64: self.elfhdr.e_entry = self.so.read(8)
        if size == 32: self.elfhdr.e_phoff = self.so.read(4)
        elif size == 64: self.elfhdr.e_phoff = self.so.read(8)
        if size == 32: self.elfhdr.e_shoff = self.so.read(4)
        elif size == 64: self.elfhdr.e_shoff = self.so.read(8)
        self.elfhdr.e_flags = self.so.read(4)
        self.elfhdr.e_ehsize = self.so.read(2)
        self.elfhdr.e_phentsize = self.so.read(2)
        self.elfhdr.e_phnum = self.so.read(2)
        self.elfhdr.e_shentsize = self.so.read(2)
        self.elfhdr.e_shnum = self.so.read(2)
        self.elfhdr.e_shstrndx = self.so.read(2)

    def read_PHDR(self, size):
        dummy = PHDR(0,0,0,0,0,0,0,0,0)
        dummy.p_type = self.so.read(4)
        if size == 64: dummy.p_flags = self.so.read(4)
        if size == 32: dummy.p_offset = self.so.read(4)
        elif size == 64: dummy.p_offset = self.so.read(8)
        if size == 32: dummy.p_vaddr = self.so.read(4)
        elif size == 64: dummy.p_vaddr = self.so.read(8)
        if size == 32: dummy.p_paddr = self.so.read(4)
        elif size == 64: dummy.p_paddr = self.so.read(8)
        if size == 32: dummy.p_filesz = self.so.read(4)
        elif size == 64: dummy.p_filesz = self.so.read(8)
        if size == 32: dummy.p_memsz = self.so.read(4)
        elif size == 64: dummy.p_memsz = self.so.read(8)
        if size == 32: dummy.p_flags2 = self.so.read(4)
        elif size == 64: pass
        if size == 32: dummy.p_align = self.so.read(4)
        elif size == 64: dummy.p_align = self.so.read(8)
        self.phdr.append(dummy)

    def read_SHDR(self, size):
        dummy = SHDR(0,0,0,0,0,0,0,0,0,0)
        dummy.sh_name = self.so.read(4)
        dummy.sh_type = self.so.read(4)
        if size == 32: dummy.sh_flags = self.so.read(4)
        elif size == 64: dummy.sh_flags = self.so.read(8)
        if size == 32: dummy.sh_addr = self.so.read(4)
        elif size == 64: dummy.sh_addr = self.so.read(8)
        if size == 32: dummy.sh_offset = self.so.read(4)
        elif size == 64: dummy.sh_offset = self.so.read(8)
        if size == 32: dummy.sh_size = self.so.read(4)
        elif size == 64: dummy.sh_size = self.so.read(8)
        dummy.sh_link = self.so.read(4)
        dummy.sh_info = self.so.read(4)
        if size == 32: dummy.sh_addralign = self.so.read(4)
        elif size == 64: dummy.sh_addralign = self.so.read(8)
        if size == 32: dummy.sh_entsize = self.so.read(4)
        elif size == 64: dummy.sh_entsize = self.so.read(8)
        self.shhdr.append(dummy)

    def read_st_entry(self, st):
        dummy = Symbol_Table_Entry()
        dummy.st_name = st[0:4]
        dummy.st_info = st[4:5]
        dummy.st_other = st[5:6]
        dummy.st_shndx = st[6:8]
        dummy.st_value = st[8:16]
        dummy.st_size = st[16:24]

    def dump_header(self):
        print("------------------------------------------------------------------------------")
        print(Colors.green + "elf header:" + Colors.ENDC)
        print(Colors.blue + "ei_mag: " + Colors.cyan + repr(self.elfhdr.ei_mag) + Colors.ENDC)
        print(Colors.blue + "ei_class: " + Colors.cyan + repr(self.elfhdr.ei_class) + Colors.ENDC)
        print(Colors.blue + "ei_data: " + Colors.cyan + repr(self.elfhdr.ei_data) + Colors.ENDC)
        print(Colors.blue + "ei_version: " + Colors.cyan + repr(self.elfhdr.ei_version) + Colors.ENDC)
        print(Colors.blue + "ei_osabi: " + Colors.cyan + repr(self.elfhdr.ei_osabi) + Colors.ENDC)
        print(Colors.blue + "ei_abiversion: " + Colors.cyan + repr(self.elfhdr.ei_abiversion) + Colors.ENDC)
        print(Colors.blue + "ei_pad: " + Colors.cyan + repr(self.elfhdr.ei_pad) + Colors.ENDC)
        print(Colors.blue + "e_type: " + Colors.cyan + repr(self.elfhdr.e_type) + Colors.ENDC)
        print(Colors.blue + "e_machine: " + Colors.cyan + repr(self.elfhdr.e_machine) + Colors.ENDC)
        print(Colors.blue + "e_version: " + Colors.cyan + repr(self.elfhdr.e_version) + Colors.ENDC)
        print(Colors.blue + "e_entry: " + Colors.cyan + repr(self.elfhdr.e_entry) + Colors.ENDC)
        print(Colors.blue + "e_phoff: " + Colors.cyan + repr(self.elfhdr.e_phoff) + Colors.ENDC)
        print(Colors.blue + "e_shoff: " + Colors.cyan + repr(self.elfhdr.e_shoff) + Colors.ENDC)
        print(Colors.blue + "e_flags: " + Colors.cyan + repr(self.elfhdr.e_flags) + Colors.ENDC)
        print(Colors.blue + "e_ehsize: " + Colors.cyan + repr(self.elfhdr.e_ehsize) + Colors.ENDC)
        print(Colors.blue + "e_phentsize: " + Colors.cyan + repr(self.elfhdr.e_phentsize) + Colors.ENDC)
        print(Colors.blue + "e_phnum: " + Colors.cyan + repr(self.elfhdr.e_phnum) + Colors.ENDC)
        print(Colors.blue + "e_shentsize: " + Colors.cyan + repr(self.elfhdr.e_shentsize) + Colors.ENDC)
        print(Colors.blue + "e_shnum: " + Colors.cyan + repr(self.elfhdr.e_shnum) + Colors.ENDC)
        print(Colors.blue + "e_shstrndx: " + Colors.cyan + repr(self.elfhdr.e_shstrndx) + Colors.ENDC)
        print("------------------------------------------------------------------------------")

    def dump_phdrs(self):
        print(Colors.green + "pheaders:" + Colors.ENDC)
        for i in range(0, int.from_bytes(self.elfhdr.e_phnum, byteorder="little", signed=False)):
            print("------------------------------------------------------------------------------")
            print(Colors.blue + "p_type: " + Colors.cyan + repr(self.phdr[i].p_type) + Colors.ENDC)
            print(Colors.blue + "p_flags: " + Colors.cyan + repr(self.phdr[i].p_flags) + Colors.ENDC)
            print(Colors.blue + "p_offset: " + Colors.cyan + repr(self.phdr[i].p_offset) + Colors.ENDC)
            print(Colors.blue + "p_vaddr: " + Colors.cyan + repr(self.phdr[i].p_vaddr) + Colors.ENDC)
            print(Colors.blue + "p_paddr: " + Colors.cyan + repr(self.phdr[i].p_paddr) + Colors.ENDC)
            print(Colors.blue + "p_filesz: " + Colors.cyan + repr(self.phdr[i].p_filesz) + Colors.ENDC)
            print(Colors.blue + "p_memsz: " + Colors.cyan + repr(self.phdr[i].p_memsz) + Colors.ENDC)
            print(Colors.blue + "p_flags2: " + Colors.cyan + repr(self.phdr[i].p_flags2) + Colors.ENDC)
            print(Colors.blue + "p_align: " + Colors.cyan + repr(self.phdr[i].p_align) + Colors.ENDC)
            print("------------------------------------------------------------------------------")

    def dump_shdrs(self):
        print(Colors.green + "sheaders:" + Colors.ENDC)
        for i in range(0, int.from_bytes(self.elfhdr.e_shnum, byteorder="little", signed=False)):
            print("------------------------------------------------------------------------------")
            print(Colors.blue + "sh_name: " + Colors.cyan + repr(self.shhdr[i].sh_name) + Colors.ENDC)
            print(Colors.blue + "sh_type: " + Colors.cyan + repr(self.shhdr[i].sh_type) + Colors.ENDC)
            print(Colors.blue + "sh_flags: " + Colors.cyan + repr(self.shhdr[i].sh_flags) + Colors.ENDC)
            print(Colors.blue + "sh_addr: " + Colors.cyan + repr(self.shhdr[i].sh_addr) + Colors.ENDC)
            print(Colors.blue + "sh_offset: " + Colors.cyan + repr(self.shhdr[i].sh_offset) + Colors.ENDC)
            print(Colors.blue + "sh_size: " + Colors.cyan + repr(self.shhdr[i].sh_size) + Colors.ENDC)
            print(Colors.blue + "sh_link: " + Colors.cyan + repr(self.shhdr[i].sh_link) + Colors.ENDC)
            print(Colors.blue + "sh_info: " + Colors.cyan + repr(self.shhdr[i].sh_info) + Colors.ENDC)
            print(Colors.blue + "sh_addralign: " + Colors.cyan + repr(self.shhdr[i].sh_addralign) + Colors.ENDC)
            print(Colors.blue + "sh_entsize: " + Colors.cyan + repr(self.shhdr[i].sh_entsize) + Colors.ENDC)
            print("------------------------------------------------------------------------------")

    def dump_symbol_tb(self):
        for i in range(0, int.from_bytes(self.elfhdr.e_shnum, byteorder="little", signed=False)):
            #print(repr(int.from_bytes(self.shhdr[i].sh_type, byteorder="little", signed=False)) + " : ", end='')
            #print(int.from_bytes(self.shhdr[i].sh_size, byteorder="little", signed=False))
            if int.from_bytes(self.shhdr[i].sh_type, byteorder="little", signed=False) == sh_type_e.SHT_SYMTAB:
                self.so.seek(int.from_bytes(self.shhdr[i].sh_offset, byteorder="little", signed=False), 0)
                #print(self.so.read(int.from_bytes(self.shhdr[i].sh_size, byteorder="little", signed=False)))
                symbol_tb = self.so.read(int.from_bytes(self.shhdr[i].sh_size, byteorder="little", signed=False))
            if int.from_bytes(self.shhdr[i].sh_type, byteorder="little", signed=False) == sh_type_e.SHT_DYNSYM:
                self.so.seek(int.from_bytes(self.shhdr[i].sh_offset, byteorder="little", signed=False), 0)
                #print(self.so.read(int.from_bytes(self.shhdr[i].sh_size, byteorder="little", signed=False)))
                symbol_tb = self.so.read(int.from_bytes(self.shhdr[i].sh_size, byteorder="little", signed=False))
            if int.from_bytes(self.shhdr[i].sh_type, byteorder="little", signed=False) == sh_type_e.SHT_STRTAB:
                self.so.seek(int.from_bytes(self.shhdr[i].sh_offset, byteorder="little", signed=False), 0)
                #print(self.so.read(int.from_bytes(self.shhdr[i].sh_size, byteorder="little", signed=False)))
                symbol_tb = self.so.read(int.from_bytes(self.shhdr[i].sh_size, byteorder="little", signed=False))
                #print(symbol_tb.decode("utf-8"))
                for byte in symbol_tb:
                    print(chr(byte), end='')
                    if chr(byte) == '\0': print()


def ch_so_to_exe(path):
    so = open(path, "r+b")
    so.seek(16)
    so.write(bytes([2]))
    print(Colors.purple + "changed so to exe" + Colors.ENDC)
    so.close


def ch_exe_to_so(path):
    so = open(path, "r+b")
    so.seek(16)
    so.write(bytes([3]))
    print(Colors.purple + "changed exe to so" + Colors.ENDC)


def main():
    so = openSO_r("./test/test.so")
    elf = ELF(so)
    elf.init(64)
    #elf.dump_header()
    elf.dump_symbol_tb()
    #elf.dump_phdrs()
    #elf.dump_shdrs()
    '''
    so.close()
    ch_so_to_exe("./test/test.so")
    so = openSO_r("./test/test.so")
    elf2 = ELF(so)
    elf2.init(64)
    elf.dump_header()
    '''

if __name__ == "__main__":
    main()
