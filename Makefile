.PHONY: all clean

all:
	@python3 pmo.py

clean:
	@rm -rf build cluster.gv cluster.gv.pdf
