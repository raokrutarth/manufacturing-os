

# run each target below for about 5 minutes
# and __

PY?=python

# runtime of each expriment
RT?=600

# ========= Running Expriments with different cluster sizes and print results =========
# RUn with target:	make run-expriments

pre-run-setup:
	rm -rf ./expriments/results
	mkdir ./expriments/results

s-no-fail:
	# compare with med-no-fail
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 5 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-s-no-fail

m-no-fail:
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 10 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-m-no-fail


l-no-fail:
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 15 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-l-no-fail

xl-no-fail:
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 20 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-xl-no-fail

xxl-no-fail:
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 25 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-xxl-no-fail

xxxl-no-fail:
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 30 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-xxxl-no-fail

no-fail: xxxl-no-fail  xxl-no-fail xl-no-fail m-no-fail l-no-fail s-no-fail


# failure cases 

s-fail_0:
	# compare with med-no-fail
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 6 --nodes_per_type 3 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-s-fail_0


s-fail_1:
	# compare with med-no-fail
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 6 --nodes_per_type 3 --failure_rate 1 --recover_rate 1
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-s-fail_1

s-fail_2:
	# compare with med-no-fail
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 6 --nodes_per_type 3 --failure_rate 2 --recover_rate 2
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-s-fail_2

s-fail_3:
	# compare with med-no-fail
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 6 --nodes_per_type 3 --failure_rate 3 --recover_rate 3
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-s-fail_3

s-fail_4:
	# compare with med-no-fail
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 6 --nodes_per_type 3 --failure_rate 4 --recover_rate 4
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-s-fail_4

s-fail_5:
	# compare with med-no-fail
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 6 --nodes_per_type 3 --failure_rate 5 --recover_rate 5
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-s-fail_5

s-fail_10:
	# compare with med-no-fail
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 6 --nodes_per_type 3 --failure_rate 10 --recover_rate 10
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-s-fail_10

s-fail_20:
	# compare with med-no-fail
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 6 --nodes_per_type 3 --failure_rate 20 --recover_rate 20
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-s-fail_20

s-fail_30:
	# compare with med-no-fail
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 6 --nodes_per_type 3 --failure_rate 30 --recover_rate 30
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-s-fail_30

s-fail_40:
	# compare with med-no-fail
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 6 --nodes_per_type 3 --failure_rate 40 --recover_rate 40
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-s-fail_40

s-fail_50:
	# compare with med-no-fail
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 6 --nodes_per_type 3 --failure_rate 50 --recover_rate 50
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-s-fail_50


s-fail_60:
	# compare with med-no-fail
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 6 --nodes_per_type 3 --failure_rate 60 --recover_rate 60
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-s-fail_60


fail: s-fail_0 s-fail_1 s-fail_5 s-fail_10 s-fail_20 s-fail_30 s-fail_40 s-fail_50 s-fail_60 

all: pre-run-setup fail no-fail
