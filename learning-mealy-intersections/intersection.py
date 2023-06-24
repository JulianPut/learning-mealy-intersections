from typing import Iterable
from statistics import mean
from aalpy.automata.MealyMachine import MealyMachine
from aalpy.learning_algs.deterministic.LStar import run_Lstar
from aalpy.base.SUL import SUL
from aalpy.oracles import RandomWMethodEqOracle

class _FilterMealySUL(SUL):
    mealy_machine = MealyMachine
    filter_sul = SUL
    in_sink = False
    def __init__(self, mealy_machine: MealyMachine, filter_machine:MealyMachine):
        super().__init__()
        self.mealy_sul = _SingleMealySUL(mealy_machine)
        self.filter_sul = _SingleMealySUL(filter_machine)
        self.in_sink = False
        self.num_steps  = 0
        self.num_queries  = 0

    def query(self, word: tuple) -> list:
        self.num_queries  += 1
        self.pre()
        result = []
        for letter in word:
            result.append(self.step(letter))
        self.post()
        return result

    def pre(self):
        self.mealy_sul.pre()
        self.filter_sul.pre()
        self.in_sink = False

    def post(self):
        self.mealy_sul.post()
        self.filter_sul.post()

    def step(self, letter):
        if self.in_sink:
            return "tau"
        filter_output = self.filter_sul.step(letter)
        if filter_output == "tau":
            self.in_sink = True
            return "tau"
        mealy_output = self.mealy_sul.step(letter)
        self.num_steps += 1
        if mealy_output != filter_output:
            self.in_sink = True
            return "tau"
        else:
            return mealy_output

class _SingleMealySUL(SUL):
    mealy_machine = MealyMachine
    input_alphabet = Iterable
    def __init__(self, mealy_machine: MealyMachine):
        super().__init__()
        self.mealy_machine = mealy_machine
        self.input_alphabet = mealy_machine.get_input_alphabet()
        self.num_steps = 0
        self.num_queries  = 0

    def query(self, word: tuple) -> list:
        self.num_queries  += 1
        self.pre()
        output = []
        for letter in word:
            output.append(self.step(letter))
        self.post()
        return output

    def pre(self):
        self.mealy_machine.reset_to_initial()

    def post(self):
        pass

    def step(self, letter):
        if letter not in self.input_alphabet:
            return "tau"
        self.num_steps += 1
        return self.mealy_machine.step(letter)

class _IntersectionMealySUL(SUL):
    suls = list[_SingleMealySUL]
    in_sink = False
    def __init__(self, mealy_machines: list[MealyMachine]):
        super().__init__()
        self.suls = []
        for mealy_machine in mealy_machines:
            self.suls.append(_SingleMealySUL(mealy_machine))
        self.in_sink = False
        self.num_steps = 0
        self.num_queries  = 0

    def query(self, word: tuple) -> list:
        self.num_queries  += 1
        self.pre()
        result = []
        for letter in word:
            result.append(self.step(letter))
        self.post()
        return result

    def pre(self):
        for mealysul in self.suls:
            mealysul.pre()
        self.in_sink = False

    def post(self):
        pass

    def step(self, letter):
        if self.in_sink:
            return "tau"
        self.num_steps += 1
        result = self.suls[0].step(letter)
        for sul in self.suls[1:]:
            self.num_steps += 1
            out = sul.step(letter)
            if result != out:
                self.in_sink = True
                return "tau"
            result = out
        return result
    
class _MealyLearner:
    def __init__(self, use_cache, cache_sul_queries):
        self._data = []
        self._use_cache = use_cache
        self._cache_sul_queries = cache_sul_queries

    def run(self, machines_to_be_learned, filter_machine = None):
        assert not (isinstance(machines_to_be_learned, Iterable) and filter_machine is not None)

        if isinstance(machines_to_be_learned, Iterable):
            alphabet = []
            for machine in machines_to_be_learned:
                [alphabet.append(letter) for letter in machine.get_input_alphabet()]
        else:
            alphabet = machines_to_be_learned.get_input_alphabet()

        if filter_machine is None:
            if isinstance(machines_to_be_learned, Iterable):
                sul = _IntersectionMealySUL(machines_to_be_learned)
            else:
                sul = _SingleMealySUL(machines_to_be_learned)
        else:
            sul = _FilterMealySUL(machines_to_be_learned, filter_machine)
        oracle = RandomWMethodEqOracle(alphabet, sul, 12, 12)

        mealy, data = run_Lstar(alphabet, sul, oracle, 'mealy', None, 'shortest_first' ,cache_and_non_det_check= False, return_data= True, print_level=0)
        self._data.append(data)
        return mealy

    def reset(self):
        self._data = []

    def data_index(self, i):
        return {
            "queries_learning": self._data[i]["queries_learning"],
            "steps_learning": self._data[i]["steps_learning"],
            "queries_eq_oracle": self._data[i]["learning_rounds"],
            "steps_eq_oracle": self._data[i]["steps_eq_oracle"],
            "automaton_size": self._data[i]["automaton_size"]
        }

    @property
    def stats(self):
        return {
            "queries_learning": sum([data["queries_learning"] for data in self._data]),
            "steps_learning": sum([data["steps_learning"] for data in self._data]),
            "queries_eq_oracle": sum([data["learning_rounds"] for data in self._data]),
            "steps_eq_oracle": sum([data["steps_eq_oracle"] for data in self._data]),
            "automaton_size": sum([data["automaton_size"] for data in self._data])
        }
    
    @property
    def mean_stats(self):
        return {
            "queries_learning": int(mean([data["queries_learning"] for data in self._data])),
            "steps_learning": int(mean([data["steps_learning"] for data in self._data])),
            "queries_eq_oracle": int(mean([data["learning_rounds"] for data in self._data])),
            "steps_eq_oracle": int(mean([data["steps_eq_oracle"] for data in self._data])),
            "automaton_size": int(mean([data["automaton_size"] for data in self._data]))
        }

class _AbstractIntersectionLearner():
    def __init__(self, individual_automata: list[MealyMachine], use_cache=False, cache_queries=False):
        self.automata = individual_automata
        self.learner_uses_cache = use_cache
        self.mealy_learner = _MealyLearner(use_cache, cache_queries)

    def run(self):
        pass

    def _learn_automaton(self, aut, filter_machine=None):
        return self.mealy_learner.run(aut, filter_machine)

    def reset(self):
        self.mealy_learner.reset()

    def data_index(self, i):
        return self.mealy_learner.data_index(i)

    @property
    def stats(self):
        return self.mealy_learner.stats
    
    @property
    def mean_stats(self):
        return self.mealy_learner.mean_stats


class IndependentLearner(_AbstractIntersectionLearner):
    def run(self):
        learned_automata = [self._learn_automaton(aut) for aut in self.automata]
        return learned_automata

    def __str__(self):
        return "idp"

class LazyWordByWordLearner(_AbstractIntersectionLearner):
    def run(self):
        return self._learn_automaton(self.automata)
    def __str__(self):
        return "wbw"
    
class MachineByMachineLearner(_AbstractIntersectionLearner):
    def run(self):
        learned_automaton = self._learn_automaton(self.automata[0])
        [learned_automaton := self._learn_automaton(aut, learned_automaton) for aut in self.automata[1:]]
        return learned_automaton
    def __str__(self):
        return "mbm"