function [omegaS,zetaS,PhiS]=SSI_Data(FileName,Fs,nmax,nblock)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% STOCHASTIC SUBSPACE IDENTIFICATION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Input:
%   FileName - Name of the file containing the measured output response(s).
%   Fs       - Sampling frequency.
%   nmax     - Maximum state-space model order.
%   nblock   - Number of block columns in Hankel matrix.
%
% Output:
%   omegaS   - Eigenfrequencies with model order n.
%   zetaS    - Damping ratios (assum. classical damping) with model order n.
%   PhiS     - Mode shapes with model order n.
%
% Note(s):
%            - A figure is saved with the modal assurance criterion values and
%              model complexity factors. This figure is used in the model upda-
%              ting code.
%
% /MDU 06-11-2023
%-------------------------------------------------------------------------------

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Data definitions and arrangement
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
dt=1/Fs;
y=load(FileName);
[ms,Ns]=size(y);
if Ns<ms
  y=y';
  [ms,Ns]=size(y);
end
i=nblock;
j=Ns-2*i+1; % Number of columns in block Hankel matrix
if i<=0 || j<0
  error('Both i and j must be positive - please fix');
end
if j>Ns-i+1
  error('j is too big - please fix');
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Block Hankel data matrix
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
y1=y(:,i+1:Ns)/sqrt(j);
y=y/sqrt(j);
Yp=zeros(ms,j);
Yf=zeros(ms,j);
for k=1:i
  Yp((k-1)*ms+1:k*ms,:)=y(:,k:k+j-1);
  Yf((k-1)*ms+1:k*ms,:)=y1(:,k:k+j-1);
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Decompositions and projections
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Y=[Yp;Yf];
R=triu(qr(Y'))';
R=R(1:2*i*ms,1:2*i*ms);
Ob=R(ms*i+1:2*ms*i,1:ms*i);
[U1,S,~]=svd(Ob);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Computation of eigencharacteristics for different model orders
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
omega=zeros(nmax);
zeta=zeros(nmax);
phi=zeros(ms,nmax,nmax);
LeL=zeros(nmax,1);
for ii=1:nmax
  U2=U1(:,1:ii);
  S1=S(1:ii,1:ii);
  gammai=U2*sqrt(S1);
  gammaip1=gammai(1:ms*(i-1),:);
  Xi=gammai\Ob;
  Xip=gammaip1\R(ms*(i+1)+1:2*ms*i,1:ms*(i+1));
  Rhs=[Xi zeros(ii,ms)];
  Lhs=[Xip ; R(ms*i+1:ms*(i+1),1:ms*(i+1))];
  sol=Lhs/Rhs;
  A=sol(1:ii,1:ii);
  C=sol(ii+1:ii+ms,1:ii);
  [V,Lambda]=eig(A);
  lamC=log(diag(Lambda))/dt;
  Omega=abs(imag(lamC));
  Zeta=-real(lamC)./abs(lamC);
  [Omega,e1]=sort(Omega);
  Zeta=Zeta(e1);
  Phi=C*V;
  Phi=Phi(:,e1);
  [Omega,e2]=uniquetol(Omega,0.001);
  Zeta=Zeta(e2);
  Phi=Phi(:,e2);
  LeL(ii)=length(Omega);
  omega(1:length(Omega),ii)=Omega;
  zeta(1:length(Zeta),ii)=Zeta;
  phi(:,1:size(Phi,2),ii)=Phi;
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Model-order selection using a stabilization diagram
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
n=Stab_Diag(nmax,LeL,omega,zeta,phi);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% The eigencharacteristics with model order n
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
omegaS=omega(1:LeL(n),n).';
zetaS=zeta(1:LeL(n),n).';
PhiS=phi(:,1:LeL(n),n);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Modal assurance criterion (MAC) values and modal complexity factors (MCFs)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
MAC=zeros(LeL(n));
MCF=zeros(1,LeL(n));
for jj=1:LeL(n)
  phiSjj=PhiS(:,jj);
  for ii=1:LeL(n)
    phiSii=PhiS(:,ii);
    MAC(jj,ii)=real(abs(phiSjj'*phiSii)^2/(phiSjj'*phiSjj*phiSii'*phiSii));
  end
  WRR=real(phiSjj)'*real(phiSjj);
  WII=imag(phiSjj)'*imag(phiSjj);
  WRI=real(phiSjj)'*imag(phiSjj);
  MCF(jj)=1-((WRR-WII)^2+4*WRI^2)/(WRR+WII)^2;
end
figure;
subplot(1,2,1); imagesc(1:LeL(n),1:LeL(n),MAC); colormap(summer); colorbar;
set(gca,'YDir','normal');
xlabel('Mode'); ylabel('Mode'); cb=colorbar(); ylabel(cb,'MAC','Rotation',270);
title('MAC');
subplot(1,2,2); bar(1:LeL(n),MCF);
ylim([0 1]); xlabel('Mode'); ylabel('MCF'); title('MCF');
saveas(gcf,'Results/MAC_MCF.png')
end
