# -*- coding: utf-8 -*-
"""
   File Name：     proposals.py
   Description :  应用边框回归生成 proposals,并使用nms过滤
   Author :       mick.yi
   Date：          2019/5/8
"""
import torch
from torch import nn
from utils.torch_utils import apply_regress_3d
from cuda_functions.nms_3D.pth_nms import nms_gpu as nms_3d


class Proposal(nn.Module):
    def __init__(self, pre_nms_limit, nms_threshold, max_output_num, min_score=0.):
        self.pre_nms_limit = pre_nms_limit
        self.nms_threshold = nms_threshold
        self.max_output_num = max_output_num
        self.min_score = min_score
        super(Proposal, self).__init__()

    def forward(self, anchors, predict_scores, predict_deltas):
        """

        :param anchors: [anchors_num,(y1,x1,z1,y2,x2,z2)]
        :param predict_scores: [batch,anchors_num]
        :param predict_deltas: [batch,anchors_num,(dx,dy,dz,dh,dw,dd)]
        :return:
        """
        batch_proposals = []
        batch_scores = []
        batch_indices = []
        # 逐个样本处理
        batch_size = predict_scores.shape[0]
        for bix in range(batch_size):
            # nms之前保留得分最高topn
            scores, order = torch.sort(predict_scores[bix], descending=True)
            order = order[:self.pre_nms_limit]
            scores = scores[:self.pre_nms_limit]
            deltas = predict_deltas[bix, order, :]
            cur_anchors = torch.clone(anchors)
            # 应用边框回归
            boxes = apply_regress_3d(deltas, cur_anchors)
            # nms
            keep = nms_3d(torch.cat([boxes, scores.unsqueeze(-1)], -1),
                          self.nms_threshold)  # [n,(y1,x1,z1,y2,x2,z2,sores)]
            keep = keep[:self.max_output_num]
            # 生成batch_indices
            indices = torch.Tensor([bix] * keep.shape[0])  # proposals处于batch中哪个样本
            batch_indices.append(indices)
            batch_proposals.append(keep[:, :-1])
            batch_scores.append(keep[:, -1])

        # 在batch上打平
        batch_proposals = torch.cat(batch_proposals, dim=0)
        batch_scores = torch.cat(batch_scores, dim=0)
        batch_indices = torch.cat(batch_indices, dim=0)

        return batch_proposals, batch_scores, batch_indices