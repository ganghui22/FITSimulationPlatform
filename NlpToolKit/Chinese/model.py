from transformers import BertModel, BertPreTrainedModel
import torch.nn as nn
import torch
from torchcrf import CRF


class Bert_CRF(nn.Module):

    def __init__(self, label_size):
        super().__init__()
        self.label_size = label_size
        self.bert: BertModel = BertModel.from_pretrained(r'bert/chinese-roberta-wwm-ext')
        self.dropout = nn.Dropout(p=0.1)
        self.linear = nn.Linear(768, self.label_size)
        self.crf = CRF(self.label_size, batch_first=True)

    def _get_features(self, input_ids, mask):
        with torch.no_grad():
            embeds = self.bert(input_ids, attention_mask=mask)[0]
        enc = self.dropout(embeds)
        feats = self.linear(enc)
        return feats

    def forward(self, input_ids, attention_mask, tags=None, is_test=False):
        emissions = self._get_features(input_ids, attention_mask)
        mask = (attention_mask > 0)
        if not is_test:  # 训练阶段，返回loss
            loss = -self.crf.forward(emissions, tags, mask, reduction='mean')
            return loss
        else:  # 测试阶段，返回decoding结果
            decode = self.crf.decode(emissions, mask)
            return decode


class SubjectModel(BertPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.bert = BertModel(config)
        self.dense = nn.Linear(config.hidden_size, 2)

    def forward(self,
                input_ids,
                attention_mask=None):
        output = self.bert(input_ids, attention_mask=attention_mask)
        subject_out = self.dense(output[0])
        subject_out = torch.sigmoid(subject_out)

        return output[0], subject_out


class ObjectModel(nn.Module):
    def __init__(self, subject_model):
        super().__init__()
        self.encoder = subject_model
        self.dense_subject_position = nn.Linear(2, 768)
        self.dense_object = nn.Linear(768, 2 * 2)

    def forward(self,
                input_ids,
                subject_position,
                attention_mask=None):
        output, subject_out = self.encoder(input_ids, attention_mask)

        subject_position = self.dense_subject_position(subject_position).unsqueeze(1)
        object_out = output + subject_position
        # [bs, 768] -> [bs, 98]
        object_out = self.dense_object(object_out)
        # [bs, 98] -> [bs, 49, 2]
        object_out = torch.reshape(object_out, (object_out.shape[0], object_out.shape[1], 2, 2))
        object_out = torch.sigmoid(object_out)
        object_out = torch.pow(object_out, 4)
        return subject_out, object_out
