# Makefile para app_recetario

CONTAINER=app_recetario-recetario-1

up:
	docker compose up --build -d

down:
	docker compose down -v 

logs:
	docker compose logs -f

shell:
	docker exec -it $(CONTAINER) /bin/bash

migrate:
	docker exec -it $(CONTAINER) flask db upgrade

test:
	docker exec -it $(CONTAINER) pytest

seed:
	docker exec -it $(CONTAINER) python seed.py

ups:
	docker compose up --build -d
	docker exec -it $(CONTAINER) python seed.py

ps:
	docker ps

push:
	git add .
	git commit -m "$(word 2, $(MAKECMDGOALS))"
	git push
pull:
	git pull origin main

refresh:
	docker compose down -v && docker compose up --build -d

restart:
	docker compose down -v && docker compose up --build -d 
	docker exec -it $(CONTAINER) python seed.py

# Podés agregar más comandos si los necesitás
