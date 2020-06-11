

# run each target below for about 5 minutes
# and __

PY?=python

# runtime of each expriment
RT?=900

# ========= Running Expriments with different cluster sizes and print results =========
# RUn with target:	make run-expriments

s-no-fail:
	# compare with med-no-fail
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 5 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	mv ./tmp ./expriments/tmp-s-no-fail

med-no-fail:
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 20 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	mv ./tmp ./expriments/tmp-m-no-fail


l-no-fail:
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 150 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	mv ./tmp ./expriments/tmp-l-no-fail

xl-no-fail:
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 500 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	mv ./tmp ./expriments/tmp-xl-no-fail

xxl-no-fail:
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 1000 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	mv ./tmp ./expriments/tmp-xxl-no-fail

xxxl-no-fail:
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 2000 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./expriments/parse_metrics.py
	mv ./tmp ./expriments/tmp-xxxl-no-fail

no-fail: s-no-fail m-no-fail l-no-fail xl-no-fail xxl-no-fail xxxl-no-fail


all: no-fail