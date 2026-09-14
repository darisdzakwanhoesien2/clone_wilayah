#!/usr/bin/env python3
"""Generate a static JSON API (cascading province/city/district/village) from csv/*.csv.

Output layout (mirrors popular wilayah-indonesia static APIs, e.g. emsifa/api-wilayah-indonesia):

    api/provinces.json               -> [{id, name}, ...]
    api/regencies/<province_id>.json -> [{id, name}, ...]
    api/districts/<regency_id>.json  -> [{id, name}, ...]
    api/villages/<district_id>.json  -> [{id, name, postal_code}, ...]

Postal codes come from csv/postal_codes.csv (village_id;postal_code), sourced from
cahyadsn/wilayah_kodepos (MIT) — see README. A village missing from that dataset
gets postal_code: null.

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


def group_by(rows, key, extra_fields=()):
    groups = {}
    for row in rows:
        item = {"id": row["id"], "name": row["name"]}
        for field in extra_fields:
            item[field] = row.get(field)
        groups.setdefault(row[key], []).append(item)
    return groups


def main():
    provinces = list(read_csv("provinces.csv"))
    regencies = list(read_csv("regencies.csv"))
    districts = list(read_csv("districts.csv"))
    villages = list(read_csv("villages.csv"))

    postal_codes = {row["village_id"]: row["postal_code"] for row in read_csv("postal_codes.csv")}
    for village in villages:
        village["postal_code"] = postal_codes.get(village["id"])

    write_json(
        os.path.join(API_DIR, "provinces.json"),
        [{"id": p["id"], "name": p["name"]} for p in provinces],
    )

    for province_id, items in group_by(regencies, "province_id").items():
        write_json(os.path.join(API_DIR, "regencies", f"{province_id}.json"), items)

    for regency_id, items in group_by(districts, "regency_id").items():
        write_json(os.path.join(API_DIR, "districts", f"{regency_id}.json"), items)

    for district_id, items in group_by(villages, "district_id", extra_fields=("postal_code",)).items():
        write_json(os.path.join(API_DIR, "villages", f"{district_id}.json"), items)

    matched = sum(1 for v in villages if v["postal_code"])
    print(f"provinces: {len(provinces)}")
    print(f"regencies: {len(regencies)} across {len(group_by(regencies, 'province_id'))} province files")
    print(f"districts: {len(districts)} across {len(group_by(districts, 'regency_id'))} regency files")
    print(f"villages:  {len(villages)} across {len(group_by(villages, 'district_id'))} district files")
    print(f"postal codes matched: {matched}/{len(villages)}")


if __name__ == "__main__":
    main()
