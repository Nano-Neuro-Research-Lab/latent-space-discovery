
############################# IMPORT LIBRARY  #################################
seed=75
import numpy as np
from tensorflow import set_random_seed 
import pandas as pd
import os
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import interp
from itertools import cycle
from xgboost import XGBClassifier
from collections import Counter
from sklearn.metrics import average_precision_score, precision_recall_curve, matthews_corrcoef, precision_score, recall_score, confusion_matrix, classification_report
from sklearn.metrics import f1_score, roc_auc_score, auc, cohen_kappa_score, precision_recall_curve, log_loss, roc_curve, classification_report, accuracy_score
from sklearn.model_selection import GridSearchCV, train_test_split, cross_val_score, cross_val_predict, StratifiedKFold, StratifiedShuffleSplit
from sklearn.metrics.classification import accuracy_score
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn import metrics
from sklearn.ensemble import RandomTreesEmbedding, RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC, LinearSVC
from sklearn.neural_network import MLPClassifier, BernoulliRBM
from sklearn import model_selection
from sklearn.decomposition import PCA, KernelPCA, SparsePCA, MiniBatchSparsePCA, NMF, TruncatedSVD, FastICA, FactorAnalysis, LatentDirichletAllocation
from sklearn.neighbors import KNeighborsClassifier
from sklearn.datasets import make_classification
from sklearn.multiclass import OneVsRestClassifier, OneVsOneClassifier
from sklearn.preprocessing import  Normalizer, MinMaxScaler, StandardScaler, RobustScaler, LabelEncoder, label_binarize, QuantileTransformer
from sklearn.manifold import TSNE
from sklearn.feature_selection import SelectFromModel, SelectKBest, chi2, RFE, RFECV
from sklearn.pipeline import make_pipeline
from imblearn.over_sampling import RandomOverSampler, ADASYN, SMOTE 
from imblearn.combine import SMOTEENN, SMOTETomek
from keras.initializers import RandomNormal
from keras.wrappers.scikit_learn import KerasClassifier
from keras.layers import Input, Dense
from keras.models import Model, load_model
from keras_adversarial import AdversarialOptimizerSimultaneous, normal_latent_sampling
from variational_autoencoder import *
#from aae_architechture import *
from aae_single_layer import *
from deep_autoencoder import *
from denoising_autoencoder import *
from shallow_autoencoder import *
from weight_analysis import *
matplotlib.use('Agg')
np.random.seed(seed)


def zero_mix(x, n):
    temp = np.copy(x)
    noise=n
    if 'spilt' in noise:
        frac = float(noise.split('-')[1])
    for i in temp:
        n = np.random.choice(len(i), int(round(frac * len(i))), replace=False)
        i[n] = 0
    return (temp)

def gaussian_mix(x):
    n = np.random.normal(0, 0.1, (len(x), len(x[0])))
    return (x + n)

# The above two functions are used to add noise in the data
# And used to train denoising autoencoder

#########################   LOAD BREAST CANCER DATA ####################

file_1 = pd.read_csv('./data/subtype_molecular_rna_seq.csv')
data = file_1.iloc[0:20439,2:607].values  
X=data.T
       
file_2 = pd.read_csv('./data/subtype_molecular_rna_seq_label.csv', low_memory=False)
label= file_2.iloc[0,2:607].values   
y=label.T

print('Actual dataset shape {}'.format(Counter(y)))


##########################  LOAD UCEC  DATA   ###########################
'''
file_1 = pd.read_csv('./data/ucec_rna_seq.csv')
data = file_1.iloc[0:20482,2:232].values 
X=data.T

file_2 = pd.read_csv('./data/ucec_rna_seq_label.csv', low_memory=False)
label = file_2.iloc[0,2:232].values   #First row then column from dataset
y=label.T   

print('Actual dataset shape {}'.format(Counter(y)))
'''
              

sm = SMOTEENN(ratio=1, random_state=seed)
X, y = sm.fit_sample(X, y)
#x_train, y_train = sm.fit_sample(x_train, y_train)
#x_test, y_test = sm.fit_sample(x_test, y_test)

print('Resampled dataset shape {}'.format(Counter(y)))
    

########################  FEATURE SCALING/NORMALIZATION ##################
from sklearn.preprocessing import QuantileTransformer
qt = QuantileTransformer(n_quantiles=10, random_state=seed)
qt.fit(X)
X=qt.transform(X)
#x_train=qt.transform(x_train)
#x_test=qt.transform(x_test)



############## HEAT MAP INPUT DATA   #######################
'''
sns_plot=sns.heatmap(X, cmap="PiYG", cbar=True, xticklabels=False, yticklabels=False)
fig = sns_plot.get_figure()
fig.savefig("./figures/input_data.png", format='png', dpi=500)
'''

#################### Spilt the data for training and testing ################
x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

#noise_factor = 0.2
#x_train_noisy = x_train + noise_factor * np.random.normal(loc=0.0, scale=1.0, size=x_train.shape) 
#x_test_noisy = x_test + noise_factor * np.random.normal(loc=0.0, scale=1.0, size=x_test.shape) 
#x_train_noisy=gaussian_mix(x_train)
#x_test_noisy=gaussian_mix(x_test)
# this is used for denoising autoencoder
    

###############################################################################       
###############################DIMENSION REDUCTION ############################
###############################################################################

       
################ VARIOUS AUTOENCODERS ###############
       

######### Shallow Autoencoder ############
'''
shallow_autoencoder_fit(x_train, x_test, dimension=50, optimizer="adadelta",
                        loss_function="binary_crossentropy", nb_epoch=100, 
                        batch_size=20, path='./feature_extraction/shallowAE/'+aaenum+'/')

#do not require fine tuning since this autoencoder does not have any hidden layer
shallow_autoencoder = load_model('./feature_extraction/shallowAE/'+aaenum+'/shallow_encoder'+'.h5')
x_train = shallow_autoencoder.predict(x_train)
print('X_Train Shape after ShallowAE :', x_train.shape)
x_test = shallow_autoencoder.predict(x_test)
print('X_Test Shape after ShallowAE :', x_train.shape)
'''

######### Denoising Autoencoder ############
'''
denoising_autoencoder_fit(x_train, x_test, x_train_noisy, x_test_noisy, dimension=50, optimizer="adadelta",
                          loss_function="binary_crossentropy", nb_epoch=100, 
                          batch_size=20, path='./feature_extractiondenoisingAE/'+aaenum+'/')

#do not require fine tuning since this autoencoder does not have any hidden layer
denoising_autoencoder = load_model('./results/denoisingAE/'+aaenum+'/denoising_encoder'+'.h5')

x_train = denoising_autoencoder.predict(x_train)
print('X_Train Shape after ShallowAE :', x_train.shape)
x_test = denoising_autoencoder.predict(x_test)
print('X_Test Shape after ShallowAE :', x_train.shape)
'''

######### Deep Autoencoder  ################
'''
deep_autoencoder_fit(x_train, x_test, dimension=50, optimizer="adadelta",
                     loss_function="binary_crossentropy", nb_epoch=100, 
                     batch_size=20, path='./feature_extraction/DeepAE/'+aaenum+'/')
       
####### don't need to use the following lines if you fine tune the autoencoder
deep_encoder = load_model('./feature_extraction/DeepAE/'+aaenum+'/deep_autoencoder'+'.h5')

x_train = deep_encoder.predict(x_train)
print('X_Train Shape after DeepAE :', x_train.shape)   
x_test = deep_encoder.predict(x_test)
print('X_Test Shape after DeepAE :', x_test.shape)
'''
       
##############  AAE  ##############
       
aae_model('./feature_extraction/AAE/', AdversarialOptimizerSimultaneous(),
          xtrain=x_train, ytrain=y_train, xtest=x_test, ytest=y_train, encoded_dim=50,img_dim=x_train.shape[1], nb_epoch=100)          
       
'''
####### don't need to use the following lines if autoencoder require fine tuning
model = load_model('./feature_extraction/AAE/'+aaenum+'/aae_encoder'+'.h5')

x_train = model.predict(x_train)
print('X_Train Shape after AAE :', x_train.shape)
       
x_test = model.predict(x_test)
print('X_Test Shape after AAE :', x_test.shape)
'''
                 
################  Variational Autoencoder  ####################
'''
vae_model_single('./feature_extraction/VAE/'+aaenum+'/',x_train.shape[1],
                 x_train,x_test,intermediate_dim=1000,batch_size=20,latent_dim=50,epochs=100)

####### don't need to use the following lines if autoencoder require fine tuning
model = load_model('./feature_extraction/VAE/'+aaenum+'/vae_encoder'+'.h5')
x_train = model.predict(x_train)
print('X_Train Shape after VAE :', x_train.shape)
x_test = model.predict(x_test)
print('X_Test Shape after VAE :', x_test.shape)
'''

#index = dataset.iloc[0:20482,0] # this is for valiadtion data
index = file_1.iloc[0:20439,0]

################ load model  #########################
weight = load_model('./feature_extraction/AAE/aae_encoder.h5')

encoded_aae=weight.predict(X)

sns_plot1=sns.heatmap(encoded_aae, cmap="PiYG", cbar=True)
fig1 = sns_plot1.get_figure()
fig1.savefig("./figures/encoded_data.png", format='png', dpi=500)



weights = []
for layer in weight.layers:
    weights.append(layer.get_weights())
d = pd.DataFrame(weights)
print ('Weight layer shape:', d.shape)

intermediate_weight_df = pd.DataFrame(weights[1][0])

'''
# use the following two lines when one hidden layer in autoencoder is used
# assign weight_matrix=abstracted_weight_df
intermediate_weight_df_2 = pd.DataFrame(weights[2][0])
abstracted_weight_df = intermediate_weight_df.dot(intermediate_weight_df_2)
'''

'''
# use the following lines including above two lines when two hidden layers in autoencoder are used
# assign weight_matrix= abstracted_weight_df_2
intermediate_weight_df_3 = pd.DataFrame(weights[3][0])
abstracted_weight_df_2 = abstracted_weight_df.dot(intermediate_weight_df_3)
'''

# assign the weight matrix based on how many layers in autoencoder are used

weight_matrix=intermediate_weight_df
print (weight_matrix)

####################### SAVE DECODED VALUE ##########################

decode = load_model('./feature_extraction/AAE/aae_decoder.h5')
decoded_data=decode.predict(encoded_aae)
dr_file =os.path.join('./feature_extraction/AAE/aae_decoded.tsv')
decoded = pd.DataFrame(decoded_data)
decoded.to_csv(dr_file, sep='\t')
# saving decoded file 
# this has no use in this project

'''
sns_plot2=sns.heatmap(decoded_aae, cmap="PiYG", cbar=True)
fig2 = sns_plot2.get_figure()
fig2.savefig("./figures/decoded_data.png", format='png', dpi=500)
'''

'''
sns_plot3=sns.heatmap(weight_matrix, cmap="PiYG", cbar=True)
fig3 = sns_plot3.get_figure()
fig3.savefig("./figures/weight_matrix.png", format='png', dpi=500)
'''

top_gene(weight_matrix=weight_matrix, weight_file='./results/AAE/aae_weight_matrix.tsv', 
         encoded_matrix=encoded_aae, encoded_file='./results/AAE/aae_encoded.tsv', 
         gene_file='./results/AAE/aae_sorted_gene.tsv', index=index,
         feature_distribution='./results/AAE/aae_weight_distribution.png')
