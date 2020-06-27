### Darkstar: Yet another domain cataloguing and resolving indexer
Hat-tip to @silascutler, I finally found a use for Hivemind and decided it was just better to rewrite the whole damn thing

### Env Variables this image wants (defaults to a local stack)

- ES_HOST=es
- ES_PORT=9200
- REDIS_HOST=redis
- REDIS_PORT=6379
- REDIS_DATABASE=0

### Compose file example for a local stack
```
version: '3'
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - 80:80
    networks:
      - darkstar
  es:
    image: elasticsearch:7.8.0
    environment:
      - node.name=es
      - cluster.name=es-darkstar
      - discovery.seed_hosts=es
      - cluster.initial_master_nodes=es
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - ${ES_DATA_DIR:?err}:/usr/share/elasticsearch/data
    networks:
      - darkstar
  redis:
    image: redis:6.0.5
    volumes:
      - ${REDIS_DATA_DIR:?err}:/data
    networks:
      - darkstar
networks:
  darkstar:
```

#### Notes about ES
- `vm.max_map_count=262144` in `/etc/sysctl`
- Need to also set permissions on ES' data dir to be owned -R by 1000:1000