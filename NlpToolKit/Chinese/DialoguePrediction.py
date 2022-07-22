from transformers import BertTokenizer
import torch
from model import ObjectModel
import numpy as np
import os
import json

GPU_NUM = 0


class SPO(tuple):
    """用来存三元组的类
    表现跟tuple基本一致，只是重写了 __hash__ 和 __eq__ 方法，
    使得在判断两个三元组是否等价时容错性更好。
    """

    def __init__(self, spo):
        self.spox = (
            spo[0],
            spo[1],
            spo[2],
        )

    def __hash__(self):
        return self.spox.__hash__()

    def __eq__(self, spo):
        return self.spox == spo.spox


class DialoguePrediction:
    """
    该类主要是一个实时解析群聊中对话的中文工具包，将一句对话解析成{时间、地点、人物}三元组
    """
    def __init__(self):
        # 解析模型的载入
        self.device = torch.device('cpu')
        self.model: ObjectModel = torch.load(
            '/home/llj/FITSimulationPlatform/NlpToolKit/Chinese/graph_model.bin', map_location='cpu')
        self.model.eval()

        # tokenizer的载入，从bert中载入
        self.tokenizer = BertTokenizer.from_pretrained(r'NlpToolKit/Chinese/model/bert/chinese-roberta-wwm-ext')

        # 载入词袋
        vocab = {}
        with open(r'NlpToolKit/Chinese/model/bert/chinese-roberta-wwm-ext/vocab.txt', encoding='utf_8') as file:
            for l in file.readlines():
                vocab[len(vocab)] = l.strip()
        self.vocab = vocab

        # 关系转换
        self.id2predicate = {"0": "地点", "1": "时间"}
        self.predicate2id = {"地点": 0, "时间": 1}

    def __call__(self, sentence: str):
        """
        返回[人物, 时间, 地点]
        """
        spo = []
        en = self.tokenizer(text=sentence, return_tensors='pt')
        subject_model = self.model.encoder
        _, subject_preds = subject_model(en.input_ids.to(self.device), en.attention_mask.to(self.device))
        subject_preds = subject_preds.cpu().data.numpy()
        start = np.where(subject_preds[0, :, 0] > 0.6)[0]
        end = np.where(subject_preds[0, :, 1] > 0.5)[0]
        subjects = []
        for i in start:
            j = end[end >= i]
            if len(j) > 0:
                j = j[0]
                subjects.append((i, j))
        # print(subjects)
        if subjects:
            for s in subjects:
                index = en.input_ids.cpu().data.numpy().squeeze(0)[s[0]:s[1] + 1]
                subject = ''.join([self.vocab[i] for i in index])
                # print(subject)

                _, object_preds = self.model(en.input_ids.to(self.device),
                                             torch.from_numpy(np.array([s])).float().to(self.device),
                                             en.attention_mask.to(self.device))
                object_preds = object_preds.cpu().data.numpy()
                for object_pred in object_preds:
                    start = np.where(object_pred[:, :, 0] > 0.2)
                    end = np.where(object_pred[:, :, 1] > 0.2)
                    for _start, predicate1 in zip(*start):
                        for _end, predicate2 in zip(*end):
                            if _start <= _end and predicate1 == predicate2:
                                index = en.input_ids.cpu().data.numpy().squeeze(0)[_start:_end + 1]
                                object = ''.join([self.vocab[i] for i in index])
                                predicate = self.id2predicate[str(predicate1)]
                                # print(object, '\t', predicate)
                                spo.append([subject.replace("##", ''), predicate, object.replace("##", '')])
        # print(spo)
        # 预测结果
        R = set([SPO(_spo) for _spo in spo])
        # print(R)
        res = {}
        triple = []
        if R is not None:
            for i in R:
                per_person = i[0]
                if per_person not in res:
                    res[per_person] = [per_person, '', '']
                if i[1] == '时间':
                    per_time = i[2]
                    res[per_person][2] = per_time
                if i[1] == '地点':
                    per_loc = i[2]
                    res[per_person][1] = per_loc
            for m in ['我们', '大家', '咱们', '全体员工', '所有人']:
                if m in res:
                    tmp_res=res[m]
                    res={}
                    res[m]=tmp_res
                    break
            for key, value in res.items():
                triple.append(value)
        return triple


if __name__ == '__main__':
    dia = DialoguePrediction()
    print(dia("我们2:30去518开会"))
