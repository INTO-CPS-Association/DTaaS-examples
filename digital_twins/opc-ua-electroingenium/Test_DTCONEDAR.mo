model Test_DTCONEDAR
constant Integer N_RADIAL = 5; // Number of radial cells around lamp
constant Integer N_AXIAL = 10; // Number of stream-wise cells for each module
parameter Integer I      = 3 "[]"; // Number of UV modules
parameter Integer N      = 10 "[]"; // Number of rows of lamps in UV modules
parameter Integer M      = 8 "[]"; // Number of columns of lamps in UV modules

input Real abs_in(start = 30.0) "[1/m]";             // Absorption coefficient at inlet
input Real rho_a1_in(start = 100000.) "[UFC/100ml]";  // Pathogen concentration at inlet
input Real rho_a2_in(start = 10000.)  "[UFC/100ml]";  // Pathogen concentration at inlet
input Real rho_a3_in(start = 1000.)   "[UFC/100ml]";  // Pathogen concentration at inlet
input Real rho_c_in(start = 0.1) "[ml(H2O2)/L]";  // Disinfectant concentration at inlet
input Real vfr(start = 0.20833) "[m3/s]";            // Volumetric flow rate of water
input Real[N,M] vel_prof(start = fill(10.0, N, M));   // Weight matrix to obtain velocity profiles for each lamp
input Real[3] power(start = fill(100., 3)) "[%]"; // Power going to each UV module; for now, 100% power is 150 for each lamp

output Real concOutA1_1;
output Real concOutA1_2;
output Real concOutA1_3;
output Real concOutA1_4;
output Real concOutA1_5;
output Real concOutA1_6;
output Real concOutA1_7;

output Real concOutA2_1;
output Real concOutA2_2;
output Real concOutA2_3;
output Real concOutA2_4;
output Real concOutA2_5;
output Real concOutA2_6;
output Real concOutA2_7;

output Real concOutA3_1;
output Real concOutA3_2;
output Real concOutA3_3;
output Real concOutA3_4;
output Real concOutA3_5;
output Real concOutA3_6;
output Real concOutA3_7;

output Real concOutC_1;
output Real concOutC_2;
output Real concOutC_3;
output Real concOutC_4;
output Real concOutC_5;
output Real concOutC_6;
output Real concOutC_7;

equation
concOutA1_1=time*0.1;
concOutA1_2=time*0.15;
concOutA1_3=time*0.2;
concOutA1_4=time*0.25;
concOutA1_5=time*0.3;
concOutA1_6=time*0.05;
concOutA1_7=time*0.35;

concOutA2_1=time*0.1;
concOutA2_2=time*0.15;
concOutA2_3=time*0.2;
concOutA2_4=time*0.25;
concOutA2_5=time*0.3;
concOutA2_6=time*0.05;
concOutA2_7=time*0.35;

concOutA3_1=time*0.1;
concOutA3_2=time*0.15;
concOutA3_3=time*0.2;
concOutA3_4=time*0.25;
concOutA3_5=time*0.3;
concOutA3_6=time*0.05;
concOutA3_7=time*0.35;

concOutC_1=time*0.01;
concOutC_2=time*0.01;
concOutC_3=time*0.01;
concOutC_4=time*0.01;
concOutC_5=time*0.3;
concOutC_6=time*0.15;
concOutC_7=time*0.25;


end Test_DTCONEDAR;
