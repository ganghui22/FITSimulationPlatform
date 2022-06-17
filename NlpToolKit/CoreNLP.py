import stanza
from stanza.server import CoreNLPClient


CUSTOM_PORS = {"parse.model": "edu/stanford/nlp/stanford-corenlp/4.4.0/stanford-corenlp-4.4.0-models-chinese.jar"}
input_text = "bring a cup to Lanjun in room219"

userfrom = 'Ganghui'
userto = 'Jiqiren'

CHINESE_CUSTOM_PROPS = {'tokenize.language': 'zh'}
CHINESE_ANNOTATORS = ['tokenize', 'ssplit', 'pos', 'ner', 'depparse']
ENGLISH_ANNOTATORS = ['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'depparse', 'coref', 'openie', 'kbp']


class CorenNLP:
    def __init__(self):
        with CoreNLPClient(
                endpoint="http://pi.ganghui22.com",
                annotators=ENGLISH_ANNOTATORS,
                start_server=stanza.server.StartServer.DONT_START,
                memory='6G') as client:
            self.client = client

    def annotate_message_en(self, message: str, fromuser: str, touser: str) -> list:
        annotators = self.client.annotate(message, output_format='json')
        sentence = annotators['sentences'][0]
        # 提取的tokens
        tokens = sentence['tokens']
        words = []

        # 复制tokens 中的每一个单词
        for token in tokens:
            words.append(token['word'])

        # 把词根为"I"，即第一人称代词换为消息发送者的名字。把词根为"you"，即第二人称的代词换为消息接受者，即机器人
        for token in tokens:
            if token['lemma'] == 'I':
                words[token['index'] - 1] = fromuser
            if token['lemma'] == 'you':
                words[token['index'] - 1] = touser

        # 如果动词前没有名词，即没有主语，则在动词前添加主语，即要执行动作的机器人
        for token in tokens:
            if token['pos'] == 'VBP' or token['pos'] == 'VB' or token['pos'] == 'VBZ':
                if token['index'] == 1:
                    words.insert(0, touser)
                else:
                    v_front = tokens[token['index'] - 2]['pos']
                    if v_front == 'NN' or v_front == 'NNP' or v_front == 'PRP':
                        pass
                    else:
                        words.insert(token['index'] - 1, touser)
        # 处理后的句子
        process_sentence = ""
        for word in words:
            process_sentence = process_sentence + " " + word

        # 再次解析
        annotators_process = self.client.annotate(process_sentence, output_format='json')
        sentence_process = annotators_process['sentences'][0]
        openie_process = sentence_process['openie']
        tokens_process = sentence_process['tokens']
        openie_len = len(openie_process)
        subjects = []
        relations = []
        objects = []
        for w in openie_process:
            subjects.append(w['subject'])
            if w['relationSpan'][0] + 1 == w['relationSpan'][1]:
                relations.append(w['relation'])
            objects.append(w['object'])
        max_subjectcount = 0
        most_subject = ""
        for subject in subjects:
            if subjects.count(subject) > max_subjectcount:
                max_subjectcount = subjects.count(subject)
                most_subject = subject
        max_relationcount = 0
        most_relation = ""
        for relation in relations:
            if relations.count(relation) > max_relationcount:
                max_relationcount = relations.count(relation)
                most_relation = relation
        if most_subject == "Jiqiren":
            most_subject = "Robot"
        return [most_subject, relations, objects, process_sentence]

    def annotate_message_ch(self, message: str, fromuser: str, touser: str) -> list:
        annotators = self.client.annotate(message)
