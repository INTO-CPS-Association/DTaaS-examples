"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% INPUT FILE TO CONDUCT MODEL UPDATING BASED ON VIBRATION MEASUREMENTS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
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
%------------------------------------------------------------------------------

"""
import numpy as np
from scipy.optimize import minimize
import json
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def model_upd(sys, m, k, PaR):
    """
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % MODEL UPDATING BASED ON VIBRATION MEASUREMENTS
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
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
    %--------------------------------------------------------------------------

    """
    
    # Nominal model
    M, Cdam, K = chain(m, np.array(m)*0, k)  # Omitting damping for now
    PhiM, omegaM = model_eig(M, Cdam, K, sys)
    
    # Initial pairing of experimental modes and model-based modes
    Odis = np.abs(np.subtract.outer(np.array(omegaM), np.array(sys['omegaS'])))
    r1 = np.argmin(Odis, axis=0)
    MoKe = mode_pair(sys['PhiS'], sys['omegaS'], PhiM, omegaM, r1)
    
    global comb
    comb = {'sys': sys, 'm': m, 'k': k, 'PaR': PaR, 'MoKe': MoKe}
       
    # Initial optimization
    x0 = np.ones(len(PaR))
    bounds = [(0.6, 1.4)] * len(PaR)
    res = minimize(par_est, x0, bounds=bounds, options={'maxiter': 1000})
    X = res.x
    
    # Model updating
    k_est = k.copy()
    k_est = np.array(k_est, dtype=np.float64)
    k_est[PaR] *= X
    m_est = m.copy()
    zeta_est = np.zeros_like(m)
    zeta_est[comb['MoKe']] = sys['zetaS']
    MU, CdamU, KU = chain(m_est, zeta_est, k_est)
    PhiMU, omegaMU = model_eig(MU, np.array(MU)*0, KU, sys)
    
    omegaResNU = np.abs(omegaM[MoKe] - sys['omegaS']) / sys['omegaS'] * 100
    MACNU = np.abs(np.abs(np.diag(PhiM[:, MoKe].conj().T @ sys['PhiS']))**2 / \
            (np.diag(PhiM[:, MoKe].conj().T @ PhiM[:, MoKe]) * np.diag(sys['PhiS'].conj().T @ sys['PhiS'])))
    omegaResU = np.abs(omegaMU[MoKe] - sys['omegaS']) / sys['omegaS'] * 100
    MACU = np.abs(np.abs(np.diag(PhiMU[:, MoKe].conj().T @ sys['PhiS']))**2 / \
            (np.diag(PhiMU[:, MoKe].conj().T @ PhiMU[:, MoKe]) * np.diag(sys['PhiS'].conj().T @ sys['PhiS'])))
    
    # Plotting
    fig, axs = plt.subplots(1, 2)
    MoKe = MoKe+1
    bar_width = 0.15
    # Plotting omegaResNU and omegaResU
    axs[0].bar(np.arange(len(MoKe)), omegaResNU, bar_width, label='Before the update')
    axs[0].bar(np.arange(len(MoKe))+bar_width, omegaResU, bar_width, label='After the update')
    axs[0].legend(loc="upper left")
    axs[0].set_xlabel('Mode (in the model)')
    axs[0].set_ylabel('System-model eigenfrequency discrepancy (%)')
    axs[0].set_xticks(np.arange(len(MoKe)))
    axs[0].set_xticklabels(MoKe)  # Assuming MoKe contains mode numbers
    
    # Plotting MACNU and MACU
    axs[1].bar(np.arange(len(MoKe)), MACNU, bar_width, label='Before the update')
    axs[1].bar(np.arange(len(MoKe))+bar_width, MACU, bar_width, label='After the update')
    axs[1].legend(loc="upper left")
    axs[1].set_xlabel('Mode (in the model)')
    axs[1].set_ylabel('System-model MAC value')
    axs[1].set_xticks(np.arange(len(MoKe)))
    axs[1].set_xticklabels(MoKe)  # Assuming MoKe contains mode numbers
    plt.tight_layout()    
    plt.show()
    
    return MU, CdamU, KU

def par_est(x):
    """
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % OPTIMIZATION FOR PARAMETER ESTIMATION
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
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
    %--------------------------------------------------------------------------
    
    """
    
    k = np.array(comb['k'], dtype=np.float64) 
    k[comb['PaR']] *= x  
    m = np.array(comb['m'])
    # dof = len(m)
    
    M, Cdam, K = chain(m, m*0, k)   
    PhiM, omegaM = model_eig(M, Cdam, K, comb['sys'])
    Odis = np.abs(np.subtract.outer(np.array(omegaM), np.array(comb['sys']['omegaS'])))
    r1 = np.argmin(Odis, axis=0)
    Rdis = r1 - comb['MoKe']
    
    if np.max(np.abs(Rdis)) > 0:
        Rloc = np.where(Rdis != 0)[0]
        MoKe2 = mode_pair(comb['sys']['PhiS'], comb['sys']['omegaS'], PhiM, omegaM, r1, comb['MoKe'], Rloc)
    else:
        MoKe2 = comb['MoKe']
    
    omegaMP = omegaM[MoKe2]
    PhiMP = PhiM[:, MoKe2]
    MACn = np.abs(np.diag(np.conj(comb['sys']['PhiS']).T @ PhiMP))**2
    MACd = np.diag(np.conj(comb['sys']['PhiS']).T @ comb['sys']['PhiS']) * np.diag(np.conj(PhiMP).T @ PhiMP)
    MAC = MACn / MACd
    
    # Objective function
    resOM = omegaMP - comb['sys']['omegaS']
    resPhi = MAC
    X = np.dot(resOM.T, resOM) + 1 / np.dot(resPhi.T, resPhi)
   
    return X

def chain(m, zeta, k):
    """
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % COMPUTATION OF MASS, DAMPING, AND STIFFNESS MATRICES FOR CHAIN SYSTEMS
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %
    % Input:
    %   m       - Point masses.
    %   zeta    - Damping ratios (assum. classical damping).
    %   k       - Spring stiffnesses.
    %
    % Output:
    %   M       - Mass matrix.
    %   C       - Damping matrix (assum. classical damping).
    %   K       - Stiffness matrix.
    %
    % /MDU 06-11-2023
    %--------------------------------------------------------------------------

    """
    
    dof = len(zeta)
    if dof != 1:
        kd = np.zeros(dof)
        kf = np.zeros(dof-1)
        for j in range(dof-1):
            kd[j] = k[j] + k[j+1]
            kf[j] = -k[j+1]
        kd[dof-1] = k[dof-1]
        K = np.diag(kf, 1) + np.diag(kf, -1) + np.diag(kd)
        M = np.diag(m)
        if np.max(zeta) == 0:
            C = np.zeros((dof, dof))
        else:
            aa11, bb = np.linalg.eig(K, M)
            omegaN = np.sqrt(np.diag(bb))
            dd = np.sqrt(np.diag(aa11.T @ M @ aa11))
            aa = aa11 @ np.diag(1 / dd)
            Cmodal = np.diag(2 * zeta * omegaN)
            C = np.linalg.inv(aa).T @ Cmodal @ np.linalg.inv(aa)
    else:
        K = k
        M = m
        C = 2 * zeta * np.sqrt(k * m)    
    return M, C, K

def model_eig(M, Cdam, K, sys):
    """
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % EIGENCHARACTERISTICS USING A STATE-SPACE FORMULATION
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %
    % Input:
    %   M        - Mass matrix.
    %   Cdam     - Damping matrix.
    %   K        - Stiffness matrix.
    %   sys      - Data structure with experimental data.
    %
    % Output:
    %   PhiM     - Mode shapes of the model.
    %   omegaM   - Eigenfrequencies of the model.
    %
    % /MDU 06-11-2023
    %--------------------------------------------------------------------------

    """
    
    dof = M.shape[0]
    AM = np.vstack((np.hstack((np.zeros((dof, dof)), np.eye(dof))), np.hstack((-np.linalg.inv(M) @ K, -np.linalg.inv(M) @ Cdam))))
   
    if sys['otype'] == 0:
        CMM = np.hstack((np.eye(dof), np.zeros((dof, dof))))
    elif sys['otype'] == 1:
        CMM = np.hstack((np.zeros((dof, dof)), np.eye(dof)))
    elif sys['otype'] == 2:
        CMM = AM[dof:, :]
    else:
        raise ValueError('A wrong output type has been chosen - please fix')

    CM = CMM[np.array(sys['oloc']-1), :]
    
    LambdaM, PhiM3 = np.linalg.eig(AM)
    OmegaM = np.sort(np.abs(LambdaM))
    omegaM = OmegaM[::2]  # Every second since Cdam=0
    PhiM3 = PhiM3[:, np.array(np.argsort(np.abs(LambdaM)))]
    PhiM2 = PhiM3[:, ::2]
    PhiM = CM @ PhiM2
    return PhiM, omegaM

def mode_pair(PhiS, omegaS, PhiM, omegaM, r1, MoKe=None, Rloc=None):
    """
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % PAIRING OF EXPERIMENTAL MODES AND MODEL-BASED MODES
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
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
    %--------------------------------------------------------------------------

    """
    if MoKe is None and Rloc is None:
        CaMo = len(omegaS)
        MoKe2 = r1
        Rloc = np.arange(CaMo)
    elif MoKe is not None and Rloc is not None:
        MoKe2 = MoKe
    else:
        raise ValueError('Incorrect input configuration for mode pairing - please fix.')
                    
    for pp in range(len(Rloc)):
        Rpp = Rloc[pp]
        MAC2 = np.abs(np.abs(PhiS[:, Rpp].T @ PhiM)**2 / (PhiS[:, Rpp].T @ PhiS[:, Rpp] * np.diag(PhiM.T @ PhiM)))
        il = np.argmax(np.real(MAC2))
        if il == r1[Rpp]:
            MoKe2[Rpp] = il
        elif il == MoKe2[Rpp] and np.abs(il - r1[Rpp]) == 1 and MAC2[il] > 0.8 and MAC2[il] > 2 * MAC2[r1[Rpp]]:
            print('Mismatch in eigenmode pairing - a choice based on MAC is made.')
        else:
            raise ValueError('A manual pairing of eigenmodes is necessary.')
    return MoKe2

def main():
    """
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Starting inputs
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    """
    # Load JSON input file
    with open('sys.json', 'r') as file:
        input_data = json.load(file)
    
    input_data['sys']['PhiS'] = np.array([[complex(*pair) for pair in row] for row in input_data['sys']['PhiS']])
    
    plt.imshow(mpimg.imread(r'../system-identification/Results/MAC_MCF.png'))
    plt.show(block=False)
    plt.pause(0.1)
    
    # Ask the user for input
    ReMo = input("Choose the physical modes to use for updating (ex.: [1,3,4]): ")
    ReMo = np.array(eval(ReMo))-1                     # Adjusting to 0-based indexing
    input_data['sys']['oloc'] = np.array([1,3,5])     # output DOF
    
    m  = [1]*5                          # initial mass of the model
    k  = [1000]*5                       # initial stiffness of the model
    PaR = np.array([1,2,4,5])           # number of parameters will be updated in stiffness matrix
    PaR = PaR-1                         # Adjusting to 0-based indexing
        
    sys = input_data['sys']
    sys['omegaS'] = [sys['omegaS'][ii] for ii in ReMo]
    sys['zetaS']  = [sys['zetaS'][ii] for ii in ReMo]
    sys['PhiS']   = sys['PhiS'][:, ReMo]
    
    if len(PaR) > len(sys['omegaS']):
        raise ValueError('The problem is underdetermined - please fix it.')
            
    MU, CdamU, KU = model_upd(sys, m, k, PaR)
    
    ReMo = ReMo+1
    
    # Save the results to JSON output file
    mod = {'MU': MU.tolist(), 'CdamU': CdamU.tolist(), 'KU': KU.tolist(), 'ReMo': ReMo.tolist(), 'oloc': input_data['sys']['oloc'].tolist()}
    with open('modUpd.json', 'w') as file:
        json.dump(mod, file)

if __name__ == '__main__':
    main()

