#!/bin/sh
# wait-for.sh

set -e

host="$1"
port="$2"
shift 2
cmd="$@"

until nc -z "$host" "$port"; do
  echo "Esperando a $host:$port..."
  sleep 1
done

exec $cmd
