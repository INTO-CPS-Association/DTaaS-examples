function [MU,CdamU,KU]=Model_Upd(sys,m,k,PaR)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MODEL UPDATING BASED ON VIBRATION MEASUREMENTS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Input:
%   sys      - Data structure with experimental data
%   m        - Mass for each component/element in the model.
%   k        - Stiffness for each component/element in the model.
%   PaR      - Parameters to be updated (for now, confined to stiffness).
%
% Output:
%   MU       - Updated mass matrix.
%   CdamU    - Updated damping matrix.
%   KU       - Updated stiffness matrix.
%
% /MDU 06-11-2023
%-------------------------------------------------------------------------------

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Starting command (for optimization in Octave)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
pkg load optim

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Nominal model
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
[M,Cdam,K]=Chain(m,0*m,k); % We omit damping for now - is employed later
dof=size(M,1);
[PhiM,omegaM]=Model_Eig(M,Cdam,K,sys);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Initial pairing of experimental modes and model-based modes
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Odis=abs(omegaM-sys.omegaS);
[~,r1]=min(Odis);
MoKe=Mode_Pair(sys.PhiS,sys.omegaS,PhiM,omegaM,r1);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Parameter estimation through constrained minimization
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
np=numel(PaR);
lb=0.6*ones(1,np); % lower bound(s)
ub=1.4*ones(1,np); % upper bound(s)
H=[]; b=[]; Heq=[]; beq=[];
x0=1*ones(1,np); % initial guess
options.MaxIter=1000;
global comb
comb.sys=sys;
comb.m=m;
comb.k=k;
comb.PaR=PaR;
comb.MoKe=MoKe;
func_call=@Par_Est;
[X,Ob]=fmincon(func_call,x0,H,b,Heq,beq,lb,ub,[],options);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Model updating
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
k_est=k;
k_est(PaR)=k_est(PaR).*X;
m_est=m;
zeta_est=zeros(1,dof);
zeta_est(MoKe)=sys.zetaS;
[MU,CdamU,KU]=Chain(m_est,zeta_est,k_est);
[PhiMU,omegaMU]=Model_Eig(MU,0*MU,KU,sys);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Visualization of the updating effects
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
omegaResNU=abs(omegaM(MoKe)-sys.omegaS.')./sys.omegaS.'*100;
MACNU=abs(diag(PhiM(:,MoKe)'*sys.PhiS)).^2./...
      (diag(PhiM(:,MoKe)'*PhiM(:,MoKe)).*diag(sys.PhiS'*sys.PhiS));
omegaResU=abs(omegaMU(MoKe)-sys.omegaS.')./sys.omegaS.'*100;
MACU=abs(diag(PhiMU(:,MoKe)'*sys.PhiS)).^2./...
     (diag(PhiMU(:,MoKe)'*PhiMU(:,MoKe)).*diag(sys.PhiS'*sys.PhiS));
figure;
subplot(1,2,1);
bar(MoKe,[omegaResNU,omegaResU]);
legend('Before the update','After the update')
xlabel('Mode (in the model)');
ylabel('System-model eigenfrequency discrepancy (%)');
subplot(1,2,2);
bar(MoKe,[MACNU,MACU]);
legend('Before the update','After the update')
xlabel('Mode (in the model)');
ylabel('System-model MAC value');
