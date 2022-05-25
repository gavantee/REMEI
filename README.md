# REMEI

RISC-V Emulator and Maybe Even IDE

The plan is to have an online RISC-V emulator with following features:
- Programs can be written in C
- Frontend (or at least API) for gdb (breakpoints, next, continue, registers, memory dumping)
- Few precoded examples of how programing errors could be exploited like gets buffer overflow, format strings... (more examples are welcome or I might steal some from OverTheWire)

TODO:
- executing programs in qemu and attaching gdb
- passing commands to gdb and getting responses

Done:
- using gcc for assembly

Required:
- riscv64-elf-gcc
- riscv64-elf-gdb
- qemu-riscv64

Running:
- python backend/server.py
- ./run_example <path_to_c_program>
