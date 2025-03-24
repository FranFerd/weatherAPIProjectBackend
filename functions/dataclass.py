from dataclasses import dataclass

@dataclass
class Current_conditions_filtered:
    current_time : str
    temperature : str
    feels_like : str
    description : str
    precipitaion_probability : str
    precipitation_type : list
