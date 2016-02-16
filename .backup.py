'''
            try:
                author['link'] = author_info.find(
                    'a', class_='author-link')['href']
            except TypeError:
                pass

            file_name = os.path.join(
                REPO_DIR, question_title_html, 'info', author['name'] + '_info.txt')
            if os.path.exists(file_name):
                continue

            self.save_text(
                file_name, '{introduction}\r\n{link}'.format(**author))  # 保存作者的信息
            print('正在获取用户`{name}`的答案'.format(**author))
            answerContent = answer.find(
                'div', class_='zm-editable-content clearfix')
            if answerContent is None:
                continue
            else:
                self._getTextFromAnswer(
                    answerContent, question_title_html, **author)

            imgs = answerContent.find_all('img')
            if len(imgs) == 0:  # 答案没有上图
                pass
            else:
                self._getImgFromAnswer(imgs, question_title_html, **author)
'''


    def _convertToMarkdown(self, answer):
        h = html2text.HTML2Text()
        h.ignore_links = True
        print(h.handle(answer))
        path_name = os.path.join(
            REPO_DIR, question_title_html, author['name'] + '.markdown')
        # answer_output = re.sub('<>', '', p.get_markdown())
        try:
            self.save_text(path_name, answer_output)
        except ValueError:
            pass
        except urllib.error.HTTPError as e:
            pass
        except KeyError as e:
            pass
        except http.client.IncompleteRead:
            pass
