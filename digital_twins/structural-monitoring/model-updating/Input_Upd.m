%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% INPUT FILE TO CONDUCT MODEL UPDATING BASED ON VIBRATION MEASUREMENTS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% This is the main file for conducting model updating based on vibration meas-
% urements. Input must be provided by the user; including the input ReMo through
% the command window. The output is a file containing updated system matrices
% and ReMo.
%
% Input (manually provided by the user in the section "Input plugin" below).
%
% Output
%   mod     - txt-file with the stiffness, mass, and damping matrices of the up-
%             dated model along with the output DOF (oloc) and modes used in the
%             model updating (ReMo).
%
% Note(s):
%           - The code uses global variables, which is not recommended. Once the
%             final coding language has been decided, adjustments will be made.
%           - For now, the code is set up to update stiffness parameters, but
%             mass parameters can be readily included in the updating.
%           - The "updated" damping matrix is formed using a modal damping model
%             (assuming classical damping) with the estimated damping ratios.
%             For the remaining modes, the damping ratios are set to 0.
%           - The example is based on a simulated 5DOF model with the stiffness
%             perturbations [1.15 0.75 1 0.92 1].
%
% /MDU 06-11-2023
%-------------------------------------------------------------------------------

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Starting commands (no input required)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clear all; close all; clc;
addpath('Functions');

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Input plugin (the user plugs in the required input)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
load('../system-identification/Results/sys.txt'); % load sys file from the ID
imshow('../system-identification/Results/MAC_MCF.png');
ReMo=input('Choose the physical modes to use for updating (ex.: [1,3,4]): ');
sys.oloc=[1,3,5]; % Output DOF (must match some DOF in the model)
m=ones(1,5); % Initial mass of the model
k=ones(1,5)*1000; % Initial stiffness of the model
PaR=[1,2,4,5]; % Updating parameters (the numbers refer to stiffness parameters)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Model updating routine (no input required)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
sys.omegaS=sys.omegaS(ReMo);
sys.zetaS=sys.zetaS(ReMo);
sys.PhiS=sys.PhiS(:,ReMo);
if numel(PaR)>numel(ReMo)
  error('The problem is underdetermined - please fix it.')
end
[MU,CdamU,KU]=Model_Upd(sys,m,k,PaR);
mod.MU=sparse(MU);
mod.CdamU=sparse(CdamU);
mod.KU=sparse(KU);
mod.ReMo=ReMo;
mod.oloc=sys.oloc;
clearvars -except mod
pathname=fileparts('Results/');
OutputFile=fullfile(pathname,'mod.txt');
save(OutputFile);

