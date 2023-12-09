#  .DEFAULT_GOAL := clean

## Show files tree
tree:
	clear
	tree -L 3 -I __pycache__

## Delete all temporary files
clean:
	@echo "Clean Up..."
	find . -type f -iname ".DS_Store" -delete
	find . -type d -iname ".pytest_cache" -exec rm -r {} +
	find . -type d -iname "__pycache__" -exec rm -r {} +
	find . -type d -iname "htmlcov" -exec rm -r {} +
	find . -type f -iname ".coverage" -exec rm -r {} +

## Run tests
test:
	@echo "Testing..."
	poetry run pytest -vrP src/tests/

## Start development server
serve:
	@echo "Starting uvicorn server..."
	poetry run uvicorn main:app --port 5005 --app-dir src --reload

## Lint & format code
lint:
	@echo "Linting..."
	# poetry run ruff --fix src/
	poetry run black --line-length 220 --target-version py312 src/
	# poetry run flake8 src/

## Build docker image
build:
	@echo "Building Docker Image..."
	docker build -t ress/foldbknd .

## Run docker
run:
	@echo "Running Docker Image..."
	docker run --rm -p 5005:5005 ress/foldbknd

## Run docker as daemon
daemon:
	@echo "Running Docker Image as daemon..."
	docker run -d --restart unless-stopped -p 5005:5005 ress/foldbknd

## Clean test database
# dbclean:
# 	@echo "Running test db cleaning..."
# 	poetry run python src/maintenance/db_clean.py

## Run nginx in docker to host images
nginx:
	@echo "Running nginx in docker..."
	docker run --name my-nginx \
	-v /Users/ress/dev/Ursadate/uploads:/usr/share/nginx/html:ro \
	-p 80:80 \
	-d nginx

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available commands:$$(tput sgr0)"
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
