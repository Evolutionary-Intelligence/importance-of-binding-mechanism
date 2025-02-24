#
# Introduces the idea of trapping and justifies the use of the Milnes protocol.
#

import myokit
import os

import modelling

drugs = ['dofetilide', 'verapamil']
drug_concs = [30, 1000]  # nM
short_label = ['drug_free', 'dofetilide', 'verapamil']

data_dir = '../simulation_data/background/'
if not os.path.isdir(data_dir):
    os.makedirs(data_dir)

# Simulating the SD model with Milnes' protocol for 10 pulses after addition
# of example drug T (dofetilide-like drug) and example drug N (verapamil-like
# drug)

# Load hERG model
model = '../math_model/ohara-cipa-v1-2017-IKr-opt.mmt'
model, _, x = myokit.load(model)
current_model = modelling.BindingKinetics(model)

# Define Milnes' protocol
pulse_time = 25e3
Milnes_protocol = modelling.ProtocolLibrary().Milnes(pulse_time)
current_model.protocol = Milnes_protocol
repeats = 10

# Set simulation tolerance
abs_tol = 1e-7
rel_tol = 1e-8

# Simulate control condition
control_log = current_model.drug_simulation(drugs[0], 0, 1000, save_signal=10,
                                            abs_tol=abs_tol, rel_tol=rel_tol,
                                            protocol_period=pulse_time)
control_log.save_csv(data_dir + 'control_Milnes_current_pulses10.csv')

# Simulate 10 pulses from steady state for control condition
control_log_single = current_model.drug_simulation(
    drugs[0], 0, 1000, abs_tol=abs_tol, rel_tol=rel_tol,
    protocol_period=pulse_time)

# Simulate 10 pulses after addition of drugs from steady state
for i, conc_i in enumerate(drug_concs):

    log = current_model.drug_simulation(
        drugs[i], conc_i, repeats, save_signal=repeats,
        log_var=['engine.time', 'membrane.V', 'ikr.IKr'],
        set_state=control_log_single, abs_tol=abs_tol, rel_tol=rel_tol,
        protocol_period=pulse_time)
    log.save_csv(data_dir + drugs[i] + '_Milnes_current_pulses10.csv')

# Simulating the SD model with Milnes' protocol for 1000 pulses till steady
# state under drug free, addition of example drug T and example drug N
# conditions

# Simulate SD model under drug-free condition
repeats = 1000
log_control = current_model.drug_simulation(drugs[0], 0, repeats,
                                            abs_tol=abs_tol, rel_tol=rel_tol)
log_control.save_csv(data_dir + short_label[0] + '_Milnes_current.csv')

# Simulate the SD model under addition of drugs
for d in range(len(drugs)):
    log = current_model.drug_simulation(drugs[d], drug_concs[d], repeats,
                                        abs_tol=abs_tol, rel_tol=rel_tol)
    log.save_csv(data_dir + short_label[d + 1] + '_Milnes_current.csv')

# Simulating the SD model with AP clamp protocol for 1000 pulses till steady
# state under drug free, addition of example drug T and example drug N
# conditions

# Load AP model
APmodel = '../math_model/ohara-cipa-v1-2017-opt.mmt'
APmodel, _, x = myokit.load(APmodel)
AP_model = modelling.BindingKinetics(APmodel, current_head='ikr')

# Define current protocol
pulse_time = 1000
protocol = modelling.ProtocolLibrary().current_impulse(pulse_time)
AP_model.protocol = protocol

# Simulate AP for AP clamp protocol
APclamp = AP_model.drug_simulation(drugs[1], drug_concs[1], repeats,
                                   abs_tol=abs_tol, rel_tol=rel_tol)
APclamp.save_csv(data_dir + 'APclamp.csv')

# Set up AP clamp protocol
times = APclamp['engine.time']
voltages = APclamp['membrane.V']
tmax = times[-1] + 1

# Simulate SD model with AP clamp protocol under drug free condition
log_control = current_model.drug_APclamp(drugs[0], 0, times, voltages,
                                         tmax, repeats, abs_tol=abs_tol,
                                         rel_tol=rel_tol)
log_control.save_csv(data_dir + short_label[0] + '_APclamp_current.csv')

# Simulate the SD model under addition of drugs
for d in range(len(drugs)):
    log = current_model.drug_APclamp(drugs[d], drug_concs[d], times,
                                     voltages, tmax, repeats, abs_tol=abs_tol,
                                     rel_tol=rel_tol)
    log.save_csv(data_dir + short_label[d + 1] + '_APclamp_current.csv')
