.PHONY: all build run docker clean

all: run

build:
	docker build -t walk3r .

run:
	python3 app/go_walk3r.py

docker:
	docker run --rm -v $(PWD)/../padma:/src walk3r \
		--path /src/app --format dot --output /src/walk3r/deps

clean:
	rm -f ../padma/walk3r/deps.*
