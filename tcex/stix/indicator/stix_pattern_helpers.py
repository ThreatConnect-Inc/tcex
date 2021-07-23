"""Several helper functions that produce a STIX pattern for a threatconnect indicator."""
# standard library
import ipaddress


def address_stix_pattern_producer(data):
    """Convert an address from TC to a STIX pattern."""
    if isinstance(ipaddress.ip_address(data.get('summary')), ipaddress.IPv6Address):
        return f"[ipv6-addr:value = '{data.get('summary')}']"

    return f"[ipv4-addr:value = '{data.get('summary')}']"


def cidr_stix_pattern_producer(data):
    """Convert a CIDR from TC to a STIX pattern."""
    if isinstance(ipaddress.ip_network(data.get('summary'), strict=False), ipaddress.IPv6Network):
        return f"[ipv6-addr:value = '{data.get('summary')}']"

    return f"[ipv4-addr:value = '{data.get('summary')}']"


def file_stix_pattern_producer(data):
    """Convert a File from TC to a STIX pattern."""
    expressions = []
    for _hash in data.get('summary', '').split(' : '):
        if len(_hash) == 32:
            expressions.append(f"file:hashes.md5 = '{_hash}'")
        elif len(_hash) == 40:
            expressions.append(f"file:hashes.sha1 = '{_hash}'")
        elif len(_hash) == 64:
            expressions.append(f"file:hashes.sha256 = '{_hash}'")

    return f'[{" OR ".join(expressions)}]'


def asn_stix_pattern_producer(data):
    """Convert an ASN from TC to a STIX pattern."""
    return f"[autonomous-system:name = '{data.get('summary')}']"


def email_address_stix_pattern_producer(data):
    """Convert an email address from TC to a STIX pattern."""
    return f"[email-addr:value = '{data.get('summary')}']"


def url_stix_pattern_producer(data):
    """Convert a URL from TC to a STIX pattern."""
    return f"[url:value = '{data.get('summary')}']"


def host_stix_pattern_producer(data):
    """Convert a host from TC to a STIX pattern."""
    return f"[domain-name:value = '{data.get('summary')}']"


def email_subject_stix_pattern_producer(data):
    """Convert a host from TC to a STIX pattern."""
    return f"[email-message:subject = '{data.get('summary')}']"


def registery_key_stix_pattern_producer(data):
    """Convert a Registry Key from TC to a STIX pattern."""
    key_name, value_name, value_type = data.get('summary').split(':')

    parts = []

    if key_name.strip():
        key_name = key_name.strip().replace('\\', '/')
        parts.append(f"windows-registry-key:key = '{key_name.strip()}'")

    if value_name.strip():
        parts.append(f"windows-registry-key:values.name = '{value_name.strip()}'")

    if value_type.strip():
        parts.append(f"windows-registry-key:values.data_type = '{value_type.strip()}'")

    return f'[{" AND ".join(parts)}]'
