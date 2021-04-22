from automata.fa.dfa import DFA
# DFA which matches all binary strings ending in an odd number of '1's
dfa = DFA(
    states={'q1', 'q2', 'q4', 'q5', 'q6'},
    input_symbols={'0', '1'},
    transitions={
        'q1': {'0': 'q0', '1': 'q1'}
    },
    initial_state='q0',
    final_states={'q0'}
)

#print(dfa.read_input('01'))

dfa.validate()