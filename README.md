### Darkstar: Yet another domain cataloguing and resolving indexer
Hat-tip to @silascutler, I finally found a use for Hivemind and decided it was just better to rewrite the whole damn thing

### What does this do?
It lets you add domains to a DB, and it will periodically resolve them, preserving history. Storage is backed by ElasticSearch.

### Env Variables this image wants (defaults to a local stack)

See the `example.env` file for deets

#### Notes about ES
- `vm.max_map_count=262144` in `/etc/sysctl`
- Need to also set permissions on ES' data dir to be owned -R by 1000:1000