

# run each target below for about 5 minutes
# and __

demo-video:
	# TODO (Andrej) see if we can use strings for item types
	# unclear about num nodes dead at any time.
	/usr/bin/python3 ../src/main.py --num_types 5 --nodes_per_type 3 --failure_rate 1 --recovery_rate 1 >& /dev/null
	/usr/bin/python3 ./parse_metrics.py

large-no-fail:
	/usr/bin/python3 ../src/main.py --num_types 20 --nodes_per_type 20 --failure_rate 0 --recovery_rate 0 >& /dev/null

large-high-fail-rate-cluster:
	# at any time, >=30% of the cluster except the leader is down.
	/usr/bin/python3 ../src/main.py --num_types 20 --nodes_per_type 20 --failure_rate 20 --recovery_rate 20 >& /dev/null

large-low-fail-rate-cluster:
	# at any time, <30% of the cluster is down.
	/usr/bin/python3 ../src/main.py --num_types 20 --nodes_per_type 20 --failure_rate 3 --recovery_rate 3 >& /dev/null

med-no-fail:
	# compare with large-no-fail
	/usr/bin/python3 ../src/main.py --num_types 10 --nodes_per_type 5 --failure_rate 0 --recovery_rate 0 >& /dev/null

small-no-fail:
	# compare with med-no-fail
	# -timeout 5 /usr/bin/python3 ../src/main.py --num_types 5 --nodes_per_type 3 --failure_rate 0 --recovery_rate 0
	@printf "\n\n============\n"
	@printf "[+] Starting to parse expriment results at %s\n" "$$(date)"
	@printf "============\n"
	/usr/bin/python3 ./parse_metrics.py
