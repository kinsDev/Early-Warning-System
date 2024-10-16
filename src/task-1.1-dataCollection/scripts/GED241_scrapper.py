import requests
import csv
from tqdm import tqdm

base_url = "https://ucdpapi.pcr.uu.se/api/gedevents/24.1"

def fetch_ucdp_data_pagination(n_rows=None):
    page = 0
    page_size = 100 # adjust based on hardware capabilities
    total_fetched = 0

    with open("ucdp_data.csv", mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            'id', 'relid', 'year', 'active_year', 'code_status', 'type_of_violence', 
            'conflict_dset_id', 'conflict_new_id', 'conflict_name', 'dyad_dset_id',
            'dyad_new_id', 'dyad_name', 'side_a_dset_id', 'side_a_new_id', 'side_a',
            'side_b_dset_id', 'side_b_new_id', 'side_b', 'number_of_sources',
            'source_article', 'source_office', 'source_date', 'source_headline',
            'source_original', 'where_prec', 'where_coordinates',
            'where_description', 'adm_1', 'adm_2', 'latitude', 'longitude',
            'geom_wkt', 'priogrid_gid', 'country', 'country_id', 'region',
            'event_clarity', 'date_prec', 'date_start', 'date_end', 'deaths_a',
            'deaths_b', 'deaths_civilians', 'deaths_unknown', 'best', 'high', 'low',
            'gwnoa', 'gwnob'
        ])

        with tqdm(desc="Fetching UCDP data", unit="rows") as pbar:
            while True:
                # preparing the request
                params = {'pagesize': page_size, 'page': page}
                response = requests.get(base_url, params=params)
                data = response.json()

                if not data['Result']:
                    break

                for event in data['Result']:
                    writer.writerow([
                        event.get('id', None), event.get('relid', None), event.get('year', None),
                        event.get('active_year', None), event.get('code_status', None),
                        event.get('type_of_violence', None), event.get('conflict_dset_id', None),
                        event.get('conflict_new_id', None), event.get('conflict_name', None),
                        event.get('dyad_dset_id', None), event.get('dyad_new_id', None),
                        event.get('dyad_name', None), event.get('side_a_dset_id', None),
                        event.get('side_a_new_id', None), event.get('side_a', None),
                        event.get('side_b_dset_id', None), event.get('side_b_new_id', None),
                        event.get('side_b', None), event.get('number_of_sources', None),
                        event.get('source_article', None), event.get('source_office', None),
                        event.get('source_date', None), event.get('source_headline', None),
                        event.get('source_original', None), event.get('where_prec', None),
                        event.get('where_coordinates', None), event.get('where_description', None),
                        event.get('adm_1', None), event.get('adm_2', None), event.get('latitude', None),
                        event.get('longitude', None), event.get('geom_wkt', None),
                        event.get('priogrid_gid', None), event.get('country', None),
                        event.get('country_id', None), event.get('region', None),
                        event.get('event_clarity', None), event.get('date_prec', None),
                        event.get('date_start', None), event.get('date_end', None),
                        event.get('deaths_a', None), event.get('deaths_b', None),
                        event.get('deaths_civilians', None), event.get('deaths_unknown', None),
                        event.get('best', None), event.get('high', None), event.get('low', None),
                        event.get('gwnoa', None), event.get('gwnob', None)
                    ])
                    total_fetched += 1
                    pbar.update(1)

                    # stopping if n_rows is reached
                    if n_rows and total_fetched >= n_rows:
                        print(f"\nReached {n_rows} rows. Stopping fetch.")
                        return

                page += 1

    print(f"\nFinished fetching {total_fetched} rows of UCDP data.")

# n_rows: Number of rows to fetch. None fetches all rows.
fetch_ucdp_data_pagination()
