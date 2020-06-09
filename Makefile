

# run each target below for about 5 minutes
# and __

demo-video:
	# TODO (Andrej) see if we can use strings for item types
	# unclear about num nodes dead at any time.
	-timeout 300 python ./src/main.py --log_level warn --num_types 5 --nodes_per_type 3 --failure_rate 1 --recover_rate 1
	@printf "\n\n============\n"
	@printf "[+] Starting to parse experiment results at %s\n" "$$(date)"
	@printf "============\n"
	python ./src/parse_metrics.py


large-no-fail:
	-timeout 300 python ./src/main.py --log_level warn --num_types 20 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	python ./src/parse_metrics.py

large-high-fail-rate-cluster:
	# at any time, >=30% of the cluster except the leader is down.
	/usr/bin/python3 ../src/main.py --num_types 20 --nodes_per_type 20 --failure_rate 20 --recovery_rate 20 >& /dev/null

large-low-fail-rate-cluster:
	# at any time, <30% of the cluster is down.
	/usr/bin/python3 ../src/main.py --num_types 20 --nodes_per_type 20 --failure_rate 3 --recovery_rate 3 >& /dev/null
	-timeout 40 python ./src/main.py --log_level warn --num_types 20 --nodes_per_type 20 --failure_rate 3 --recover_rate 3
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	python ./src/parse_metrics.py


med-no-fail:
	# compare with large-no-fail
	-timeout 300 python ./src/main.py --log_level warn --num_types 8 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	python ./src/parse_metrics.py


small-no-fail:
	# compare with med-no-fail
	-timeout 300 python ./src/main.py --log_level warn --num_types 5 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	python ./src/parse_metrics.py


small-low-failure:
	# compare with med-no-fail
	-timeout 300 python ./src/main.py --log_level warn --num_types 5 --nodes_per_type 2 --failure_rate 1 --recover_rate 1
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	python ./src/parse_metrics.py
