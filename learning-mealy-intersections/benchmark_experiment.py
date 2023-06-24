import util
from aalpy.automata.MealyMachine import MealyMachine

def run_dot_benchmarks():
    paths_of_paths = {
        "Mastercard":           ["benchmark_mealy/Mastercard/1_learnresult_MasterCard_fix.dot", "benchmark_mealy/Mastercard/10_learnresult_MasterCard_fix.dot"],
        "MAESTRO":              ["benchmark_mealy/MAESTRO/4_learnresult_MAESTRO_fix.dot", "benchmark_mealy/MAESTRO/ASN_learnresult_MAESTRO_fix.dot", "benchmark_mealy/MAESTRO/Rabo_learnresult_MAESTRO_fix.dot", "benchmark_mealy/MAESTRO/Volksbank_learnresult_MAESTRO_fix.dot"],
        "SecureCode":           ["benchmark_mealy/SecureCode/4_learnresult_SecureCode Aut_fix.dot", "benchmark_mealy/SecureCode/ASN_learnresult_SecureCode Aut_fix.dot", "benchmark_mealy/SecureCode/Rabo_learnresult_SecureCode_Aut_fix.dot"],
        "QUICprotocol":         ["benchmark_mealy/QUICprotocol/QUICprotocolwith0RTT.dot", "benchmark_mealy/QUICprotocol/QUICprotocolwithout0RTT.dot"],
        "SSH":                  ["benchmark_mealy/SSH/BitVise.dot", "benchmark_mealy/SSH/DropBear.dot", "benchmark_mealy/SSH/OpenSSH.dot"],
        "TCP_client":           ["benchmark_mealy/TCP_client/TCP_FreeBSD_Client.dot", "benchmark_mealy/TCP_client/TCP_Linux_Client.dot", "benchmark_mealy/TCP_client/TCP_Windows8_Client.dot"],
        "TCP_server":           ["benchmark_mealy/TCP_server/TCP_FreeBSD_Server.dot", "benchmark_mealy/TCP_server/TCP_Linux_Server.dot", "benchmark_mealy/TCP_server/TCP_Windows8_Server.dot"],
        "GnuTLS_client_full":   ["benchmark_mealy/GnuTLS_client_full/GnuTLS_3.3.8_client_full.dot", "benchmark_mealy/GnuTLS_client_full/GnuTLS_3.3.12_client_full.dot"],
        "GnuTLS_client_regular":["benchmark_mealy/GnuTLS_client_regular/GnuTLS_3.3.8_client_regular.dot", "benchmark_mealy/GnuTLS_client_regular/GnuTLS_3.3.12_client_regular.dot"],
        "GnuTLS_server_full":   ["benchmark_mealy/GnuTLS_server_full/GnuTLS_3.3.8_server_full.dot", "benchmark_mealy/GnuTLS_server_full/GnuTLS_3.3.12_server_full.dot"],
        "GnuTLS_server_regular":["benchmark_mealy/GnuTLS_server_regular/GnuTLS_3.3.8_server_regular.dot", "benchmark_mealy/GnuTLS_server_regular/GnuTLS_3.3.12_server_regular.dot"],
        "OpenSSL_client":       ["benchmark_mealy/OpenSSL_client/OpenSSL_1.0.2_client_regular.dot", "benchmark_mealy/OpenSSL_client/OpenSSL_1.0.1g_client_regular.dot", "benchmark_mealy/OpenSSL_client/OpenSSL_1.0.1j_client_regular.dot", "benchmark_mealy/OpenSSL_client/OpenSSL_1.0.1l_client_regular.dot"],
        "OpenSSL_server":       ["benchmark_mealy/OpenSSL_server/OpenSSL_1.0.2_server_regular.dot", "benchmark_mealy/OpenSSL_server/OpenSSL_1.0.1g_server_regular.dot", "benchmark_mealy/OpenSSL_server/OpenSSL_1.0.1j_server_regular.dot", "benchmark_mealy/OpenSSL_server/OpenSSL_1.0.1l_server_regular.dot"],
        "TLS_RSA_BSAFE_server": ["benchmark_mealy/TLS_RSA_BSAFE_server/RSA_BSAFE_Java_6.1.1_server_regular.dot", "benchmark_mealy/TLS_RSA_BSAFE_server/RSA_BSAFE_C_4.0.4_server_regular.dot"],
        "X-ray-system-PCS":     ["benchmark_mealy/x-ray-system-PCS/learnresult1.dot", "benchmark_mealy/x-ray-system-PCS/learnresult3.dot", "benchmark_mealy/x-ray-system-PCS/learnresult4.dot", "benchmark_mealy/x-ray-system-PCS/learnresult5.dot", "benchmark_mealy/x-ray-system-PCS/learnresult6.dot"]
        }
    lists_of_machines = {key : util.from_dots_to_mealys(paths) for key, paths in paths_of_paths.items()}
    learners = [util.choose_learner(learner, None) for learner in ["idp","wbw","mbm"]]
    with open("results/results_benchmarks.txt", "w") as f:
        for type_of_machine, list_of_machines in lists_of_machines.items():
            for i in range(20):
                total_sizes = [0 for i in list_of_machines]
                f.write(f"{type_of_machine}:\n")
                for learner in learners:
                    f.write(f"\tlearned with {str(learner)}:\n")
                    learner.automata = list_of_machines
                    machines = learner.run()
                    f.write(f"\t\t{learner.stats}\n")
                    learner.reset()
                f.write("\n\n")

if __name__ == "__main__":
    run_dot_benchmarks()
