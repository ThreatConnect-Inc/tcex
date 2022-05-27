#!/usr/bin/env python
"""TcEx Dependencies Command"""
# standard library
import hashlib
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

# third-party
import yaml
from pydantic import ValidationError
from requests import Session
from requests.auth import HTTPBasicAuth
from tinydb import Query, TinyDB

# first-party
from tcex.app_config.models import TemplateConfigModel
from tcex.backports import cached_property
from tcex.bin.bin_abc import BinABC

if TYPE_CHECKING:  # pragma: no cover
    # third-party
    from requests import Response


class Template(BinABC):
    """Install dependencies for App."""

    def __init__(self):
        """Initialize class properties."""
        super().__init__()

        # properties
        self.base_url = os.getenv(
            'TCEX_TEMPLATE_URL',
            'https://api.github.com/repos/ThreatConnect-Inc/tcex-app-templates',
        )
        self.base_raw_url = 'https://raw.githubusercontent.com/ThreatConnect-Inc/tcex-app-templates'
        self.errors = False
        self.password = os.getenv('GITHUB_PAT')
        self.template_configs = {}
        self.template_data = {}
        self.template_manifest_fqfn = Path('.template_manifest.json')
        self.username = os.getenv('GITHUB_USER')

    @cached_property
    def cache_valid(self) -> bool:
        """Return the current commit sha for the tcex-app-templates project."""
        if self.project_sha is None:
            return False

        # get the store sha
        stored_sha = self.db_get_sha(self.project_sha)

        # if sha values don't match upsert and return False
        if stored_sha != self.project_sha:
            # upsert current sha
            self.db_add_sha(self.project_sha)
            return False

        # cache is valid
        return True

    def contents(
        self,
        branch: str,
        type_: str,
        template: Optional[str] = None,
        app_builder: Optional[bool] = False,
    ) -> dict:
        """Yield template contents."""
        url = f'{self.base_url}/contents/{type_}/{template}'
        if template is None:
            url = f'{self.base_url}/contents/{type_}'
        elif template == '_app_common':
            url = f'{self.base_url}/contents/{template}'

        params = {'ref': branch}
        r: 'Response' = self.session.get(url, params=params)
        if not r.ok:
            self.log.error(
                f'action=get-contents, url={r.request.url}, '
                f'status_code={r.status_code}, headers={r.headers}, '
                f'response={r.text or r.reason}'
            )
            self.errors = True

        for content in r.json():
            # exclusion - this file is only needed for building App Builder templates
            if content.get('name') == '.appbuilderconfig' and app_builder is False:
                continue

            # exclusions - files that should not be part of the App
            if content.get('name') in ['.gitignore', 'template.yaml']:
                continue

            # rename gitignore to .gitignore
            if content.get('name') == 'gitignore':
                content['name'] = '.gitignore'

            yield content

    @cached_property
    def db(self) -> 'TinyDB':
        """Return db instance."""
        try:
            return TinyDB(os.path.join(self.cli_out_path, 'tcex.json'))
        except Exception:
            return None

    def db_add_config(self, config: TemplateConfigModel):
        """Add a config to the DB."""
        Config = Query()
        try:
            if config.name == '_app_common':
                config.type = '_app_common'
            self.db.upsert(
                json.loads(config.json()),
                (Config.type == config.type) & (Config.name == config.name),
            )
        except Exception as ex:
            self.log.error(f'Failed inserting config in db ({ex}).')
            self.errors = True

    def db_add_sha(self, sha: str):
        """Add a config to the DB."""
        SHA = Query()
        try:
            self.db.upsert({'sha': sha}, SHA.sha.exists())
        except Exception as ex:
            self.log.error(f'Failed inserting config in db ({ex}).')
            self.errors = True

    def db_get_config(self, type_: str, template: str) -> 'TemplateConfigModel':
        """Get a config from the DB."""
        Config = Query()
        try:
            if template == '_app_common':
                type_ = '_app_common'
            config = self.db.search((Config.type == type_) & (Config.name == template))

            if config:
                return TemplateConfigModel(**config[0])
            return None
        except Exception as ex:
            self.log.error(f'Failed retrieving config from db ({ex}).')
            self.errors = True
            return None

    def db_get_sha(self, sha: str):
        """Get repo SHA from the DB."""
        SHA = Query()
        try:
            sha = self.db.search(SHA.sha == sha)
            if sha:
                return sha[0].get('sha')
            return None
        except Exception as ex:
            self.log.error(f'Failed inserting config in db ({ex}).')
            self.errors = True
            return None

    def download_template_file(self, item: dict):
        """Download the provided source file to the provided destination."""
        download_url = item.get('download_url')
        name = item.get('name')

        # where to write the file
        destination = Path(os.path.join(os.getcwd(), name))
        self.log.info(f'action=download-template-file, file={name}')

        r: 'Response' = self.session.get(
            download_url, allow_redirects=True, headers={'Cache-Control': 'no-cache'}
        )
        if not r.ok:
            self.log.error(
                f'action=download-template-file, url={r.request.url}, '
                f'status_code={r.status_code}, headers={r.headers}, '
                f'response={r.text or r.reason}'
            )

        # write destination file
        destination.open(mode='wb').write(r.content)

        # update manifest
        self.template_manifest[name]['md5'] = self.file_hash(destination)

    @staticmethod
    def file_hash(fqfn: Path) -> str:
        """Return the file hash."""
        with fqfn.open(mode='rb') as fh:
            md5 = hashlib.md5()  # nosec
            while True:
                chunk = fh.read(8192)
                if not chunk:
                    break
                md5.update(chunk)

        return md5.hexdigest()

    def get_template_config(
        self, type_: str, template: str, branch: str = 'main'
    ) -> 'TemplateConfigModel':
        """Return the data from the template.yaml file."""
        self.log.info(
            f'action=get-template-config, type={type_}, '
            f'template={template}, cache-valid={self.cache_valid}, branch={branch}'
        )
        if self.cache_valid is True:
            config = self.db_get_config(type_, template)
            if config is not None:
                return config

        url = f'{self.base_raw_url}/{branch}/{type_}/{template}/template.yaml'
        if template == '_app_common':
            type_ = '_app_common'
            url = f'{self.base_raw_url}/{branch}/_app_common/template.yaml'

        params = {}
        if branch:
            params['ref'] = branch
        r: 'Response' = self.session.get(url)
        self.log.debug(f'action=get-template-config, url={url}, status-code={r.status_code}')
        if not r.ok:
            self.log.error(
                f'action=get-template-config, url={r.request.url}, '
                f'status_code={r.status_code}, headers={r.headers}, '
                f'response={r.text or r.reason}'
            )
            self.errors = True
            return None

        try:
            template_config_data = yaml.safe_load(r.text)
            template_config_data.update({'name': template, 'type': type_})
            config = TemplateConfigModel(**template_config_data)

            # upsert db
            self.db_add_config(config)
            self.log.debug(f'action=get-template-config, config={config}')
            return config
        except ValidationError as ex:
            for error in json.loads(ex.json()):
                location = [str(location) for location in error.get('loc')]
                self.log.error(
                    '''Schema validation failed for template.yaml. '''
                    f'''({error.get('msg')}: {' -> '.join(location)})'''
                )
                self.errors = True
            return None

    def init(self, branch: str, type_: str, template: str, app_builder: bool) -> List[dict]:
        """Initialize an App with template files."""
        downloads = {}
        for tp in self.template_parents(type_, template, branch):
            for item in self.contents(branch, type_, tp, app_builder):
                if item.get('type') == 'file':
                    # overwrite name if found in later parent
                    downloads[item.get('name')] = item
                    self.template_manifest.setdefault(item.get('name'), {})
                    self.template_manifest[item.get('name')]['sha'] = item.get('sha')

        return downloads.values()

    def list(self, branch: str, type_: Optional[str] = None):
        """List template types."""
        template_types = self.template_types
        if type_ is not None:
            if type_ not in self.template_types:
                raise ValueError(f'Invalid Types: {type_}')
            template_types = [type_]

        for selected_type in template_types:
            for td in self.contents(branch, selected_type):
                if td.get('type') == 'dir':
                    template_config = self.get_template_config(
                        selected_type, td.get('name'), branch
                    )
                    if template_config is not None:
                        self.template_data.setdefault(selected_type, [])
                        self.template_data[selected_type].append(template_config)

    def print_error_message(self):
        """Print error message, if applicable."""
        if self.errors is True:
            print(
                '''\n\nErrors were encountered during command execution. Please '''
                f'''see logs at {os.path.join(self.cli_out_path, 'tcex.log')}.'''
            )

    def print_list(self, branch: Optional[str] = None):
        """Print the list output."""
        for type_, templates in self.template_data.items():
            self.print_title(f'''{type_.replace('_', ' ').title()} Templates''')
            for config in templates:
                self.print_setting('Template', config.name, fg_color='green', bold=False)
                self.print_setting('Contributor', config.contributor, fg_color='green', bold=False)
                self.print_setting('Summary', config.summary, fg_color='green', bold=False)
                install_cmd = f'tcex init --type {type_} --template {config.name}'
                if branch != 'main':
                    install_cmd += f' --branch {branch}'
                self.print_setting(
                    'Install Command',
                    install_cmd,
                    fg_color='white',
                    bold=False,
                )
                # looks cleaner just to have a blank line
                # self.print_divider()
                print('')

    @cached_property
    def project_sha(self) -> str:
        """Return the current commit sha for the tcex-app-templates project."""
        params = {'perPage': '1'}
        r: 'Response' = self.session.get(f'{self.base_url}/commits', params=params)
        if not r.ok:
            self.log.error(
                f'action=get-project-sha, url={r.request.url}, '
                f'status_code={r.status_code}, headers={r.headers}, '
                f'response={r.text or r.reason}'
            )
            self.errors = True
            return None

        try:
            commits_data = r.json()
        except Exception:
            return None

        # get current sha
        return commits_data[0].get('sha')

    @cached_property
    def session(self) -> 'Session':
        """Return session object"""
        session = Session()
        session.headers.update({'Cache-Control': 'no-cache'})

        # add auth if set (typically not require since default site is public)
        if self.username is not None and self.password is not None:
            session.auth = HTTPBasicAuth(self.username, self.password)

        return session

    @cached_property
    def template_manifest(self):
        """Write the template manifest file."""
        if self.template_manifest_fqfn.is_file():
            with self.template_manifest_fqfn.open() as fh:
                return json.load(fh)
        return {}

    def template_manifest_write(self):
        """Write the template manifest file."""
        with self.template_manifest_fqfn.open(mode='w') as fh:
            fh.write(json.dumps(self.template_manifest, indent=2, sort_keys=True))
            fh.write('\n')

    def template_parents(self, type_: str, template: str, branch: str = 'main') -> list:
        """Return all parents for the provided template."""
        # get the config for the requested template
        template_config = self.get_template_config(type_, template, branch)

        # fail if template config can't be found
        if template_config is None:
            self.print_failure(
                f'Failed retrieving template.yaml: type={type_}, template={template}.\n'
                'Try running "tcex list" to get valid template types and names.'
            )

        # iterate over each parent template
        app_templates = []
        for parent in template_config.template_parents:
            parent_config = self.get_template_config(type_, parent, branch)

            # update templates
            app_templates.extend(
                [t for t in parent_config.template_parents if t not in app_templates]
            )

        # add parent after parent->parents have been added
        app_templates.extend(
            [t for t in template_config.template_parents if t not in app_templates]
        )

        # add this template last
        app_templates.extend([template])

        return app_templates

    @property
    def template_to_prefix_map(self) -> Dict[str, str]:
        """Return the defined template types."""
        return {
            'api_service': 'tcva',
            'organization': 'tc',
            'playbook': 'tcpb',
            'trigger_service': 'tcvc',
            'web_api_service': 'tcvp',
            'webhook_trigger_service': 'tcvw',
        }

    @property
    def template_types(self) -> List[str]:
        """Return the defined template types."""
        return [
            'api_service',
            'external',
            'organization',
            'playbook',
            'trigger_service',
            # 'web_api_service',
            'webhook_trigger_service',
        ]

    def update(self, branch: str, template: str, type_: str, ignore_hash=False) -> List[dict]:
        """Initialize an App with template files."""
        if template is not None:
            self.tj.model.template_name = template
        if type_ is not None:
            self.tj.model.template_type = type_

        template = template or self.tj.model.template_name
        type_ = type_ or self.tj.model.template_type

        # get the final contents after procession all parents
        contents = {}
        for tp in self.template_parents(
            self.tj.model.template_type, self.tj.model.template_name, branch
        ):
            template_config = self.get_template_config(self.tj.model.template_type, tp, branch)
            for item in self.contents(branch, self.tj.model.template_type, tp):
                if item.get('type') == 'file':
                    # determine if file requires user prompt
                    prompt = True
                    if item.get('name') in template_config.template_files:
                        prompt = False
                    item['prompt'] = prompt

                    # overwrite name if found in later parent
                    contents[item.get('name')] = item

        # determine which files should be downloaded
        downloads = []
        for item in contents.values():
            fqfn = Path(item.get('name'))
            name = item.get('name')

            if fqfn.is_file():
                file_hash = self.file_hash(fqfn)
            else:
                continue

            # has the file hash changed since init or last update
            if not ignore_hash and self.template_manifest.get(name, {}).get('md5') == file_hash:
                self.log.debug(
                    f'action=update, template-file={name}, '
                    'check=hash-check, result=hash-has-not-changed'
                )
                continue

            # # has the repo sha changed since init or last update
            # if self.template_manifest.get(name, {}).get('sha') == item.get('sha'):
            #     self.log.debug(
            #         f'action=update, template-file={name}, '
            #         'check=sha-check, result=sha-has-not-changed'
            #     )
            #     continue

            # is the file a template file and dev says overwrite
            if item.get('prompt') is True and os.path.isfile(name):
                response = self.prompt_choice(f'Overwrite: {name}', choices=['y', 'n'], default='n')
                if response == 'n':
                    continue

            downloads.append(item)
            self.template_manifest.setdefault(item.get('name'), {})
            self.template_manifest[item.get('name')]['sha'] = item.get('sha')

        return downloads

    def update_tcex_json(self):
        """Update the tcex.json file."""
        self.tj.model.template_repo_hash = self.project_sha
        self.tj.write()
