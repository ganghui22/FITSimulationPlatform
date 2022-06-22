import torch
import json
from transformers import BertTokenizer

from model import Bert_CRF


class InstructionPrediction:
    """
    指令解析工具
    """
    def __init__(self):
        self.device = torch.device('cpu')
        self.model: Bert_CRF = torch.load(r'NlpToolKit/Chinese/model/Instruction_model.bin',
                                          map_location='cpu')
        self.model.eval()
        self._tokenizer = BertTokenizer.from_pretrained(r'NlpToolKit/Chinese/model/bert/chinese-roberta-wwm-ext')
        with open(r'NlpToolKit/Chinese/model/LabelAndIdx.json', encoding='utf-8') as file:
            labelAndIdx = json.load(file)
        self.label2idx, self.idx2label = labelAndIdx["label2idx"], labelAndIdx["idx2label"]

    def __call__(self, sentence: str):
        tokens_encode = self._tokenizer.encode_plus(sentence, max_length=50, pad_to_max_length=True, truncation=True,
                                       padding='max_length')
        tokens_input_ids, tokens_attention_mask = torch.tensor(tokens_encode.input_ids).reshape(1, -1).to(
            self.device), torch.tensor(tokens_encode.attention_mask).reshape(1, -1).to(self.device)
        pre_idx_list = self.model(tokens_input_ids, tokens_attention_mask, is_test=True)[0]
        pre_label_list = [self.idx2label[str(idx)] for idx in pre_idx_list]
        # 分词预测
        tokens = self._tokenizer.tokenize(sentence)
        tokens.append('[SEP]')
        tokens.insert(0, '[CLS]')
        frameElements = self._label2frame(pre_label_list, tokens)
        return frameElements

    @staticmethod
    def _label2frame(pre_label_list: list, tokens: list) -> dict:
        if len(pre_label_list) != len(tokens):
            raise "pre_label_list != tokens"
        else:
            frameElements = dict()
            for idx, pre_label in enumerate(pre_label_list):
                if pre_label[0] == 'B':
                    frame = pre_label.split('-')[1].lower()
                    frameElement = pre_label.split('-')[2].lower()
                    if frame not in frameElements:
                        frameElements[frame] = {}
                    if frameElement not in frameElements[frame]:
                        frameElements[frame][frameElement] = [tokens[idx].replace('##', '')]
                    else:
                        frameElements[frame][frameElement].append(tokens[idx].replace('##', ''))
                elif pre_label[0] == 'I':
                    frame = pre_label.split('-')[1].lower()
                    frameElement = pre_label.split('-')[2].lower()
                    if frame not in frameElements:
                        raise "frame not in"
                    if frameElement not in frameElements[frame]:
                        raise "B is not"
                    frameElements[frame][frameElement][-1] = frameElements[frame][frameElement][-1] + tokens[idx].replace('##', '')
            return frameElements


