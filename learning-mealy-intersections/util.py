import networkx
from aalpy.utils.AutomatonGenerators import mealy_from_state_setup, generate_random_mealy_machine
from intersection import IndependentLearner, MachineByMachineLearner, LazyWordByWordLearner


def from_dot_to_aalpydict(path):
    graph = networkx.nx_pydot.read_dot(path)
    graphdict = networkx.convert.to_dict_of_dicts(graph)
    new_dict = {}
    for input_state, input_state_dict in graphdict.items():
        new_dict[input_state] = {}
        for output_state, output_state_dict in input_state_dict.items():
            for _, transition in output_state_dict.items():
                input_and_output = transition["label"][1:-1].split('/')
                new_dict[input_state][input_and_output[0]] = (input_and_output[1],output_state)
    return new_dict

def from_dots_to_mealys(paths):
    machines = []
    for path in paths:
        machines.append(mealy_from_state_setup(from_dot_to_aalpydict(path)))
    return machines

def choose_learner(id, machines):
    match id:
        case "idp":
            learner = IndependentLearner(machines)
        case "wbw":
            learner = LazyWordByWordLearner(machines)
        case "mbm":
            learner = MachineByMachineLearner(machines)
    return learner

def generate_random_mealys(number_of_machines, machine_size, input_alphabet_length, output_alphabet):
    input_alphabet = [x for x in range(input_alphabet_length)]
    return [generate_random_mealy_machine(machine_size, input_alphabet, output_alphabet) for i in range(number_of_machines)]

def generate_random_sized_mealys(machine_sizes, input_alphabet_length, output_alphabet):
    input_alphabet = [x for x in range(input_alphabet_length)]
    return [generate_random_mealy_machine(i, input_alphabet, output_alphabet) for i in machine_sizes]

def generate_alphabet_ratio(ratio):
    alphabet = []
    for letter in range(len(ratio)):
        alphabet += [letter]*ratio[letter]
    return alphabet