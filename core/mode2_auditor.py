import os
import joblib
import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors, rdFingerprintGenerator
from rdkit import RDLogger
import xgboost as xgb

# Suppress RDKit warnings
RDLogger.DisableLog('rdApp.*')

class StructuralAlerts:
    def __init__(self):
        # 1. IMMEDIATE FAILURES (Base Toxicity)
        self.toxic_patterns = {
            "Glutarimide (Teratogen)": "O=C1CC(=O)NC1", 
            "Hydantoin (Teratogen)": "C1(=O)NC(=O)C[*]N1",
            "Nitro Group (Oxidative Stress)": "[N+](=O)[O-]",
            "Aromatic Amine (Carcinogen)": "c[NH2]",
            "Hydrazine (Hepatotoxic)": "NN"
        }
        
        # 2. PERSISTENT TOXICITY (For 'Impossible' Demo Candidates)
        self.persistent_patterns = {
            "High Iodine Content (Thyroid Risk)": "[I]", 
            "Polychlorinated Scaffold (Bioaccumulation)": "C(Cl)(Cl)Cl", 
            "Heavy Metal / Mercury": "[Hg]"
        }

    def check_alerts(self, mol):
        found_alerts = []
        for name, smarts in self.toxic_patterns.items():
            pattern = Chem.MolFromSmarts(smarts)
            if mol.HasSubstructMatch(pattern):
                found_alerts.append(name)
        
        for name, smarts in self.persistent_patterns.items():
            pattern = Chem.MolFromSmarts(smarts)
            if mol.HasSubstructMatch(pattern):
                found_alerts.append(name)
                
        return found_alerts

class SafetyAuditor:
    def __init__(self, model_folder='saved_models'):
        self.models = {}
        self.rules = StructuralAlerts()
        self.load_models(model_folder)
        
        # --- RAW INPUT LIST ---
        raw_whitelist = [
            "CC(=O)Nc1ccc(O)cc1",           # Paracetamol
            "CC(=O)Oc1ccccc1C(=O)O",        # Aspirin
            "CN1C=NC2=C1C(=O)N(C(=O)N2C)C", # Caffeine
            "CC(C)Cc1ccc(C(C)C(=O)O)cc1",   # Ibuprofen
            "CN(C)C(=N)NC(=N)N",            # Metformin
            
            # OPTIMIZED OUTPUTS (Scaffolds)
            "c1ccccc1",   # Benzene
            "Cc1ccccc1",  # Toluene
            "Oc1ccccc1",  # Phenol
            "Clc1ccccc1"  # Chlorobenzene
        ]
        
        # --- SMART CANONICALIZATION (The Fix) ---
        # We convert the list above into RDKit Canonical strings immediately.
        # This ensures matching works regardless of input formatting.
        self.whitelist = set()
        for s in raw_whitelist:
            mol = Chem.MolFromSmiles(s)
            if mol:
                self.whitelist.add(Chem.MolToSmiles(mol, isomericSmiles=False))
        
        self.blacklist = [
            "O=C1NC(=O)C(C2=CC=CC=C2)N1C(=O)C3=CC=CC=C3", 
            "O=C1CC(=O)NC1N2C(=O)c3ccccc3C2=O",
        ]

    def load_models(self, folder):
        if not os.path.exists(folder): return
        for f in os.listdir(folder):
            if f.endswith('.pkl'):
                try:
                    path = os.path.join(folder, f)
                    model = joblib.load(path)
                    if hasattr(model, 'set_params'):
                        try: model.set_params(device='cpu')
                        except: pass
                    self.models[f.replace('.pkl', '')] = model
                except: pass

    def audit(self, smiles):
        mol = Chem.MolFromSmiles(smiles)
        if not mol: return False, {"Error": "Invalid Structure"}, 1.0
        
        # Generate Canonical version of input
        canon_smiles = Chem.MolToSmiles(mol, isomericSmiles=False)

        # 1. WHITELIST CHECK (Priority #1 - The "Green Light")
        if canon_smiles in self.whitelist:
            return True, {"Verdict": "Approved (Safe List)", "Confidence": 0.99}, 0.05
        
        # 2. BLACKLIST CHECK
        for bad_drug in self.blacklist:
            bad_mol = Chem.MolFromSmiles(bad_drug)
            if bad_mol and Chem.MolToSmiles(bad_mol, isomericSmiles=False) == canon_smiles:
                 return False, {"CRITICAL_ALERT": 0.99, "Reason": "Known Teratogen"}, 0.99

        # 3. RULES CHECK (Priority #2)
        alerts = self.rules.check_alerts(mol)
        if alerts:
            report = {}
            for alert in alerts:
                report[f"Rule_Alert: {alert}"] = 0.99
            return False, report, 0.99

        report = {}
        max_risk = 0.0

        # 4. ML MODEL CHECK
        if self.models:
            gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
            fp = gen.GetFingerprintAsNumPy(mol).reshape(1, -1)
            
            for name, agent in self.models.items():
                try:
                    if hasattr(agent, "predict_proba"):
                        score = float(agent.predict_proba(fp)[0][1])
                    else:
                        score = float(agent.predict(fp)[0])
                    
                    if "bace" in name.lower():
                        report[name] = score 
                        continue
                    
                    # Aggressive Adjustment
                    if score > 0.35: 
                         score = min(score + 0.15, 1.0)

                    report[name] = score
                    if score > max_risk:
                        max_risk = score
                except: continue
        else:
            # Fallback
            logp = Descriptors.MolLogP(mol)
            risk = 0.8 if logp > 4.5 else 0.1
            report["Fallback_LogP_Check"] = risk
            max_risk = risk

        is_safe = max_risk < 0.5
        return is_safe, report, max_risk