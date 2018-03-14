from model import *
from train import *

def evaluate(net, dataset, bactch_size=64, use_cuda=False):
    dataloader = DataLoader(dataset, batch_size=bactch_size, collate_fn=collate, num_workers=0)
    count = 0
    if use_cuda:
        net.cuda()
    for i, batch_samples in enumerate(dataloader):
        x, y = batch_samples
        doc_list = []
        for sample in x:
            doc = []
            for sent_vec in sample:
                # print(sent_vec.size())
                if use_cuda:
                    sent_vec = sent_vec.cuda()
                doc.append(Variable(sent_vec, volatile=True))
            doc_list.append(pack_sequence(doc))
        if use_cuda:
            y = y.cuda()
        predicts = net(doc_list)
        # idx = []
        # for p in predicts.data:
        #     idx.append(np.random.choice(5, p=torch.exp(p).numpy()))
        # idx = torch.LongTensor(idx)
        p, idx = torch.max(predicts, dim=1)
        idx = idx.data
        count += torch.sum(torch.eq(idx, y))
    return count

def visualize_attention(doc, alpha_vec):
    pass

if __name__ == '__main__':
    from gensim.models import Word2Vec
    import gensim
    from gensim import models
    embed_model = Word2Vec.load('yelp.word2vec')
    embedding = Embedding_layer(embed_model.wv, embed_model.wv.vector_size)
    del embed_model

    net = HAN(input_size=200, output_size=5, 
            word_hidden_size=50, word_num_layers=1, word_context_size=100,
            sent_hidden_size=50, sent_num_layers=1, sent_context_size=100)
    net.load_state_dict(torch.load('model.dict'))
    test_dataset = YelpDocSet('reviews', 199, 4, embedding)
    correct = evaluate(net, test_dataset, True)
    print('accuracy {}'.format(correct/len(test_dataset)))
    # data_idx = 121
    # x, y = test_dataset[data_idx]
    # doc = []
    # for sent_vec in x:
    #     doc.append(Variable(sent_vec, volatile=True))
    # input_vec = [pack_sequence(doc)]
    # predict = net(input_vec)
    # p, idx = torch.max(predict, dim=1)
    # print(net.word_layer.last_alpha.squeeze())
    # print(net.sent_layer.last_alpha)
    # print(test_dataset.get_doc(data_idx)[0])
    # print('predict: {}, true: {}'.format(int(idx), y))
