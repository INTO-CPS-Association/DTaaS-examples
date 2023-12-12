function [M,C,K]=Chain(m,zeta,k)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% COMPUTATION OF MASS, DAMPING, AND STIFFNESS MATRICES FOR CHAIN SYSTEMS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Input:
%   m       - Point masses.
%   m       - Damping ratios (assum. classical damping).
%   k       - Spring stiffnesses.
%
% Output:
%   M       - Mass matrix.
%   C       - Damping matrix (assum. classical damping).
%   K       - Stiffness matrix.
%
% /MDU 06-11-2023
%-------------------------------------------------------------------------------

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% M, C, and K
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
dof=numel(m);
if dof~=1
  for j=1:dof-1
    kd(j)=k(j)+k(j+1);
    kf(j)=-k(j+1);
  end
  kd(dof)=k(dof);
  K=diag(kf,1)+diag(kf,-1)+diag(kd);
  M=diag(m);
  if max(zeta)==0
    C=M*0;
  else
    [aa11,bb]=eig(K,M);
    omegaN=sqrt(diag(bb));
    omegaN=omegaN';
    dd=sqrt(diag(aa11'*M*aa11));
    aa=aa11*diag(1./dd);
    Cmodal=diag(2*zeta.*omegaN);
    C=inv(aa)'*Cmodal*inv(aa);
  end
else
  K=k;
  M=m;
  C=2*zeta*sqrt(k*m);
end
