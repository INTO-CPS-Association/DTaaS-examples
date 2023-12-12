%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% INPUT FILE TO CONDUCT MODAL EXPANSION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% This is the main file for conducting modal expansion based on vibration meas-
% urements and a physics-based model. The input includes the vibration measure-
% ments, sys.txt and mod.txt (which are loaded automatically), and MoRe, which
% contains the modes to be used for modal expansion and must be typed in the
% command window during the code run. The output file contains the displacements
% in all DOF.
%
% Input (manually provided by the user in the section "Input plugin" below).
%
% Output
%   Disp    - txt-file with estimates of the displacements in all the DOF in the
%             physics-based model.
%
% Note(s):
%           - The modal expansion is conducted assuming classical damping.
%           - Currently, the expansion basis is solely model-based. This can,
%             however, be readily changed.
%           - For now, only zero- to second-order detrending is employed. Addi-
%             tional filtering should probably be implemented at some point.
%           - The example is based on a simulated 5DOF model with output sensors
%             at DOF 1, 3, and 5.
%
% /MDU 06-11-2023
%-------------------------------------------------------------------------------

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Starting commands (no input required)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clear all; close all; clc;
addpath('Functions','..\Data');

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Input plugin (the user plugs in the required input)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
FileName='Acc_5DOF.txt'; % provide the name of the output measurement data file
load('..\System identification\Results\sys.txt'); % file from the sys. ID block
load('..\Model updating\Results\mod.txt'); % file from the model updating block
MoRe=input('Choose (experimental) modes to use for expansion (ex.: [1,3,4]): ');
if  any(~ismember(MoRe,mod.ReMo))
  disp('Warning: modes have been selected that are not updated in the model.')
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Modal expansion routine (no input required)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if numel(MoRe)>numel(mod.oloc)
  error('The problem is underdetermined - please fix it.')
end
Disp=Modal_Exp(FileName,sys,mod,MoRe);
clearvars -except Disp
pathname=fileparts('Results/');
OutputFile=fullfile(pathname,'Disp.txt');
save(OutputFile);
