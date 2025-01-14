import click
import requests
import os


class GithubClient():
    PROXY_ENDPOINT = os.environ.get("PROXY_ENDPOINT")

    def __init__(self, token):
        self.headers = {"Authorization": f"Bearer {token}",
                        "Accept": "application/vnd.github+json"}

    def get_proxy_runs_list(self, proxy_branch):
        response = requests.get(
            f"{self.PROXY_ENDPOINT}/actions/workflows/pipeline.yml/runs?branch={proxy_branch}", headers=self.headers)
        if response.status_code != 200:
            raise RuntimeError(f"Can't get proxy runs list. Error: {response.json()}")
        runs = [item['id'] for item in response.json()['workflow_runs']]
        return runs

    def get_proxy_runs_count(self, proxy_branch):
        response = requests.get(
            f"{self.PROXY_ENDPOINT}/actions/workflows/pipeline.yml/runs?branch={proxy_branch}", headers=self.headers)
        return int(response.json()["total_count"])

    def run_proxy_dispatches(self, proxy_branch, github_ref, github_sha, test_set, initial_pr):
        data = {"ref": proxy_branch,
                "inputs": {"test_set": test_set,
                           "neon_evm_commit": github_sha,
                           "neon_evm_branch": github_ref,
                           "initial_pr": initial_pr}
                }
        response = requests.post(
            f"{self.PROXY_ENDPOINT}/actions/workflows/pipeline.yml/dispatches", json=data, headers=self.headers)
        click.echo(f"Sent data: {data}")
        click.echo(f"Status code: {response.status_code}")
        if response.status_code != 204:
            raise RuntimeError("proxy-model.py action is not triggered")

    def get_proxy_branches(self):
        proxy_branches_obj = requests.get(
            f"{self.PROXY_ENDPOINT}/branches?per_page=100").json()
        return [item["name"] for item in proxy_branches_obj]

    def get_proxy_run_info(self, id):
        response = requests.get(
            f"{self.PROXY_ENDPOINT}/actions/runs/{id}", headers=self.headers)
        return response.json()
