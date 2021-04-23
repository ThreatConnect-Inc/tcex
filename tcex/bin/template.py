#!/usr/bin/env python
"""TcEx Dependencies Command"""
# standard library
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

# third-party
import colorama as c
import yaml
from pydantic import ValidationError
from requests import Session
from requests.auth import HTTPBasicAuth
from tinydb import Query, TinyDB

# first-party
from tcex.app_config.models import TemplateConfigModel
from tcex.backports import cached_property

from .bin import Bin


class Template(Bin):
    """Install dependencies for App."""

    def __init__(self):
        """Initialize class properties."""
        super().__init__()

        # properties
        self.errors = False
        self.template_configs = {}
        self.template_data = {}
        self.base_url = os.getenv(
            'TCEX_TEMPLATE_URL',
            'https://api.github.com/repos/ThreatConnect-Inc/tcex-app-templates',
        )
        self.base_raw_url = (
            'https://raw.githubusercontent.com/ThreatConnect-Inc/tcex-app-templates/master'
        )
        self.password = os.getenv('TCEX_TEMPLATE_PASSWORD')
        self.username = os.getenv('TCEX_TEMPLATE_USERNAME')

    @cached_property
    def cache_valid(self):
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

    def contents(self, type_: str, template: Optional[str] = None) -> dict:
        """Yield template contents."""
        url = f'{self.base_url}/contents/{type_}/{template}'
        if template is None:
            url = f'{self.base_url}/contents/{type_}'
        elif template == '_app_common':
            url = f'{self.base_url}/contents/{template}'

        r = self.session.get(url)
        if not r.ok:
            self.log.errors(f'Failed retrieving contents for type {url}.')
            self.errors = True

        for content in r.json():
            # exclusions - files that should not be part of the App
            if content.get('name') in ['.gitignore', 'template.yaml']:
                continue

            # rename gitignore to .gitignore
            if content.get('name') == 'gitignore':
                content['name'] = '.gitignore'

            yield content

    @cached_property
    def db(self) -> TinyDB:
        """Return db instance."""
        try:
            return TinyDB(os.path.join(self.cli_out_path, 'tcex.json'))
        except Exception:
            return None

    def db_add_config(self, config: TemplateConfigModel) -> None:
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

    def db_add_sha(self, sha: str) -> None:
        """Add a config to the DB."""
        SHA = Query()
        try:
            self.db.upsert({'sha': sha}, SHA.sha.exists())
        except Exception as ex:
            self.log.error(f'Failed inserting config in db ({ex}).')
            self.errors = True

    def db_get_config(self, type_: str, template: str) -> TemplateConfigModel:
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

    def db_get_sha(self, sha: str) -> None:
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

        r = self.session.get(
            download_url, allow_redirects=True, headers={'Cache-Control': 'no-cache'}
        )
        if not r.ok:
            self.log.errors(f'Could not download template file ({download_url}).')

        # write destination file
        destination.open(mode='wb').write(r.content)

    def get_template_config(self, type_: str, template: str) -> TemplateConfigModel:
        """Return the data from the template.yaml file."""
        self.log.info(
            f'action=get-template-config, type={type_}, '
            f'template={template}, cache-valid={self.cache_valid}'
        )
        if self.cache_valid is True:
            config = self.db_get_config(type_, template)
            if config is not None:
                return config

        url = f'{self.base_raw_url}/{type_}/{template}/template.yaml'
        if template == '_app_common':
            type_ = '_app_common'
            url = f'{self.base_raw_url}/_app_common/template.yaml'
        r = self.session.get(url)
        self.log.debug(f'action=get-template-config, url={url}, status-code={r.status_code}')
        if not r.ok:
            self.log.error(f'Failed retrieving template.yaml for project {type_} -> {template}.')
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

    def init(self, type_: str, template: str) -> List[dict]:
        """Initialize an App with template files."""
        downloads = {}
        for tp in self.template_parents(type_, template):
            for item in self.contents(type_, tp):
                if item.get('type') == 'file':
                    # overwrite name if found in later parent
                    downloads[item.get('name')] = item

        return downloads.values()

    def list(self, type_: Optional[str] = None) -> None:
        """List template types."""
        template_types = self.template_types
        if type_ is not None:
            if type_ not in self.template_types:
                raise ValueError(f'Invalid Types: {type_}')
            template_types = [type_]

        for selected_type in template_types:
            for td in self.contents(selected_type):
                if td.get('type') == 'dir':
                    template_config = self.get_template_config(selected_type, td.get('name'))
                    if template_config is not None:
                        self.template_data.setdefault(selected_type, [])
                        self.template_data[selected_type].append(template_config)

    def print_error_message(self):
        """Print error message, if applicable."""
        if self.errors is True:
            print(
                '''\n\nErrors encountered when running command. Please '''
                f'''see logs at {os.path.join(self.cli_out_path, 'tcex.log')}.'''
            )

    def print_list(self):
        """Print the list output."""
        for type_, templates in self.template_data.items():
            print(f'''{type_.replace('_', ' ').title()} Templates''')
            for config in templates:
                print(f'  Template Name: {config.name}')
                print(f'    Contributor: {config.contributor}')
                print(f'    Description: {config.description}')

    @cached_property
    def project_sha(self):
        """Return the current commit sha for the tcex-app-templates project."""
        params = {'perPage': '1'}
        r = self.session.get(f'{self.base_url}/commits', params=params)
        if not r.ok:
            err = r.text or r.reason
            self.log.error(f'Error trying to retrieve git commit ({err}).')
            self.errors = True
            return None

        try:
            commits_data = r.json()
        except Exception:
            return None

        # get current sha
        return commits_data[0].get('sha')

    @cached_property
    def session(self) -> Session:
        """Return session object"""
        session = Session()
        session.headers.update({'Cache-Control': 'no-cache'})

        # add auth if set (typically not require since default site is public)
        if self.username is not None and self.password is not None:
            session.auth = HTTPBasicAuth(self.username, self.password)

        return session

    def template_parents(self, type_: str, template: str) -> list:
        """Return all parents for the provided template."""
        # get the config for the requested template
        template_config = self.get_template_config(type_, template)

        # iterate over each parent template
        app_templates = []
        for parent in template_config.template_parents:
            parent_config = self.get_template_config(type_, parent)

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

    def update(self, template: str) -> List[dict]:
        """Initialize an App with template files."""
        template = template or self.tj.data.template_name
        type_ = self.tj.data.template_type

        # download template files
        downloads = {}
        for tp in self.template_parents(type_, template):
            template_config = self.get_template_config(type_, tp)
            for item in self.contents(type_, tp):
                name = item.get('name')
                if item.get('type') == 'file':
                    if name not in template_config.template_files and os.path.isfile(name):
                        if self.update_prompt(name) is True:
                            downloads[item.get('name')] = item
                    else:
                        downloads[item.get('name')] = item

        return downloads.values()

    def update_tcex_json(self) -> None:
        """Update the tcex.json file."""
        self.tj.data.template_repo_hash = self.project_sha
        self.tj.write()

    @staticmethod
    def update_prompt(name: str) -> bool:
        """Present the update prompt for the user."""
        overwrite = False
        print(f'''{c.Style.BRIGHT}{'File:'!s:<15}{c.Fore.CYAN}{name}''')
        message = (
            f'{c.Fore.MAGENTA}Replace ' f'{c.Style.BRIGHT}{c.Fore.WHITE}(y/[n]):{c.Fore.RESET} '
        )
        response: str = input(message).strip()  # nosec
        if response in ['y', 'yes']:
            overwrite = True

        return overwrite
