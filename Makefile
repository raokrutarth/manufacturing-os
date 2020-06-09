

# run each target below for about 5 minutes
# and __

PY?=python

# runtime of each expriment
RT?=600

demo-video:
	# TODO (Andrej) see if we can use strings for item types
	# unclear about num nodes dead at any time.
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 5 --nodes_per_type 3 --failure_rate 1 --recover_rate 1
	@printf "\n\n============\n"
	@printf "[+] Starting to parse experiment results at %s\n" "$$(date)"
	@printf "============\n"
	$(PY) ./src/parse_metrics.py


# ========= Running Expriments with 3 different cluster sizes and seeing results =========
#	make run-expriments

large-no-fail:
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 20 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./src/parse_metrics.py
	-mv ./tmp ./tmp-large-no-fail

large-low-fail:
	-timeout $(RT) $(PY) ../src/main.py --log_level warn --num_types 20 --nodes_per_type 2 --failure_rate 2 --recovery_rate 2
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./src/parse_metrics.py
	-mv ./tmp ./tmp-large-low-fail

med-no-fail:
	# compare with large-no-fail
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 8 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./src/parse_metrics.py
	-mv ./tmp ./tmp-med-no-fail

med-low-fail:
	# compare with large-no-fail
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 8 --nodes_per_type 2 --failure_rate 1 --recover_rate 1
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./src/parse_metrics.py
	-mv ./tmp ./tmp-med-low-fail

small-no-fail:
	# compare with med-no-fail
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 5 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./src/parse_metrics.py
	-mv ./tmp ./tmp-small-no-fail

small-low-failure:
	# compare with med-no-fail
	-timeout $(RT) $(PY) ./src/main.py --log_level warn --num_types 5 --nodes_per_type 2 --failure_rate 1 --recover_rate 1
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	-$(PY) ./src/parse_metrics.py
	-mv ./tmp ./tmp-small-low-failure


run-expriments: small-no-fail small-low-failure med-no-fail med-low-fail large-no-fail large-low-fail
