function n=Stab_Diag(nmax,LeL,omega,zeta,phi)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MODEL-ORDER SELECTION USING A STABILIZATION DIAGRAM
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Input:
%   nmax     - Maximum model order
%   LeL      - Number of unique eigenfrequencies for model orders 1 to nmax.
%   omega    - The unique eigenfrequencies for each model order.
%   zeta     - The associated damping ratios.
%   phi      - The associated mode shapes.
%
% Output:
%   n        - Selected model order.
%
% /MDU 06-11-2023
%-------------------------------------------------------------------------------

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Stabilization diagram
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
omega=omega/(2*pi); % Frequencies in Hz instead of rad/s
figure; hold on; clf;
for ii=1:nmax-1
  Omega1=omega(1:LeL(ii),ii);
  Omega2=omega(1:LeL(ii+1),ii+1);
  Zeta1=zeta(1:LeL(ii),ii);
  Zeta2=zeta(1:LeL(ii+1),ii+1);
  Phi1=phi(:,1:LeL(ii),ii);
  Phi2=phi(:,1:LeL(ii+1),ii+1);
  Logic_Omega=logical(sum(abs((Omega1-Omega2')./Omega1)<=0.03,2));
  Logic_Zeta=logical(sum(abs((Zeta1-Zeta2')./Zeta1)<=0.05,2));
  MAC_vals=zeros(1,length(Omega2));
  Logic_Phi=zeros(length(Omega1),1);
  for j=1:length(Omega1)
    for k=1:length(Omega2)
      MAC_vals(k)=(abs(Phi1(:,j)'*Phi2(:,k)))^2/...
                  (Phi1(:,j)'*Phi1(:,j)*Phi2(:,k)'*Phi2(:,k));
    end
    Logic_Phi(j)=logical(sum(MAC_vals>=0.98));
  end
  Logic_Phi=logical(Logic_Phi);
  Stable_Pole=Omega1(Logic_Omega&Logic_Zeta&Logic_Phi);
  StaOrder=ii*ones(numel(Stable_Pole),1);
  Unstable_Pole=Omega1; Unstable_Pole(Logic_Omega&Logic_Zeta&Logic_Phi)=[];
  UnStaOrder=ii*ones(numel(Unstable_Pole),1);
  plot(Stable_Pole,StaOrder,'ko',Unstable_Pole,UnStaOrder,'k*'); hold on
end
title('Stabilization diagram')
ylabel('Model order')
xlabel('Frequency [Hz]')
h=zeros(2,1);
h(1)=plot(NaN,NaN,'ko');
h(2)=plot(NaN,NaN,'k*');
legend(h,{'Strictly stable eigenmode','Partially stable or unstable eigenmode'},...
       'Location','southeast')
clc
saveas(gcf,'Results/Stab_diagram.png')

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Model-order selection
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
n=input('Choose moddel order from the diagram by typing the number and pressing enter: ');


