This codes conducts stochastic (i.e., output-only) subspace identification based on vibration 
measurements. In the main file, "Input_SysID", the user must provide input and execute the code. 
The output of the code is a file (saved in the folder "Results") containing the estimated eigen-
characteristics and the parameter "otype", which designates whether the measurements are displace-
ments (otype=0), velocitites (otype=1), or accelerations (otype=2).

The user must specify the model order in the command window during the run of the code. This can be
based on a stabilization diagram that will appear concurrently. A figure showing the modal assurance 
criterion (MAC) values and the modal complexity factors (MCFs) will appear. This can be used to assess 
the quality of the identification.

/MDU 13-11-2023