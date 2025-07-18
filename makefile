CONTAINER=recetario-recetario-1

# Comando para correr algo dentro del contenedor
run:
	docker exec -it $(CONTAINER) $(filter-out $@,$(MAKECMDGOALS))

# Comandos básicos
up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f || true

shell:
	docker exec -it $(CONTAINER) /bin/bash

migrate:
	make run flask db upgrade

test:
	make run pytest

restart:
	make down
	make up

ps:
	docker ps

push:
	git add .
	git commit -m "$(word 2, $(MAKECMDGOALS))"
	git push

pull:
	git pull origin main

# Permitir targets con argumentos al final
%:
	@:
