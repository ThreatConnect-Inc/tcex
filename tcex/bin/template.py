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
from tcex.input.field_types import Sensitive
from tcex.pleb.proxies import proxies

if TYPE_CHECKING:  # pragma: no cover
    # third-party
    from requests import Response


class Template(BinABC):
    """Install dependencies for App."""

    def __init__(
        self,
        proxy_host,
        proxy_port,
        proxy_user,
        proxy_pass,
    ):
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
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_user = proxy_user
        self.proxy_pass = proxy_pass

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
            yield from []
        else:
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

    def db_get_config(self, type_: str, template: str) -> Optional['TemplateConfigModel']:
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

    def db_get_sha(self, sha: str) -> Optional[str]:
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
        r: 'Response' = self.session.get(
            download_url, allow_redirects=True, headers={'Cache-Control': 'no-cache'}
        )
        if not r.ok:
            self.log.error(
                f'action=download-template-file, url={r.request.url}, '
                f'status_code={r.status_code}, headers={r.headers}, '
                f'response={r.text or r.reason}'
            )
            raise RuntimeError(
                f'action=get-template-config, url={r.request.url}, status_code='
                f'{r.status_code}, reason={r.reason}'
            )

        # get the relative path to the file and create the parent directory if it does not exist
        destination = item.get('relative_path')
        if destination.parent.exists() is False:
            destination.parent.mkdir(parents=True, exist_ok=True)
        destination.open(mode='wb').write(r.content)
        self.log.info(f'action=download-template-file, file={destination}')

        # update manifest, using the path as the key for uniqueness
        self.template_manifest[item.get('path')]['md5'] = self.file_hash(destination)

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
    ) -> Optional['TemplateConfigModel']:
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
            raise RuntimeError(
                f'action=get-template-config, url={r.request.url}, status_code='
                f'{r.status_code}, reason={r.reason}'
            )

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

    def get_template_contents(
        self,
        branch: str,
        data: dict,
        path: str,
        type_: str,
        app_builder: bool,
        template_name: str = None,  # preserve the template name for recursion
    ) -> dict:
        """Get the contents of a template and allow recursion."""
        for item in self.contents(branch, type_, path, app_builder):
            # add template name and type to the item to be
            # used during the download and write process
            item['template_name'] = template_name
            item['template_type'] = type_
            # add relative path key AFTER template values have been added to the item
            item['relative_path'] = self.item_relative_path(item)

            # process any files and recurse into any directories
            if item.get('type') == 'file':
                # templates are hierarchical, overwrite previous values with new
                # values using relative path for as the identifier for the file
                data[str(item.get('relative_path'))] = item

                # update manifest data, this will be used during
                # updates to determine if the file has changed
                self.template_manifest.setdefault(item.get('path'), {})
                self.template_manifest[item.get('path')]['sha'] = item.get('sha')
            elif item.get('type') == 'dir':
                nested_dir = f'''{path}/{item.get('name')}'''
                self.get_template_contents(
                    branch, data, nested_dir, type_, app_builder, template_name
                )

        return data

    def init(self, branch: str, type_: str, template: str, app_builder: bool) -> List[dict]:
        """Initialize an App with template files."""
        data = {}
        for tp in self.template_parents(type_, template, branch):
            self.get_template_contents(branch, data, tp, type_, app_builder, tp)
        return data.values()

    def item_relative_path(self, item: dict) -> Path:
        """Return the relative path to the item."""
        path = item.get('path')
        template_path = self.item_template_path(item)

        # handle nested files by stripping the type/template values from the path, the
        # remaining part is the relative path to the file to be used for read/write.
        _path = item.get('name')
        if path.startswith(template_path):
            _path = path.replace(template_path, '')
        return Path(_path)

    @staticmethod
    def item_template_path(item: dict) -> str:
        """Return the template path."""
        if item.get('template_name') == '_app_common':
            return f'''{item.get('template_name')}/'''
        return f'''{item.get('template_type')}/{item.get('template_name')}/'''

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
    def project_sha(self) -> Optional[str]:
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
            raise RuntimeError(
                f'action=get-template-config, url={r.request.url}, status_code='
                f'{r.status_code}, reason={r.reason}'
            )

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
        session.proxies = proxies(
            proxy_host=self.proxy_host,
            proxy_port=self.proxy_port,
            proxy_user=self.proxy_user,
            proxy_pass=Sensitive(self.proxy_pass),
        )

        # add auth if set (typically not require since default site is public)
        if self.username is not None and self.password is not None:
            session.auth = HTTPBasicAuth(self.username, self.password)

        return session

    @cached_property
    def template_manifest(self) -> dict:
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

    def template_parents(self, type_: str, template: str, branch: str = 'main') -> List[str]:
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

        # add this current template last
        app_templates.append(template)

        return app_templates

    @property
    def template_to_prefix_map(self) -> Dict[str, str]:
        """Return the defined template types."""
        return {
            'api_service': 'tcva',
            'feed_api_service': 'tcvf',
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
            'feed_api_service',
            'organization',
            'playbook',
            'trigger_service',
            # 'web_api_service',
            'webhook_trigger_service',
        ]

    def update(self, branch: str, template: str, type_: str, ignore_hash=False) -> List[dict]:
        """Initialize an App with template files."""
        # update tcex.json model
        if template is not None:
            self.tj.model.template_name = template
        if type_ is not None:
            self.tj.model.template_type = type_

        # retrieve ALL template contents
        data = {}
        for tp in self.template_parents(
            self.tj.model.template_type, self.tj.model.template_name, branch
        ):
            self.get_template_contents(branch, data, tp, self.tj.model.template_type, False, tp)

        # determine which files should be downloaded
        downloads = []
        for item in data.values():
            # get the relative path to the file
            relative_path = item.get('relative_path')

            # skip files if it has not changed
            if relative_path.is_file() and ignore_hash is False:
                # skip files if it has not changed
                if self.update_item_check_hash(relative_path, item) is False:
                    continue

            # is the file a template file and dev says overwrite
            if self.update_item_prompt(branch, item) and relative_path.is_file() is True:
                response = self.prompt_choice(
                    f'Overwrite: {relative_path}', choices=['y', 'n'], default='n'
                )
                if response == 'n':
                    continue

            downloads.append(item)
            self.template_manifest.setdefault(item.get('path'), {})
            self.template_manifest[item.get('path')]['sha'] = item.get('sha')

        return downloads

    def update_item_check_hash(self, fqfn: Path, item: dict) -> bool:
        """Check if the file hash has changed since init or last update."""
        file_hash = self.file_hash(fqfn)
        if self.template_manifest.get(item.get('path'), {}).get('md5') != file_hash:
            self.log.debug(
                f'''action=update-check-hash, template-file={item.get('name')}, '''
                'check=hash-check, result=hash-has-not-changed'
            )
            return True
        return False

    def update_item_prompt(self, branch: str, item: dict) -> bool:
        """Update the prompt value for the provided item."""
        template_name = item.get('template_name')
        template_config = self.get_template_config(
            self.tj.model.template_type, template_name, branch
        )

        # determine if file requires user prompt
        if str(item.get('relative_path')) in template_config.template_files:
            return False
        return True

    def update_tcex_json(self):
        """Update the tcex.json file."""
        self.tj.model.template_repo_hash = self.project_sha
        self.tj.write()
