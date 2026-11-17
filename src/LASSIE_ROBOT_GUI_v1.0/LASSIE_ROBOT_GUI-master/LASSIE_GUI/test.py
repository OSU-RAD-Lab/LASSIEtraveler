from traveler_decision_making import *
from env_wrapper import *
Traveler_DM = DecisionMaking()
Traveler_ENV = ENV()
location_list = list(np.linspace(1,22,22, dtype=int))
sample_list = list(3 * np.ones(22, dtype=int))


location =  [ 2, 11, 15, 20,  6,  4 , 9, 13, 18, 22,  1, 17,  8, 22,  1]
sample = [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]
mm, erodi = Traveler_ENV.get_data_state([location,sample])
Traveler_DM.update_current_state(location, sample, mm, erodi)


for i in range(10):
    mm, erodi = Traveler_ENV.get_data_state([location,sample])
    Traveler_DM.update_current_state(location, sample, mm, erodi)
    Traveler_DM.handle_spatial_information_coverage()
    Traveler_DM.handle_variable_information_coverage()
    Traveler_DM.handle_discrepancy_coverage()
    results = Traveler_DM.calculate_suggested_location()
    plot(Traveler_DM,Traveler_ENV, location, sample, erodi, results)
    spatial_selection = np.array(results['discrepancy_locs']) + 1
    location.append(spatial_selection[0])
    sample.append(3)

    


