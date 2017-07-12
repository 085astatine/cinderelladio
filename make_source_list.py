#!/usr/bin/python
# -*- coding: utf-8 -*-


import logging
import re
import urllib.parse
from collections import OrderedDict
import requests
import lxml.html
import yaml


class WebPage(object):
    def __init__(self, url):
        self.url = url
        self.response = requests.get(url)
        self.html = lxml.html.fromstring(self.response.content)


def represent_ordered_dict(dumper, instance):
    return dumper.represent_mapping('tag:yaml.org,2002:map', instance.items())


if __name__ == '__main__':
    # logger
    logger = logging.getLogger('make_source_list')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.formatter = logging.Formatter(
                fmt='%(asctime)s %(name)s::%(levelname)s: %(message)s')
    logger.addHandler(handler)
    logger.info('Cinderelladio MakeSourceList')
    # yaml
    yaml.add_representer(OrderedDict, represent_ordered_dict)
    # source
    source_url = (r'http://dic.nicomoba.jp/a/'
                  + urllib.parse.quote('杏・輝子・小梅のシンデレラジオ'))
    logger.info("request '{0}'".format(source_url))
    source_page = WebPage(source_url)
    # main episode
    main_episode_list = []
    main_episode_xpath = (
                r'//h3[text()="本編"]/'
                r'following-sibling::*'
                r'[following-sibling::h3[text()="外伝作品"]]'
                r'//table')
    main_episode_table = source_page.html.xpath(main_episode_xpath)[0]
    for i, row in enumerate(main_episode_table.xpath('tbody/tr[td]'), start=1):
        logger.info('episode: {0:3d}'.format(i))
        column_list = row.xpath('td')
        date = ''.join(column_list[1].itertext())
        logger.info('  date: {0}'.format(date))
        title = re.match(
                    r'.+「[^」]+」',
                    ''.join(column_list[2].itertext()).split('\n')[0]).group()
        logger.info('  title: {0}'.format(title))
        url = None
        for url_data in column_list[2].xpath('.//a[@href]'):
            if url_data.text != 'pixiv（修正版）':
                continue
            url = url_data.get('href')
        logger.info('  url: {0}'.format(url))
        guest_list = [guest.strip()
                      for line in column_list[3].xpath('p')
                      for guest in ''.join(line.itertext()).split('\n')]
        logger.info('  guest: {0}'.format(', '.join(guest_list)))
        episode = OrderedDict()
        episode['number'] = i
        episode['title'] = title
        episode['url'] = url
        episode['guest'] = guest_list
        main_episode_list.append(episode)
    # side episode
    side_episode_list = []
    side_episode_xpath_list = [
                r'//h3[text()="外伝作品"]/'
                r'following-sibling::*'
                r'[following-sibling::h3[text()="だらだらふわぁず"]]'
                r'//table',
                r'//h3[text()="だらだらふわぁず"]/'
                r'following-sibling::table'
                r'[following-sibling::h3[text()="IFストーリー"]]']
    for side_episode_table in map(source_page.html.xpath,
                                  side_episode_xpath_list):
        for row in side_episode_table[0].xpath('tbody/tr[td]'):
            logger.info('side spisode:')
            column_list = row.xpath('td')
            date = ''.join(column_list[0].itertext())
            logger.info('  date: {0}'.format(date))
            title = ''.join(column_list[1].itertext()).split('\n')[0]
            logger.info('  title: {0}'.format(title))
            for url_data in column_list[1].xpath('.//a[@href]'):
                if url_data.text != 'pixiv（修正版）':
                    continue
                url = url_data.get('href')
            logger.info('  url: {0}'.format(url))
            episode = OrderedDict()
            episode['title'] = title
            episode['url'] = url
            side_episode_list.append(episode)
    # result
    result = OrderedDict()
    result['main'] = main_episode_list
    result['side'] = side_episode_list
    print(yaml.dump(result,
                    allow_unicode=True,
                    default_flow_style=False))
