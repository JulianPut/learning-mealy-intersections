from typing import Iterable
from statistics import mean
import util
import click
import random

class Learning_Random:
    def __init__(self, number_of_machines, machine_size, input_alphabet_size, output_alphabet_ratio, learner_strs, seed = 0, repeat = 100):
        self.seed = seed
        self.input_alphabet_size = input_alphabet_size
        self.output_alphabet = util.generate_alphabet_ratio(output_alphabet_ratio)
        self.number_of_machines = number_of_machines
        if isinstance(machine_size,Iterable) and len(machine_size) == 1:
            self.machine_size = machine_size[0]
        else:
            self.machine_size = machine_size
        self.learner = [util.choose_learner(learner_str, None) for learner_str in learner_strs]
        self.repeat = repeat
    
    def run(self):
        data = {}
        with open("results/results_random.txt","a") as f:
            for learner in self.learner:
                data[str(learner)] = []
                f.write(f"\tStrategy: {str(learner)}\n")
                for s in range(self.repeat):
                    learner.reset()
                    random.seed(self.seed + s)
                    f.write(f"\t\t({s+1}/{self.repeat})\n")
                    if isinstance(self.machine_size, Iterable):
                        machines = util.generate_random_sized_mealys(self.machine_size,self.input_alphabet_size,self.output_alphabet)
                    else:
                        machines = util.generate_random_mealys(self.number_of_machines, self.machine_size,self.input_alphabet_size,self.output_alphabet)
                    learner.automata = machines
                    learner.run()
                    data[str(learner)].append(learner.stats)
                    f.write(f"\t\t\t{learner.stats}\n")
                f.write("\n")
            for learner in self.learner:
                f.write(f"\tAverage data for {learner}:\n\t\t{mean_stats(data[str(learner)])}\n")
            f.write("\n\n")
        return data

    def reset(self):
        for learner in self.learner:
            learner.reset()

def mean_stats(total_data):
    return {
        "queries_learning": int(mean([data["queries_learning"] for data in total_data])),
        "steps_learning": int(mean([data["steps_learning"] for data in total_data])),
        "queries_eq_oracle": int(mean([data["queries_eq_oracle"] for data in total_data])),
        "steps_eq_oracle": int(mean([data["steps_eq_oracle"] for data in total_data])),
        "automaton_size": int(mean([data["automaton_size"] for data in total_data]))
    }
    
@click.command()
@click.option('--seed', default=0, help='Random seed')
@click.option('--repetitions', '-n', default=20, help="How often to repeat each benchmark")
@click.option('--learner', '-l', multiple=True, type=click.Choice(["idp", "wbw", "mbm"]), required=True)
def run_random_benchmarks(seed, repetitions, learner):
    settings = [
                [[1,1], 4, 3, 5],
                [[2,1], 4, 3, 5],
                [[4,1], 4, 3, 5],
                [[8,1], 4, 3, 5],
                [[16,1], 4, 3, 5],
                [[32,1], 4, 3, 5],

                [[4,1], 4, 4, 5],
                [[4,1], 4, 5, 5],
                [[4,1], 4, 6, 5],
    
                [[4,1], 4, 3, 6],
                [[4,1], 4, 3, 8],
                [[4,1], 4, 3, 10],

                [[16,1], 6, 3, 5],
                [[16,1], 8, 3, 5],
                [[16,1], 10, 3, 5],

                [[1,1], 4, 3, [3,5,7,11]],
                [[1,1], 4, 3, [11,7,5,3]],
                [[1,1], 6, 3, [3,5,7,11,13,17]],
                [[1,1], 6, 3, [17,13,11,7,5,3]],

                [[16,1], 3, 2, [2,2,20]],
                [[16,1], 3, 2, [3,3,20]]
            ]
    for setting in settings:
        run_random_benchmark(seed,repetitions, learner, setting[0], setting[1],setting[2],setting[3])

def run_random_benchmark(seed, repetitions, learner, ratio, nr_machines, nr_inputs, nr_states):
    with open("results/results_random.txt","a") as f:
        f.write(f"reps: {repetitions}, ratio: {ratio}, nr_machines: {nr_machines}, nr_inputs: {nr_inputs}, nr_states: {nr_states}, learners: {learner}\n\n")
    random.seed(seed)
    learning = Learning_Random(nr_machines, nr_states, nr_inputs, ratio, learner, seed, repetitions)
    data = learning.run()
    for learn in learner:
        print(str(learn), mean_stats(data[str(learn)]))

        
if __name__ == "__main__":
    run_random_benchmarks()