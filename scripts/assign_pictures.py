# coding=utf-8
"""
Add pictures selected by path to given series.

Note: Set PYTHONPATH to include picdb if picdb is not installed yet!
"""
# Copyright (c) 2016 Stefan Braun
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and
# associated documentation files (the "Software"), to deal in the Software
# without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to
# whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE
# AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
#  LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
from pprint import pprint
import argparse

import group
import picture
import tag
from picdb import persistence

from picdb.picture import Picture
from picdb.group import Group
from picdb.tag import Tag
from picdb.persistence import UnknownEntityException


def main(argv):
    args = _parse_arguments(argv)
    if args.verbose:
        print('Namespace: {}'.format(args))
    try:
        series = _get_series(args.groups)
        tags = _get_tags(args.tag)
        pics = get_pic_list(args.path)
        if args.verbose:
            print('Series: {}'.format(series))
            print('Tags: {}'.format(tags))
            _show_selected_pictures(pics, args.verbose)
    except UnknownEntityException as e:
        print('>>> Error: {}'.format(e))
    else:
        if not args.dry_run:
            add_assignments(pics, series, tags)
            print('{} pictures processed.'.format(len(pics)))


def add_assignments(pics: [Picture],
                    series: [Group],
                    tags: [Tag]):
    for pic in pics:
        for s in series:
            if s not in pic.groups: group.add_picture_to_series(pic, s)
        for t in tags:
            if t not in pic.tags: picture.add_tag_to_picture(pic, t)


def get_pic_list(path: str):
    """Retrieve requested pictures.

    :param path: path name of pictures with optional wildcards.
    :type path: [str]
    :return: list of pictures
    :rtype: [Picture]
    """
    return picture.retrieve_filtered_pictures(path, None, [], [])


def _get_series(names: [str]):
    """Retrieve requested series.

    :param names: list of series names.
    :type names: [str]
    :return: list of series
    :rtype: [Group]
    """
    series_ = []
    for name in names:
        series = group.retrieve_series_by_name(name)
        series_.append(series)
    return series_


def _get_tags(names: [str]):
    """Retrieve requested tags.

    :param names: list of tag names.
    :type names: [str]
    :return: list of tags
    :rtype: [Tag]
    """
    tags = []
    for name in names:
        tag = tag.retrieve_tag_by_name(name)
        tags.append(tag)
    return tags


def _show_selected_pictures(pics, verbose):
    print('{} pictures selected.'.format(len(pics)))
    if verbose:
        print('Selected Pictures:')
        print('-' * 80)
        pprint(pics)
        print('-' * 80)


def _parse_arguments(args):
    parser = argparse.ArgumentParser(
        description='Assign pictures given by path expression to given '
                    'series and tags.')
    parser.add_argument('path', action='store',
                        help='Path of pictures as an SQL like expression '
                             'using %% as wildcard.')
    parser.add_argument('-s', '--series', action='append', dest='series',
                        default=[],
                        help='Name of series. Multiple use allowed.')
    parser.add_argument('-t', '--tag', action='append', dest='tag',
                        default=[],
                        help='Name of tag. Multiple use allowed.')
    parser.add_argument('-d', '--dry_run', action='store_true', dest='dry_run',
                        default=False,
                        help='Dry run. Do not write to database. Just list '
                             'selected pictures.')
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',
                        default=False,
                        help='Be verbose.')
    arguments = parser.parse_args(args)
    return arguments


if __name__ == '__main__':
    main(sys.argv[1:])
