# -*- coding:utf-8 -*-
"""
   File Name：     mrcnn_head.py
   Description :   mrcnn头部网络
   Author :        steven.yi
   date：          2019/05/09
"""
from torch import nn


class MrcnnHead(nn.Module):
    def __init__(self, in_channel, out_channel_branch1, out_channel_branch2,
                 kernel_size, num_classes):
        """
        构造函数
        :param in_channel: int, 输入的channel大小
        :param kernel_size: int or tuple, 卷积核尺寸
        :param num_classes: int, 类别数
        """
        super(MrcnnHead, self).__init__()
        self.in_channel = in_channel
        self.kernel_size = kernel_size
        self.num_classes = num_classes
        self.out_channel_branch1 = out_channel_branch1
        self.out_channel_branch2 = out_channel_branch2

        # branch1, 得到class和regr box
        self.branch_1 = nn.Sequential(
            nn.Conv3d(self.in_channel, self.out_channel_branch1, kernel_size=self.kernel_size),
            nn.ReLU(inplace=True),
            nn.Conv3d(self.out_channel_branch1, self.out_channel_branch1, kernel_size=1),
            nn.ReLU(inplace=True)
        )
        self.cls = nn.Linear(out_channel_branch1, self.num_classes)
        self.regr = nn.Linear(out_channel_branch1, self.num_classes * 6)

        # branch2, 得到mask
        self.branch_2 = nn.Sequential(
            nn.Conv3d(self.in_channel, self.out_channel_branch2, kernel_size=self.kernel_size),
            nn.ReLU(inplace=True),
            nn.Conv3d(self.out_channel_branch2, self.out_channel_branch2, kernel_size=self.kernel_size),
            nn.ReLU(inplace=True),
            nn.Conv3d(self.out_channel_branch2, self.out_channel_branch2, kernel_size=self.kernel_size),
            nn.ReLU(inplace=True),
            nn.Conv3d(self.out_channel_branch2, self.out_channel_branch2, kernel_size=self.kernel_size),
            nn.ReLU(inplace=True),
            nn.ConvTranspose3d(self.out_channel_branch2, self.out_channel_branch2, kernel_size=2, stride=2),
            nn.Conv3d(self.out_channel_branch2, self.num_classes, kernel_size=1, stride=1)
        )

    def forward(self, roi):
        out1 = self.branch_1(roi)
        out1 = out1.view(-1, self.out_channel_branch1)
        cls = self.cls(out1)
        regr = self.regr(out1)
        mask = self.branch_2(roi)
        return cls, regr, mask