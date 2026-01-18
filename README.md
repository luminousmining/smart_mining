# smart_mining# smart_mining

## Database
Build
```sh
docker build -t smart_mining_database .
```

Run
```sh
docker run -d -p 5432:5432 --name smart_mining_database --network smart_mining_network smart_mining_database
```

## API
Build
```sh
docker build -t smart_mining_api .
```

Run
```sh
docker run -d -p 3000:3000 --name smart_mining_api --network smart_mining_network smart_mining_api
```

## Aggregator
Build
```sh
docker build -t smart_mining_aggregator .
```

Run
```sh
docker run -d --name smart_mining_aggregator --network smart_mining_network smart_mining_aggregator
```
