BASE_PATH=$(shell pwd)
PROJECT_NAME=wmata_trains
OUTPUT_PATH=$(BASE_PATH)/../output
BUILD_PATH=$(BASE_PATH)/BUILD
SRC=$(wildcard $(BASE_PATH)/$(PROJECT_NAME)/*.py)

DOCKER_CMD=docker run -it --rm -v $(BASE_PATH):$(BASE_PATH) -w $(BASE_PATH) localdev:latest 

.PHONY: clean dist lint pretty all

$(BUILD_PATH):
	@mkdir -p $(BUILD_PATH)

pretty: 
	$(DOCKER_CMD) python3 -m autopep8 --max-line-length 200 --in-place --verbose --aggressive $(SRC)

lint: 
	$(DOCKER_CMD) python3 -m flake8 --verbose --color always --max-line-length 200 --show-source $(SRC)
	

dist: lint $(BUILD_PATH) $(SRC)
	cp -r $(PROJECT_NAME) $(BUILD_PATH)

all: dist

clean:
	rm -r $(BUILD_PATH)
