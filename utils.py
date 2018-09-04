from keras.datasets import mnist
from keras.utils import np_utils
from keras.models import model_from_json
from keras import backend as K
import sys
from sklearn.metrics import classification_report, confusion_matrix
from math import ceil
import matplotlib.pyplot as plt
import numpy as np
import h5py


def load_data(one_hot=True):
    """
    Load MNIST data
    :param one_hot:
    :return:
    """
    #Load data
    (X_train, y_train), (X_test, y_test) = mnist.load_data()

    #Preprocess dataset
    #Normalization and reshaping of input.
    X_train = X_train.reshape(X_train.shape[0], 1, 28, 28)
    X_test = X_test.reshape(X_test.shape[0], 1, 28, 28)

    X_train = X_train.astype('float32')
    X_test = X_test.astype('float32')
    X_train /= 255
    X_test /= 255

    if one_hot:
        #For output, it is important to change number to one-hot vector.
        Y_train = np_utils.to_categorical(y_train, num_classes=10)
        Y_test = np_utils.to_categorical(y_test, num_classes=10)

    return X_train, Y_train, X_test, Y_test


def load_model(model_name):
    json_file = open(model_name + '.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    # load weights into model
    model.load_weights(model_name + '.h5')

    model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])
    return model


def get_layer_outs(model, class_specific_test_set):
    inp = model.input                                           # input placeholder
    outputs = [layer.output for layer in model.layers]          # all layer outputs
    functors = [K.function([inp]+ [K.learning_phase()], [out]) for out in outputs]  # evaluation functions
    # Testing
    layer_outs = [func([class_specific_test_set, 1.]) for func in functors]

    return layer_outs


def get_python_version():
    if (sys.version_info > (3, 0)):
        # Python 3 code in this block
        return 3
    else:
        # Python 2 code in this block
        return 2


def show_image(vector):
    img = vector
    plt.imshow(img)
    plt.show()


def calculate_prediction_metrics(Y_test, Y_pred, score):
    """
    Calculate classification report and confusion matrix
    :param Y_test:
    :param Y_pred:
    :param score:
    :return:
    """
    #Find test and prediction classes
    Y_test_class = np.argmax(Y_test, axis=1)
    Y_pred_class = np.argmax(Y_pred, axis=1)

    classifications = np.absolute(Y_test_class - Y_pred_class)

    correct_classifications = []
    incorrect_classifications = []
    for i in range(1, len(classifications)):
        if (classifications[i] == 0):
            correct_classifications.append(i)
        else:
            incorrect_classifications.append(i)


    # Accuracy of the predicted values
    print(classification_report(Y_test_class, Y_pred_class))
    print(confusion_matrix(Y_test_class, Y_pred_class))

    acc = sum([np.argmax(Y_test[i]) == np.argmax(Y_pred[i]) for i in range(len(Y_test))]) / len(Y_test)
    v1 = ceil(acc*10000)/10000
    v2 = ceil(score[1]*10000)/10000
    correct_accuracy_calculation =  v1 == v2
    try:
        if not correct_accuracy_calculation:
            raise Exception("Accuracy results don't match to score")
    except Exception as error:
        print("Caught this error: " + repr(error))


def get_dummy_dominants(model_name):
    model = load_model(model_name)
    import random
    dominant = {x: random.sample(range(model.layers[x].output_shape[1]), 2) for x in range(1, len(model.layers) - 1)}

    return dominant


def save_perturbed_test(x_perturbed, y_perturbed, filename):
    # save X
    with h5py.File(filename + '_perturbations_x.h5', 'w') as hf:
        hf.create_dataset("x_perturbed", data=x_perturbed)

    #save Y
    with h5py.File(filename + '_perturbations_y.h5', 'w') as hf:
        hf.create_dataset("y_perturbed", data=y_perturbed)

    return


def save_perturbed_test_groups(x_perturbed, y_perturbed, filename, group_index):
    # Write:
    # save X
    with h5py.File(filename + '_perturbations.h5', 'w') as hf:
        group = hf.create_group('group'+str(group_index))
        group.create_dataset("x_perturbed", data=x_perturbed)
        group.create_dataset("y_perturbed", data=y_perturbed)

    return



def load_perturbed_test(filename):
    # read X
    with h5py.File(filename + '_perturbations_x.h5', 'r') as hf:
        x_perturbed = hf["x_perturbed"][:]

    # read Y
    with h5py.File(filename + '_perturbations_y.h5', 'r') as hf:
        y_perturbed = hf["y_perturbed"][:]

    return x_perturbed, y_perturbed


def load_perturbed_test_groups(filename, group_index):
    with h5py.File(filename + '_perturbations_y.h5', 'r') as hf:
        group = hf.get('group'+group_index)
        x_perturbed = group.get('x_perturbed')
        y_perturbed = group.get('y_perturbed')

        return x_perturbed, y_perturbed
