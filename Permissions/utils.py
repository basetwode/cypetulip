

def show_urls(urllist, depth=0, name="",url_prefix="", urls={}):

    for entry in urllist:
        if 'admin' not in entry.regex.pattern:
            if depth == 0:
                name = entry.regex.pattern
                urls[name]={}
            else:
                if hasattr(entry, 'name'):
                    urls[name][entry.name] = url_prefix+entry.regex.pattern
                elif not hasattr(entry, 'url_patterns'):
                    urls[name][entry.regex.pattern]=url_prefix+entry.regex.pattern


            print("  " * depth, entry.regex.pattern)
            if hasattr(entry, 'name'):
                print("  " * depth, entry.name)
            if hasattr(entry, 'url_patterns'):
                show_urls(entry.url_patterns, depth + 1,name,url_prefix+entry.regex.pattern,urls)

