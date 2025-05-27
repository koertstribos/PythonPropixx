from pypixxlib.propixx import PROPixx #type: ignore

proj = PROPixx()
proj.setDlpSequencerProgram('RGB')
proj.updateRegisterCache()

