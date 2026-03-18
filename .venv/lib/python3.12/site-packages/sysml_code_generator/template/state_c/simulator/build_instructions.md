# Build Instructions for generated C state machine with TK Simulator GUI        

# Preconditions:
- Windows
- gcc
- generated state machine and simulator code
- pyinstaller (optional)

## Compile a DLL from the state machine and its integration
```
gcc -shared -fPIC simulator.c stm.c -o integration.dll 
```

## Run the python GUI directly
The generated simulator.py expects the compiled integration.dll in the current working directory.

```
python simulator.py 
```

## Bundle simulator as standalone executable (optional)
```
pyinstaller -F --add-binary integration.dll;. --log-level WARN --distpath=. simulator.py 
```

