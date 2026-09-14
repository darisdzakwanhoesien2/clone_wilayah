#!/usr/bin/env python3
"""Generate a static JSON API (cascading province/city/district/village) from csv/*.csv.

Output layout (mirrors popular wilayah-indonesia static APIs, e.g. emsifa/api-wilayah-indonesia):

    api/provinces.json               -> [{id, name}, ...]
    api/regencies/<province_id>.json -> [{id, name}, ...]
    api/districts/<regency_id>.json  -> [{id, name}, ...]
    api/villages/<district_id>.json  -> [{id, name}, ...]

Host the api/ directory as-is (GitHub Pages, any static host, or a CDN) and fetch
the JSON files directly from the client for cascading dropdowns.
"""
import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(ROOT, "csv")
API_DIR = os.path.join(ROOT, "api")


def read_csv(name):
    path = os.path.join(CSV_DIR, name)
    with open(path, encoding="utf-8-sig", newline="") as f:
        yield from csv.DictReader(f, delimiter=";")


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


def group_by(rows, key):
    groups = {}
    for row in rows:
        groups.setdefault(row[key], []).append({"id": row["id"], "name": row["name"]})
    return groups


def main():
    provinces = list(read_csv("provinces.csv"))
    regencies = list(read_csv("regencies.csv"))
    districts = list(read_csv("districts.csv"))
    villages = list(read_csv("villages.csv"))

    write_json(
        os.path.join(API_DIR, "provinces.json"),
        [{"id": p["id"], "name": p["name"]} for p in provinces],
    )

    for province_id, items in group_by(regencies, "province_id").items():
        write_json(os.path.join(API_DIR, "regencies", f"{province_id}.json"), items)

    for regency_id, items in group_by(districts, "regency_id").items():
        write_json(os.path.join(API_DIR, "districts", f"{regency_id}.json"), items)

    for district_id, items in group_by(villages, "district_id").items():
        write_json(os.path.join(API_DIR, "villages", f"{district_id}.json"), items)

    print(f"provinces: {len(provinces)}")
    print(f"regencies: {len(regencies)} across {len(group_by(regencies, 'province_id'))} province files")
    print(f"districts: {len(districts)} across {len(group_by(districts, 'regency_id'))} regency files")
    print(f"villages:  {len(villages)} across {len(group_by(villages, 'district_id'))} district files")


if __name__ == "__main__":
    main()
