## Darkstar: Yet another domain cataloguing and resolving indexer
Hat-tip to [@silascutler](https://github.com/silascutler) :beers:

I finally found a use for [Hivemind]() (an ancient side-project) and decided it was just better to rewrite the whole damn thing. Esp since the vast majority of people that could potentially benefit from this little image probably don't have easy access to passiveDNS, etc.

![image](https://user-images.githubusercontent.com/2020115/85961728-70edc200-b97a-11ea-8f5e-446aaa0add11.png)

### What does this do?
It lets you add domains to a doc store, perodically resolving them, while also preserving resolution history. Storage is backed by ElasticSearch.

It's entirely API backed, so you can do what ever your heart desires with the results. Me? I need to leverage the resolutions to split-route traffic through VPNs because .. raisins. This just gives me a quick and easy UI to manage (and organize) the various domains I need IPs tracked for.

### Env Variables this image wants (defaults to a local stack)

See the `example.env` file for deets

#### Notes about ES
- `vm.max_map_count=262144` in `/etc/sysctl`
- Need to also set permissions on ES' data dir to be owned -R by 1000:1000