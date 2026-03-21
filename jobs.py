import base64
import requests

BASE_URL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4"
API_KEY = "jobboerse-jobsuche"
JOB_DETAILS_URL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v3/jobdetails"

KEYWORDS = [
    'kommunikation',
    'queer',
    'gleichstellung',
    'gleichberechtigung',
    'diskriminierung',
    'erwachsenenbildung',
    'veranstaltung',
    'pressestelle',
    'referent',
    'gremium',
    'gremien',
    'frauen',
    'lgbtqi',
    'dozent',
    'philosophie',
    'sozialwissenschaft',
    'geisteswissenschaft',
    'gender studies',
    'politik',
    'vernetzung',
    'netzwerkarbeit',
    'projektverwaltung',
    'projektleitung',
    'berichterstattung',
    'workshop',
    'netzwerktreffen',
    'redaktion',
    'publikation',
    'museum',
    'ausstellung',
    'gesellschaft',
    'sexarbeit',
    'feminismus',
    'intersektional',
    'intersektionale',
    'rassismus',
]

def search_jobs(
    what: str | None = None,
    where: str | None = None,
    page: int = 1,
    size: int = 50,
):
    """
    Simple wrapper to search jobs via jobsuche.api.bund.dev.
    Adjust query parameters as needed; they are forwarded to
    the original Arbeitsagentur Jobsuche API.
    """
    endpoint = f"{BASE_URL}/jobs"
    params = {
        "angebotsart": 1,
        "veroeffentlichtseit": 30,
        "arbeitszeit": "vz;tz",
        "zeitarbeit": False,
        "page": page,
        "size": size,
    }
    headers = {
        "X-API-Key": API_KEY,
        "Accept": "application/json",
    }

    # 'was' and 'wo' correspond to the Arbeitsagentur Jobsuche API parameters
    if what:
        params["was"] = what       # e.g. "Softwareentwickler"
    if where:
        params["wo"] = where       # e.g. "Berlin"

    response = requests.get(endpoint, headers=headers, params=params, timeout=30)

    response.raise_for_status()
    return response.json()

def get_job_details(refnr):
    base64_str = base64.b64encode(bytes(refnr, 'utf-8')).decode('utf-8')
    headers = {
        "X-API-Key": API_KEY,
        "Accept": "application/json",
    }
    response = requests.get(f"{JOB_DETAILS_URL}/{base64_str}", headers=headers, timeout=30)

    response.raise_for_status()
    return response.json()

def convert_location(ort_data):
    return ort_data['ort']

def show_jobs(where: str | None = None, what: str | None = None):
    jobs_response = search_jobs(where=where, what=what, page=1, size=20)

    for idx, job in enumerate(jobs_response["stellenangebote"], start=1):
        # The following fields are examples; you may need to adjust them
        # after inspecting a real response.
        details = get_job_details(job["refnr"])
        matching = [ word for word in KEYWORDS if word in details['stellenangebotsBeschreibung'].lower().split() ]
        if len(matching) > 0:
            title = job.get("titel") or job.get("bezeichnung") or job.get("stellenbezeichnung")
            company = job.get("arbeitgeber") or job.get("firma")
            ort = convert_location(job.get("arbeitsort") or job.get("arbeitsorte"))
            url = job.get("externeURL") or details.get("externeURL")
            print(f"{idx}. {title} – {company} – {ort}")
            if url is not None:
                print(url)
            print("")
            print(details['stellenangebotsBeschreibung'])
            print(f"# Matches: {", ".join(matching)}")
            print("\n")


def main():
    show_jobs(where="Berlin")
    show_jobs(where="Marburg")


if __name__ == "__main__":
    main()