
xobj = require("xobj")
asmrw = require("asmrw")

function test()
  local elf_exe = "../bfd/test/test"
  local text_section = xobj.getTextSection(elf_exe)
  -- local head = jmp_s_t()
  -- messes up the stack. I could fix it but not sure why i would want to keep this in
  --local head2 = jmp_s_t:new()
  local head = getjmptable(#text_section, text_section)
  print(type(head))

  while head:inext() ~= nil do
    --head:dump("entry")
    io.write("type:", head:type(), "\tlocation:", "0x"..string.format("%x", head:location()))
    print()
    head = head:inext()
  end

  local dummy = jmp_s_t
  print(type(dummy))
  for k,v in pairs(dummy) do
    if type(v) == "function" then
      print(k,v )
    end
  end
  --print(dummy:location())
end

test()
