function MoKe2=Mode_Pair(PhiS,omegaS,PhiM,omegaM,r1,MoKe,Rloc)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PAIRING OF EXPERIMENTAL MODES AND MODEL-BASED MODES
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Input:
%   PhiS    - Experimental mode shapes.
%   omegaS  - Experimental eigenfrequencies.
%   PhiM    - Model-based mode shapes.
%   omegaM  - Model-based eigenfrequencies.
%   r1      - Pairing indeces based on eigenfrequencies.
%   MoKe    - Original mode pairing.
%   Rloc    - Indeces with discrepancy between original pairing and current.
%
% Output:
%   MoKe2   - Updated pairing of modes.
%
% /MDU 16-11-2023
%-------------------------------------------------------------------------------

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Mode pairing
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if nargin==5
  CaMo=numel(omegaS);
  MoKe2=r1;
  Rloc=1:CaMo;
elseif nargin==7
  MoKe2=MoKe;
else
  error('Incorrect input configuration for mode pairing - please fix.')
end
for pp=1:numel(Rloc)
  Rpp=Rloc(pp);
  MAC2=abs(PhiS(:,Rpp)'*PhiM).^2./(PhiS(:,Rpp)'*PhiS(:,Rpp)*diag(PhiM'*PhiM)).';
  [~,i1]=max(real(MAC2));
  if i1==r1(Rpp)
    MoKe2(Rpp)=i1;
  elseif i1==MoKe2(Rpp) && abs(i1-r1(Rpp))==1 && MAC2(i1)>0.8 && MAC2(i1)>2*MAC2(r1(Rpp))
    disp('Mismatch in eigenmode pairing - a choice based on MAC is made.')
  else
    error('A manual pairing of eigenmodes is necessary.')
  end
end
