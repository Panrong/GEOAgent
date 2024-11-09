import GEOparse

a = GEOparse.get_GEO("GSE188847")
for x in a.metadata.keys():
    print(x)