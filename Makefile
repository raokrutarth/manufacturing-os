

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


# ========= Running Expriments with 3 different cluster sizes and seeing results =========
#	make small-no-fail; make small-low-failure; make med-no-fail; make med-low-fail; make large-no-fail; make large-low-fail

large-no-fail:
	-timeout 300 python ./src/main.py --log_level warn --num_types 20 --nodes_per_type 2 --failure_rate 0 --recover_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	python ./src/parse_metrics.py

large-low-fail:
	-timeout 300 python ../src/main.py --log_level warn --num_types 20 --nodes_per_type 2 --failure_rate 1 --recovery_rate 1
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

med-low-fail:
	# compare with large-no-fail
	-timeout 300 python ./src/main.py --log_level warn --num_types 8 --nodes_per_type 2 --failure_rate 1 --recover_rate 1
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
