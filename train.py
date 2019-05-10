# -*- coding: utf-8 -*-
"""
   File Name:     train.py
   Description:   训练
   Author:        steven.yi
   Date:          2019/5/10
"""
from utils.data_loader import DataLoader, Data3Lung
from config import cur_config as cfg
from torch import optim
from model import LungNet


# 加载数据
dataset = Data3Lung(cfg.DATA_DIR, cfg, phase='train')
train_loader = DataLoader(dataset, shuffle=True)

# 初始化网络
net = LungNet(cfg, phase='train')
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

# 训练
for epoch in range(cfg.EPOCHS):
    for i, data in enumerate(train_loader):
        inputs, masks, gts = data

        # 清零梯度
        optimizer.zero_grad()

        # 正向传播 + 反向传播 + 参数更新
        gt_boxes = gt_labels = None  # todo: 不明确gt_boxes和gt_labels从哪得到
        outputs = net(inputs, gt_boxes, gt_labels)
        loss = net.total_loss
        loss.backward()
        optimizer.step()