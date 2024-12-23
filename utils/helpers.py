def sort_regions(regions):
    return sorted(regions, key=lambda x: x.get("name", "").lower())
