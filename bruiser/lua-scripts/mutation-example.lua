setmakepath("../test/bruisertest")
setbinpath("../test/bruisertest")
make("clean")
--extractmutagen("test.cpp")
text = hijackmain()
file = io.open("../test/bruisertest/mutant.cpp", "w")
print("------------------------------------------------------------------")
print(text)
print("------------------------------------------------------------------")
file:write()
file:close()
