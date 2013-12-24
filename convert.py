#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "1.1.1"

from BeautifulSoup import BeautifulSoup
from os import path
from md5 import md5
import sys
import os
import shutil
import urllib


# this dictionary contains name conversion mapping
name_mapping = {}

shortest_filename = ""
def create_index_html(root_dir, redir_page):
    print "create index.html, redirect to " + redir_page
    redir_page = get_relative_path_to("index.html", redir_page)
    redir_page = get_name_for(redir_page).replace(path.sep, '/')
    filename = path.join(root_dir, "index.html")
    f = open(filename, "w")
    index_content = '''<html>
<head>
<script>
function onload()
{
  window.location.assign("%s");
}
</script>
</head>
<body onload="onload()">
</body>
</html>'''
    index_content = index_content%(redir_page)
    f.write(index_content)
    f.close()


def load_html_file(filename):
    f = open(filename)
    lines = f.read()
    soup = BeautifulSoup(lines)
    return soup

def write_html_file(filename, soup):
    f = open(filename, "w")
    f.write(str(soup))
    f.close()


def get_relative_path_to(src, dst, change_sep_to_unix_type=False):
# the two lines below are used to make sure leading ./ are removed
    src = path.relpath(src)
    dst = path.relpath(dst)
    if change_sep_to_unix_type:
        src = src.replace(path.sep, '/').lower()
        dst = dst.replace(path.sep, '/').lower()

    common_prefix = path.commonprefix([src, dst])
    if common_prefix.count(path.sep) > 0:
        common_prefix = common_prefix[:common_prefix.rindex(path.sep)+1]
    relative_to_src = path.relpath(src, common_prefix)
    result = "../"*relative_to_src.count(path.sep)+path.relpath(dst, common_prefix)
    result = result.replace(path.sep, '/')
    return result

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
            url = url[len(absolute_url_prefix):]
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

def video_conversion(page_url, soup):
    embeds = soup.findAll(name='embed')
    for ebd in embeds:
        if not ebd.has_key("src"):
            continue
        url = ebd["src"]

        url = url.replace(path.sep, '/')

        absolute_url_prefix = 'http://cc.usst.edu.cn:80/'
        if url.startswith(absolute_url_prefix):
            url = url[len(absolute_url_prefix):]
        if url.startswith('/'):
            url = url[1:]
        new_url = get_relative_path_to(page_url, url, True)
        ebd["src"] = new_url
        if new_url.count("flv") > 0:
            if not ebd.has_key("flashvars"):
                continue
            video_url = ebd['flashvars']
            begin_tag = 'file='
            end_tag = '&'
            begin_index = video_url.index(begin_tag)
            end_index = video_url.index(end_tag)
            string_after = video_url[end_index:]
            video_url = video_url[begin_index+len(begin_tag):end_index]
            ebd['flashvars'] = begin_tag+convert_video_url(new_url, video_url)+string_after

def convert_video_url(flash_plugin_url, video_url):
    absolute_url_prefix = 'http://cc.usst.edu.cn:80/'
    video_url = video_url[len(absolute_url_prefix):]
    new_url = get_relative_path_to(flash_plugin_url, video_url)
    return new_url

def get_name_for(p, use_checksum_as_name = True):
    basename = path.basename(p)
    basename = basename.replace('@', '?') # this is a hack for windows, for the wget tool save ? in url as @ file name
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
    print "convert.py version: " + __version__
    out_dir = "../new/"
    in_dir = './'
    if len(sys.argv) > 1:
        in_dir = sys.argv[1]
    if not path.exists(out_dir):
        shutil.os.mkdir(out_dir)
    if not path.isdir(out_dir):
        print out_dir + ' is not a directory'
        sys.exit(1)

    for root, dirs, files in os.walk(in_dir):
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
                video_conversion(f, soup)
                write_html_file(out_dir+get_name_for(f), soup)
                if (len(shortest_filename) < 1 or len(shortest_filename) > f) and f.lower().count("view.aspx") > 0:
                    shortest_filename = f
            else:
                if 'css' == get_ext_for(f):
                    shutil.copy(f, out_dir+f)
                elif 'gif' == get_ext_for(f) \
                        or 'swf' == get_ext_for(f) \
                        or 'png' == get_ext_for(f) \
                        or 'jpg' == get_ext_for(f):
                    shutil.copy(f, out_dir+f) # copy the image with intact name and hashed name 
                    shutil.copy(f, out_dir+get_name_for(f))
                else:
                    shutil.copy(f, out_dir+get_name_for(f))

    if len(shortest_filename) > 1:
        create_index_html(out_dir, shortest_filename)
