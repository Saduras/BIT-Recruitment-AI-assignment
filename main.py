import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from sklearn.metrics import mean_squared_error

from model import LSTMModel
from data_processor import DataProcessor

def plot_data(x, y, label=''):
    plt.gca().xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%Y'))
    plt.gca().xaxis.set_major_locator(dates.MonthLocator(interval=3))
    plt.plot(x,y,label=label)
    plt.gcf().autofmt_xdate()

def moving_test_window_preds(model, start_X, n_future_preds):
    preds_moving = []
    moving_test_window = start_X.reshape(1, start_X.shape[0], start_X.shape[1])

    for i in range(n_future_preds):
        preds_on_step = model.predict(moving_test_window)

        preds_moving.append(preds_on_step[0,0])
        preds_on_step = preds_on_step.reshape(1,1,1)

        moving_test_window = np.concatenate((moving_test_window[:,1:,:], \
                                            preds_on_step), axis=1)
    return preds_moving

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--dataset', type=str, default='./data/timeseries_1h.csv',
                        help='Path to csv dataset to use')
    parser.add_argument('-m','--model-path', type=str, default='./model.h5',
                        help='Path for saving/loading trained model')
    parser.add_argument('-w','--window-size', type=int, default=50,
                        help='Length of input sequence to predict next datapoint')
    parser.add_argument('--eval-only', action='store_true',
                        help='If set model will be loaded from path instead of trained')

    args = parser.parse_args()

    df = pd.read_csv(args.dataset)

    # Preprocess input and reshapes to 
    # (num_samples, window_size, 1)
    processor = DataProcessor(args.window_size)
    train_X, train_y, test_X, test_y = processor.preprocess(df)

    lstm = LSTMModel(args.window_size)
    print(lstm.model.summary())
    if not args.eval_only:
        lstm.fit(train_X, train_y)
        lstm.save(args.model_path)
    else:
        lstm.load(args.model_path)

    preds = lstm.predict(test_X)

    preds = processor.postprocess(preds)
    actuals = processor.postprocess(test_y)

    fig1 = plt.figure()
    plt.plot(actuals, label='truth')
    plt.plot(preds, label='prediction')
    plt.legend()
    plt.savefig('./plot_static.png')

    preds_moving = moving_test_window_preds(lstm, test_X[0,:], n_future_preds=500)
    preds_moving = processor.postprocess(preds_moving)

    fig2 = plt.figure()
    plt.plot(actuals, label='truth')
    plt.plot(preds_moving, label='prediction')
    plt.legend()
    plt.savefig('./plot_moving.png')

if __name__ == "__main__":
    main()