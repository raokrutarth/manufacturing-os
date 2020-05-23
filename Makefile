
test:
	echo "running preset unit test"
	-python3.5 -m unittest discover -v -s src/ -p "*sc_stage.py"
	rm -rf src/*.pyc

run:
	LOGLEVEL=INFO python3.5 src/main.py

push: test
	git commit -am "automated make target commit & push"
	git push origin HEAD