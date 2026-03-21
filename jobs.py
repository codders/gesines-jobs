import base64
import requests
from itertools import chain

class Job:

    def __init__(self, job_response, job_details, matches):
        self.matches = matches
        self.publish_date = job_response['aktuelleVeroeffentlichungsdatum']
        self.refnr = job_response["refnr"]
        self.title = job_response.get("titel") or job_response.get("bezeichnung") or job_response.get("stellenbezeichnung")
        self.company = job_response.get("arbeitgeber") or job_response.get("firma")
        self.ort = self.convert_location(job_response.get("arbeitsort") or job_response.get("arbeitsorte"))
        self.url = job_response.get("externeURL") or job_details.get("externeURL")
        self.details = job_details['stellenangebotsBeschreibung']

    def convert_location(self, ort_data):
        return ort_data['ort']

    def get_title(self):
        return f"{self.title} – {self.company} – {self.ort}" 

    def dump_job_text(self):
        print(f"{self.refnr} – {self.publish_date}")
        print(self.get_title())
        if self.url is not None:
            print(self.url)
        print("")
        print(self.details)
        print(f"# Matches: {", ".join(self.matches)}")
        print("\n")


class JobSearcher:
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
        self,
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
        endpoint = f"{self.BASE_URL}/jobs"
        params = {
            "angebotsart": 1,
            "veroeffentlichtseit": 30,
            "arbeitszeit": "vz;tz",
            "zeitarbeit": False,
            "page": page,
            "size": size,
        }
        headers = {
            "X-API-Key": self.API_KEY,
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

    def get_job_details(self, refnr):
        base64_str = base64.b64encode(bytes(refnr, 'utf-8')).decode('utf-8')
        headers = {
            "X-API-Key": self.API_KEY,
            "Accept": "application/json",
        }
        response = requests.get(f"{self.JOB_DETAILS_URL}/{base64_str}", headers=headers, timeout=30)

        response.raise_for_status()
        return response.json()

    def build_job_from_response(self, job):
        details = self.get_job_details(job["refnr"])
        matching = [ word for word in self.KEYWORDS if word in details['stellenangebotsBeschreibung'].lower().split() ]
        if len(matching) > 0:
            job_object = Job(job, details, matching)
            return job_object
        return None

    def get_jobs(self, where: str | None = None, what: str | None = None):
        jobs_response = self.search_jobs(where=where, what=what, page=1, size=20)

        return ( job for job in 
            ( self.build_job_from_response(x) for x in jobs_response["stellenangebote"] )
            if job is not None )

    def run_job_search(self):
        return chain(self.get_jobs(where="Berlin"), self.get_jobs(where="Marburg"))

    def dump_jobs(self):
        for job in self.run_job_search():
            job.dump_job_text()

if __name__ == "__main__":
    JobSearcher().dump_jobs()
