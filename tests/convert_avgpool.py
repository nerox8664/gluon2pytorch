import argparse
import torch
import mxnet as mx
import numpy as np
import sys

sys.path.append('../')
from gluon2pytorch import gluon2pytorch


class AvgPoolTest(mx.gluon.nn.HybridSequential):
    def __init__(self):
        super(AvgPoolTest, self).__init__()
        from mxnet.gluon import nn
        with self.name_scope():
            self.conv1 = nn.Conv2D(3, 32)
            self.pool = nn.AvgPool2D(pool_size=(2, 2))

    def hybrid_forward(self, F, x):
        x = F.relu(self.pool(self.conv1(x)))
        return x

def check_error(gluon_output, pytorch_output, epsilon=1e-5):
    pytorch_output = pytorch_output.data.numpy()
    gluon_output = gluon_output.asnumpy()

    error = np.max(pytorch_output - gluon_output)
    print('Error:', error)

    assert error < epsilon
    return error


if __name__ == '__main__':
    print('Test avgpool:')

    net = AvgPoolTest()
    
    # Make sure it's hybrid and initialized
    net.hybridize()
    net.collect_params().initialize()

    pytorch_model = gluon2pytorch(net, dst_dir=None, pytorch_module_name='AvgPoolTest')

    input_np = np.random.uniform(-1, 1, (1, 3, 224, 224))

    gluon_output = net(mx.nd.array(input_np))
    pytorch_output = pytorch_model(torch.FloatTensor(input_np))
    check_error(gluon_output, pytorch_output)