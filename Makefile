

# run each target below for about 5 minutes
# and __

PY?=python

# runtime of each expriment
RT?=900

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
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 20 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-m-no-fail


l-no-fail:
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 150 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-l-no-fail

xl-no-fail:
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 500 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-xl-no-fail

xxl-no-fail:
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 1000 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-xxl-no-fail

xxxl-no-fail:
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 2000 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	rm -rf ./tmp/*.log
	mv ./tmp ./expriments/results/metrics-xxxl-no-fail

no-fail: s-no-fail m-no-fail l-no-fail xl-no-fail xxl-no-fail xxxl-no-fail


all: pre-run-setup no-fail