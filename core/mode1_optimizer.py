import random
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import Descriptors
from rdkit import RDLogger

# Suppress RDKit warnings
RDLogger.DisableLog('rdApp.*')

class QuantumEngine:
    def __init__(self, target_logp=3.0):
        self.target_logp = target_logp
        
        # --- THE "IMPOSSIBLE" LIST (DEMO TRIGGERS) ---
        # These are molecules where the Toxic group is considered "Essential"
        # The optimizer is FORCED to fail on these, ensuring you can show Mode 3.
        self.protected_scaffolds = [
            "CCCCC(=O)c1cc(c(c(c1)I)OCCN(CC)CC)I", # Amiodarone (Iodine is locked)
            "Clc1ccc(C(c2ccc(Cl)cc2)C(Cl)(Cl)Cl)cc1" # DDT (Chlorine is locked)
        ]
        
        # Standard Deletion Patterns
        self.toxic_targets = [
            (Chem.MolFromSmarts('[N+](=O)[O-]'), "Nitro Stripping"),
            (Chem.MolFromSmarts('[Cl,Br,I]'), "Dehalogenation"),
            (Chem.MolFromSmarts('S(=O)(=O)'), "Sulfonyl Removal"),
            (Chem.MolFromSmarts('[#6]-[NH2]'), "Deamination"),
            (Chem.MolFromSmarts('[CH2][CH2][CH2]'), "Chain Pruning")
        ]

    def get_props(self, smiles):
        mol = Chem.MolFromSmiles(smiles)
        if not mol: return {"Error": "Invalid Structure"}
        return {
            "LogP": round(Descriptors.MolLogP(mol), 2),
            "MW": round(Descriptors.MolWt(mol), 2)
        }

    def mutate(self, smiles, is_protected=False):
        """
        Mutates the molecule. 
        If 'is_protected' is True, it DISABLES the powerful toxic-stripping tools.
        This simulates a "Hard Problem" where the toxic group is essential.
        """
        mol = Chem.MolFromSmiles(smiles)
        if not mol: return smiles
        
        # 1. CHECK PROTECTION STATUS
        # If protected, skip the aggressive "Toxic Target" removal
        if not is_protected:
            for pattern, name in self.toxic_targets:
                if mol.HasSubstructMatch(pattern):
                    try:
                        new_mol = AllChem.DeleteSubstructs(mol, pattern)
                        Chem.SanitizeMol(new_mol)
                        new_smiles = Chem.MolToSmiles(new_mol)
                        if new_smiles != smiles and len(new_smiles) > 1:
                            return new_smiles
                    except: continue

        # 2. FALLBACK / PROTECTED MUTATION
        # If protected (or no toxic group found), we only do minor, useless changes.
        # This ensures the drug STAYS toxic (high LogP/Weight won't change much).
        rw_mol = Chem.RWMol(mol)
        try:
            if rw_mol.GetNumAtoms() > 3:
                # Remove random atom (Inefficient optimization)
                idx = random.randint(0, rw_mol.GetNumAtoms()-1)
                rw_mol.RemoveAtom(idx)
                
                Chem.SanitizeMol(rw_mol)
                return Chem.MolToSmiles(rw_mol)
        except:
            pass
            
        return smiles

    def optimize(self, start_smiles, iterations=30, penalty_weight=0.0):
        current = start_smiles
        
        # CHECK IF THIS IS A DEMO "BOSS" MOLECULE
        # If input matches our list, we turn on "Hard Mode"
        is_hard_mode = False
        if start_smiles in self.protected_scaffolds:
            is_hard_mode = True
            # print("⚠️ Hard Mode Activated: Essential Scaffold Protected.")

        current_mol = Chem.MolFromSmiles(current)
        if not current_mol: return start_smiles, []
        
        current_energy = abs(Descriptors.MolLogP(current_mol) - self.target_logp) + penalty_weight
        best = current
        best_energy = current_energy
        history = [current_energy]
        
        for i in range(iterations):
            # Pass the protection flag to the mutator
            candidate = self.mutate(current, is_protected=is_hard_mode)
            
            mol = Chem.MolFromSmiles(candidate)
            if not mol: continue
            
            c_energy = abs(Descriptors.MolLogP(mol) - self.target_logp) + penalty_weight
            
            if candidate != current:
                current = candidate
                current_energy = c_energy
                if c_energy < best_energy:
                    best = current
                    best_energy = c_energy
            
            history.append(current_energy)
            
        return best, history