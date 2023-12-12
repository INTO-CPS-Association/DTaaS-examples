function Disp=Modal_Exp(FileName,sys,mod,MoRe)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MODAL EXPANSION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Input:
%   sys      - Data structure with experimental features.
%   mod      - Data structure containing the model.
%   MoRe     - Modes to be used in the modal expansion.
%
% Output:
%   Disp    - Displacements in all DOF.
%
% /MDU 06-11-2023
%-------------------------------------------------------------------------------

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Starting command (for potential filtering in Octave)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
pkg load signal

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Experimental data
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
yM=load(FileName);
[ms,N]=size(yM);
if ms~=mod.oloc
  error('Inconsistency between oloc and ms - please fix.')
end
if N<ms
  yM=yM';
  [ms,N]=size(yM);
end
if rem(N,2)==0
    N=N-1;
    yM=yM(:,1:N);
end
omegaSP=sys.omegaS(MoRe);
PhiSP=sys.PhiS(:,MoRe);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Model-based modes
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
K=full(mod.KU);
M=full(mod.MU);
olocFull=1:size(K,1);
[PhiM,omegaM]=Model_Eig(M,0*M,K,sys.otype,olocFull); % We assume classical damp.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Extraction of the correct model-based eigenmodes
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Odis=abs(omegaM-omegaSP);
[~,r1]=min(Odis);
MoKe=Mode_Pair(PhiSP,omegaSP,PhiM(mod.oloc,:),omegaM,r1);
omegaMP=omegaM(MoKe);
PhiMP=PhiM(:,MoKe);
for jj=1:numel(MoKe)
  cS=1;
  dS=-imag(PhiMP(1,jj))/real(PhiMP(1,jj));
  pS=PhiMP(:,jj)*(cS+dS*1i);
  spS=pS/norm(real(pS));
  if norm(imag(spS))<1e-12
    PhiMP(:,jj)=real(spS);
  else
    error('The model-based modes are not classically damped - please fix.')
  end
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Estimation of the measured output type in all DOF
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
nooloc=olocFull;
nooloc(mod.oloc)=[];
PhiMPm=PhiMP(mod.oloc,:);
PhiMPu=PhiMP(nooloc,:);
qmod=PhiMPm\yM;
yFull2=zeros(numel(olocFull),N);
yFull2(mod.oloc,:)=yM;
yFull2(nooloc,:)=PhiMPu*qmod;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Displacement estimation
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if sys.otype==0
  Disp=yFull2;
else
  yFull1=yFull2-mean(yFull2,2);
  YY=fft(yFull1.');
  Y=YY.';
  Nh=ceil((N+1)/2);
  cK=1:Nh-1;
  D=zeros(size(Y));
  omj=1i*2*pi*cK*sys.Fs/N;
  if sys.otype==1
    D(:,2:Nh)=Y(:,2:Nh)./omj;
    D(:,Nh+1:N)=conj(flip(D(:,2:Nh),2));
  elseif sys.otype==2
    D(:,2:Nh)=Y(:,2:Nh)./omj.^2;
    D(:,Nh+1:N)=conj(flip(D(:,2:Nh),2));
  else
    error('Unknown measurement type - please fix it.')
  end
  Disp2=ifft(D.');
  Disp1=detrend(Disp2,sys.otype);
  Disp=Disp1.';
end
if norm(imag(Disp))>norm(real(Disp))*1e-8
  error('The displacements are complex-valued - please fix it.')
else
  Disp=real(Disp);
end
