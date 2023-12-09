# Foldwrap backend

## Starting

1. Rename .env.example with test/fake credentials to .env:
```bash
mv .env.example .env
```

2. Run mongo and redis:
```bash
docker-compose -f docker-compose-4testing.yml up -d --build
```

3. Install dependencies
```bash
poetry install
```

4. Create 3 test-users to properly pass tests
```bash
poetry run pytest -vrP src/tests/manual_create_test_users.py
```

5. Run tests:
```bash
make test
or
poetry run pytest -vrP src/tests/
```

6. Run server:
```bash
make serve
or
poetry run uvicorn main:app --port 5005 --app-dir src --reload
```

7. Explore API endpoints:
```
http://127.0.0.1:5005/autodoc
```


## About project

This is only the backend part of [Foldwrap](https://foldwrap.com) project, which also have:

- Figma-to-DOM converter microservice written in Express.js
- Frontend on Nuxt 3
- Banner's editon on vanilla JavaScript
- Playwright end-to-end tests
- Deploytool for automated CI/CD on production server

Currently whole project have about 15k lines of my shitty code:

```bash
cloc . --exclude-dir=node_modules,dist,figma_tests_assets,.ruff_cache,.env,.pytest_cache,.nuxt,.output,logs,Makefile,testing_assets,mount,trash,Dockerfile --exclude-ext=svg,lockb,sh,ini,txt,toml

274 text files.
227 unique files.
216 files ignored.


-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Vuejs Component                 43           1616            715           4168
JavaScript                      59           1692           1696           3880
Python                          78           1438            933           2978
SCSS                            10            692            420           1777
HTML                             6            139             26            690
JSON                            13              3              0            437
Markdown                        12            186              5            326
YAML                             5             48            112            284
TypeScript                       1              2             14             34
-------------------------------------------------------------------------------
SUM:                           227           5816           3921          14574
-------------------------------------------------------------------------------
```