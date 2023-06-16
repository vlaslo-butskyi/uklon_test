# Uklon Test

Here we have `docker-compose.yaml` that running: 
- driver_app for getting/writing and analyze data
- generator, that create random data for sending into driver_app
- and also postgresql for saving all data about drivers and their adventures

For run need:
- `docker compose build`
- `docker compose up -d`
