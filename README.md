### Warning: Not fully operational yet! Still under active development

## Darkstar: Yet another domain cataloging and resolving indexer
Hat-tip to [@silascutler](https://github.com/silascutler) :beers:

I finally found a use for [Hivemind](https://github.com/silascutler/HiveMindDB) (an ancient side-project) and decided it was just better to rewrite the whole damn thing. Especially since the vast majority of people that can potentially benefit from this little image probably don't have easy access to passiveDNS, etc.

![image](https://user-images.githubusercontent.com/2020115/86361560-0a9ac500-bc42-11ea-9d7b-bfeeda0e73e9.png)

### What does this do?
It lets you add domains to a doc store, periodically resolving them, while also preserving resolution history. Storage is backed by ElasticSearch.

The UI is entirely API driven, so developing against / automating resolutions is trivial. My usecase? I need to leverage the resolutions to split-route traffic through VPNs because .. raisins. This just gives me a quick and easy UI to manage (and organize) the various domains I need IPs tracked for.

### Env Variables this image wants (defaults to a local stack)

See the `example.env` file for deets

#### Notes about ES if you're running it locally/in a container/don't have an ES host available already
- `vm.max_map_count=262144` in `/etc/sysctl`
- Need to also set permissions on ES' data dir to be owned -R by 1000:1000