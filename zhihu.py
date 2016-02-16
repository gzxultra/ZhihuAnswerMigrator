# -*- coding:utf-8 -*-
import sys
import http
import os
import time
import urllib
import random
import re
import codecs
from urllib import request
from bs4 import BeautifulSoup
# import html2text

'''
Zhihu spider
author: gzxultra
warning:
Before you run this script, please make sure that BeautifulSoup4 and Python3 were already installed.
'''

# please configure the collection you want to crawl.
# url = 'https://www.zhihu.com/collection/43668857'
url = 'https://www.zhihu.com/collection/68914551'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_DIR = os.path.join(BASE_DIR, '顾志翔的编程收藏夹')


class SpiderHTML(object):
    def getUrl(self, url, coding='utf-8'):
        req = request.Request(url)
        req.add_header(
            'User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36')
        with request.urlopen(req) as response:
            return BeautifulSoup(response.read().decode(coding))

    def save_text(self, filename, content, mode='w'):
        self._checkPath(filename)
        with codecs.open(filename, encoding='utf-8', mode=mode) as f:
            f.write(content)

    def save_image(self, imgUrl, imgName):
        data = request.urlopen(imgUrl).read()
        self._checkPath(imgName)
        with open(imgName, 'wb') as f:
            f.write(data)

    def _checkPath(self, path):
        dirname = os.path.dirname(path.strip())
        if not os.path.exists(dirname):
            os.makedirs(dirname)


class ZhihuSpider(SpiderHTML):
    def __init__(self, pageBegin, pageEnd, url):
        self._url = url
        self._pageBegin = int(pageBegin)
        self._pageEnd = int(pageEnd) + 1

    def run(self):
        for page in range(self._pageBegin, self._pageEnd):
            url = self._url + '?page=' + str(page)
            content = self.getUrl(url)
            # BeatifulSoup syntax
            question_list = content.find_all('div', class_='zm-item')
            for question in question_list:
                question_title_html = question.find(
                    'h2', class_='zm-item-title')
                if question_title_html is None:
                        # the question was deleted
                    continue

                # print("%r" % question_title_html)
                # example format:
                # <h2 class="zm-item-title"><a href="/question/27675151"
                # target="_blank">新手有什么入门级胶片机推荐吗？如何自学胶片风摄影？</a></h2>
                question_title = question_title_html.a.string
                # generate full url to questions
                question_full_url = 'https://www.zhihu.com' + \
                    question_title_html.a['href']
                # windows文件/目录名不支持的特殊符号
                question_title_html = re.sub(
                    r'[\\/:*?"<>]', '#', question_title_html.a.string)
                print('# acquiring questions:' + question_title_html + '#')
                question_content = self.getUrl(question_full_url)
                answer_list = question_content.find_all(
                    'div', class_='zm-item-answer  zm-item-expanded')
                self._processAnswer(
                    answer_list, question_title_html)
                # time.sleep(5)

    def _processAnswer(self, answer_list, question_title_html):
        anonymous_id = 0
        for answer in answer_list:
            anonymous_id = anonymous_id + 1

            upvoted = int(
                answer.find('span', class_='count').string.replace('K', '000'))
            if upvoted < 100:
                continue
            author_info = answer.find(
                'div', class_='zm-item-answer-author-info')
            author = {'introduction': '', 'link': ''}
            try:
                author['name'] = author_info.find(
                    'a', class_='author-link').string
                author['introduction'] = str(
                    author_info.find('span', class_='bio')['title'])
            except AttributeError:
                author['name'] = '匿名用户：' + str(anonymous_id)
            # no introduction
            except TypeError:
                pass

            try:
                author['link'] = author_info.find(
                    'a', class_='author-link')['href']
            except TypeError:
                pass

            # author info
            file_name = os.path.join(
                REPO_DIR, question_title_html, 'info', author['name'] + '_info.txt')
            if os.path.exists(file_name):
                continue
            self.save_text(
                file_name, '{introduction}\r\n{link}'.format(**author))

            # answer text only
            print('正在获取用户`{name}`的答案'.format(**author))
            answerContent = answer.find(
                'div', class_='zm-editable-content clearfix')
            if answerContent is None:
                continue
            else:
                self._getTextFromAnswer(
                    answerContent, question_title_html, **author)

            # answer image only
            imgs = answerContent.find_all('img')
            if len(imgs) == 0:
                pass
            else:
                self._getImgFromAnswer(imgs, question_title_html, **author)

    def _getImgFromAnswer(self, imgs, question_title_html, **author):
        i = 0
        for img in imgs:
            if 'inline-image' in img['class']:
                continue
            i = i + 1
            imgUrl = img['src']
            extension = os.path.splitext(imgUrl)[1]
            path_name = os.path.join(
                REPO_DIR, question_title_html, author['name'] + '_' + str(i) + extension)
            try:
                self.save_image(imgUrl, path_name)
            except ValueError:
                pass
            except urllib.error.HTTPError as e:
                pass
            except KeyError as e:
                pass
            except http.client.IncompleteRead:
                pass

    def _getTextFromAnswer(self, answerContent, question_title_html, **author):
        extension = '.txt'
        path_name = os.path.join(
            REPO_DIR, question_title_html, author['name'] + extension)
        tmp = answerContent.get_text()
        tmp2 = re.sub('<>', '', tmp)
        answer_text = tmp2.strip()
        # print(answer_text)
        try:
            self.save_text(path_name, answer_text)
        except ValueError:
            pass
        except urllib.error.HTTPError as e:
            pass
        except KeyError as e:
            pass
        except http.client.IncompleteRead:
            pass

if __name__ == '__main__':
    pageBegin, limit, paramsNum = 1, 0, len(sys.argv)
    print("%r" % sys.argv)

    # if params fully configured
    if paramsNum >= 3:
        pageBegin, pageEnd = sys.argv[1], sys.argv[2]
    # if only one param was given
    elif paramsNum == 2:
        pageBegin = sys.argv[1]
        pageEnd = pageBegin
        # default: only crawl the first page
    else:
        pageBegin, pageEnd = 1, 1

    spider = ZhihuSpider(pageBegin, pageEnd, url)
    spider.run()
    print("Mission Completed.")
