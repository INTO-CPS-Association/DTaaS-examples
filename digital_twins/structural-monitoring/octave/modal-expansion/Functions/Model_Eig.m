function [PhiM,omegaM]=Model_Eig(M,Cdam,K,otype,oloc)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EIGENCHARACTERISTICS USING A STATE-SPACE FORMULATION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Input:
%   M        - Mass matrix.
%   Cdam     - Damping matrix.
%   K        - Stiffness matrix.
%   otype    - Output type.
%   oloc     - Output DOF.
%
% Output:
%   PhiM     - Mode shapes of the model.
%   omegaM   - Eigenfrequencies of the model.
%
% /MDU 06-11-2023

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% State-space formulation
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
dof=size(M,1);
AM=[zeros(dof) eye(dof) ; -M\K -M\Cdam];
if otype==0
  CMM=[eye(dof) zeros(dof)];
elseif otype==1
  CMM=[zeros(dof) eye(dof)];
elseif otype==2
  CMM=AM(dof+1:end,:);
else
  error('A wrong output type has been chosen - please fix')
end
CM=CMM(oloc,:);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Eigenproblem
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
[PhiM3,LambdaM]=eig(AM);
[OmegaM,t2]=sort(abs(diag(LambdaM)));
omegaM=OmegaM(1:2:end); % Every second since we disregard damping
PhiM3=PhiM3(:,t2);
PhiM2=PhiM3(:,1:2:end);
PhiM=CM*PhiM2;
