#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
from os import path
from md5 import md5
import sys
import os
import shutil
import urllib


# this dictionary contains name conversion mapping
name_mapping = {}

def load_html_file(filename):
    f = open(filename)
    lines = f.read()
    soup = BeautifulSoup(lines)
    return soup

def write_html_file(filename, soup):
    f = open(filename, "w")
    f.write(str(soup))
    f.close()


def get_relative_path_to(src, dst):
# the two lines below are used to make sure leading ./ are removed
    src = path.relpath(src)
    dst = path.relpath(dst)

    common_prefix = path.commonprefix([src, dst])
    if common_prefix.count(path.sep) > 0:
        common_prefix = common_prefix[:common_prefix.rindex(path.sep)+1]
    relative_to_src = path.relpath(src, common_prefix)
    #print '+++++++++++++++++++++++++++++++++++++++++'
    #print src
    #print dst
    #print common_prefix
    #print relative_to_src
    #print  "../"*relative_to_src.count(path.sep)+path.relpath(dst, common_prefix)
    #print '------------------------------------------'
    return "../"*relative_to_src.count(path.sep)+path.relpath(dst, common_prefix)

def link_conversion(page_url, soup):
    links = soup.findAll(name='a')
    absolute_url_prefix = 'http://cc.usst.edu.cn/'
    for link in links:
        if not link.has_key("href"):
            continue
        url = link["href"]
        if url.startswith('/'):
            url = url[1:]
            new_url = get_relative_path_to(page_url, url)
            link["href"] = get_name_for(new_url)
        elif url.startswith(absolute_url_prefix):
            print '======================================================='
            print url
            url = url[len(absolute_url_prefix):]
            print url
            print '======================================================='
            new_url = get_relative_path_to(page_url, url)
            link["href"] = get_name_for(new_url)
        else:
            link["href"] = get_name_for(url)

def img_conversion(page_url, soup):
    imgs = soup.findAll(name='img')
    for img in imgs:
        if not img.has_key("src"):
            continue
        url = img["src"]
        if url.startswith('/'):
            url = url[1:]
            new_url = get_relative_path_to(page_url, url)
            img["src"] = get_name_for(new_url)
        else:
            img["src"] = get_name_for(url)
        #img["src"] = img["src"].replace('?', '@')
        #print ' aaaaaaaaaaaaa                       '

def get_name_for(p, use_checksum_as_name = True):
    basename = path.basename(p)
    basename = basename.replace('@', '?') # this is a hack for windows, for the wget tool save ? in url as @ as file name
    ext = path
    if use_checksum_as_name:
        basename = get_checksum(basename)+'.'+get_ext_for(p)
    return path.join(path.dirname(p), basename)

def get_ext_for(p):
    if p.count(path.extsep) > 0:
        ext = p[p.rindex(path.extsep)+1:]
        if not ext.startswith('aspx'):
            return ext
    return 'html'

def get_checksum(data):
    m = md5()
    m.update(urllib.url2pathname(data))
    return m.hexdigest()

if __name__ == "__main__":
    out_dir = "../new/"
    for root, dirs, files in os.walk(sys.argv[1]):
        for d in dirs:
            new_dir = path.join(out_dir, root, d)
            if not path.exists(new_dir):
                os.mkdir(new_dir)
        for f in files:
            f = path.join(root, f)
            print "process " + f
            if 'html' == get_ext_for(f):
                soup = load_html_file(f)
                link_conversion(f, soup)
                img_conversion(f, soup)
                write_html_file(out_dir+get_name_for(f), soup)
            else:
                if 'css' == get_ext_for(f) \
                        or 'swf' == get_ext_for(f):
                    shutil.copy(f, out_dir+f)
                elif 'gif' == get_ext_for(f) \
                        or 'png' == get_ext_for(f) \
                        or 'jpg' == get_ext_for(f):
                    shutil.copy(f, out_dir+f)
                    shutil.copy(f, out_dir+get_name_for(f))
                else:
                    shutil.copy(f, out_dir+get_name_for(f))
        

