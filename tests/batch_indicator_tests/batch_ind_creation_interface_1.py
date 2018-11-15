#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def address_create(batch_job):
    address = batch_job.address('123.124.125.126', '5.0', '100')
    address.attribute('Description', 'Example Description', True)
    address.tag('Example Tag')
    address.security_label('TLP Green')


def email_address_create(batch_job):
    email_address = batch_job.email_address('bad@dfadsfaddsfa.com', '5.0', '100')
    email_address.attribute('Description', 'Example Description', True)
    email_address.tag('Example Tag')
    email_address.security_label('TLP Green')


def file_create(batch_job):
    file = batch_job.file(md5='a'*32, sha1='b'*40, sha256='c'*64, rating='5.0', confidence='100')
    file.attribute('Description', 'Example Description', True)
    file.tag('Example Tag')
    file.security_label('TLP Green')


def host_create(batch_job):
    host = batch_job.host('dfadsfaddsfa.com', rating='5.0', confidence='100')
    host.attribute('Description', 'Example Description', True)
    host.tag('Example Tag')
    host.security_label('TLP Green')


def url_create(batch_job):
    url = batch_job.url('https://dfadsfaddsfa.com/index.html', '5.0', '100')
    url.attribute('Description', 'Example Description', True)
    url.tag('Example Tag')
    url.security_label('TLP Green')
