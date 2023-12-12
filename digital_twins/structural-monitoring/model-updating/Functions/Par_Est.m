function [X,Ob]=Par_Est(x)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% OPTIMIZATION FOR PARAMETER ESTIMATION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Input:
%   x       - Initial values for the parameters to be estimated.
%
% Output:
%   X       - Model parameters at the converged configuration.
%   Ob      - Objective function value at the converged configuration.
%
% Note(s)
%           - A global data structure (comb) is loaded from the main file.
%
% /MDU 06-11-2023
%-------------------------------------------------------------------------------

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Problem setup
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
global comb;
k=comb.k;
k(comb.PaR)=k(comb.PaR).*x;
m=comb.m;
dof=numel(m);
[M,Cdam,K]=Chain(m,m*0,k);
[PhiM,omegaM]=Model_Eig(M,Cdam,K,comb.sys);
Odis=abs(omegaM-comb.sys.omegaS);
[~,r1]=min(Odis);
Rdis=r1-comb.MoKe;
if max(abs(Rdis))>0
  Rloc=find(Rdis~=0);
  MoKe2=Mode_Pair(comb.sys.PhiS,comb.sys.omegaS,PhiM,omegaM,r1,comb.MoKe,Rloc);
else
  MoKe2=comb.MoKe;
end
omegaMP=omegaM(MoKe2);
PhiMP=PhiM(:,MoKe2);
MACn=abs(diag(comb.sys.PhiS'*PhiMP)).^2;
MACd=diag(comb.sys.PhiS'*comb.sys.PhiS).*diag(PhiMP'*PhiMP);
MAC=MACn./MACd;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Objective function
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
resOM=omegaMP-comb.sys.omegaS.';
resPhi=MAC;
X=resOM'*resOM+1/(resPhi'*resPhi);
