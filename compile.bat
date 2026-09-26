rgbasm %1.asm -o %1.o
rgblink %1.o -o %1.gb
rgbfix -v -p 0 %1.gb
