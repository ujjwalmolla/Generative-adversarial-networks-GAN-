# -*- coding: utf-8 -*-
"""GAN_Q2A.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XFOdsozg3QjBvhusf32lEMW7QjF3KQoK
"""

from keras.datasets import fashion_mnist
from keras.layers import Input, Dense, Reshape, Flatten
from keras.models import Sequential, Model
from keras.layers import BatchNormalization
from keras.layers.advanced_activations import LeakyReLU
from keras.optimizers import Adam
import matplotlib.pyplot as plt
import numpy as np

def load_data():
    input=open('/content/gan_data.txt','r')
    X_train=[]
    for doc in input:
        item=doc.strip('\n').split(',')
        x=[[0 , 0]]
        x[0][0]=float(item[0])
        x[0][1]=float(item[1])
        X_train.append(np.array(x))

    X_train=np.array(X_train)
    X_train=X_train/3
    # print(X_train)
    return X_train

def build_generator(img_shape,latent_dim):

    model = Sequential()

    model.add(Dense(256, input_dim=latent_dim))
    model.add(LeakyReLU(alpha=0.2))
    model.add(BatchNormalization())

    model.add(Dense(512))
    model.add(LeakyReLU(alpha=0.2))
    model.add(BatchNormalization())

    model.add(Dense(1024))
    model.add(LeakyReLU(alpha=0.2))
    model.add(BatchNormalization())

    model.add(Dense(np.prod(img_shape), activation='tanh'))
    model.add(Reshape(img_shape))
    model.summary()
    noise = Input(shape=(latent_dim,))
    img = model(noise)
    return Model(noise, img)

def build_discriminator(img_shape):
    model = Sequential()

    model.add(Flatten(input_shape=img_shape))
    model.add(Dense(512))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Dense(256))
    model.add(LeakyReLU(alpha=0.2))

    model.add(Dense(1, activation='sigmoid'))
    model.summary()

    img = Input(shape=img_shape)
    validity = model(img)
    return Model(img, validity)

def create_gan(discriminator,generator):
    z = Input(shape=(latent_dim,))
    img = generator(z)
    discriminator.trainable = False
    validity = discriminator(img)
    gan = Model(z, validity)
    gan.compile(loss='binary_crossentropy', optimizer=optimizer)
    return gan

def train(generator,discriminator,gan):
    iteration=[]
    discrim_loss=[]
    gen_loss=[]
    valid = np.ones((batch_size, 1))
    fake = np.zeros((batch_size, 1))

    for epoch in range(epochs):        
        idx = np.random.randint(0, X_train.shape[0], batch_size)
        imgs = X_train[idx]
        noise = np.random.normal(0, 1, (batch_size, latent_dim))
        g_loss = gan.train_on_batch(noise, valid)

        generated_imgs = generator.predict(noise)

        d_loss_real = discriminator.train_on_batch(imgs, valid)
        d_loss_fake = discriminator.train_on_batch(generated_imgs, fake)
        d_loss = 0.5 * np.add(d_loss_real, d_loss_fake) 

        if(epoch%10==0):
          iteration.append(epoch)
          gen_loss.append(g_loss)
          discrim_loss.append(d_loss[0])
          
          print("Epoch:",epoch)
          print("discriminator loss:" ,d_loss[0])
          print("discriminator acc.:" ,d_loss[1])
          print("generator loss:" , g_loss)

        if epoch % 1000 == 0:
            save_image(epoch)
            print("Epoch:",epoch)
            print("discriminator loss:" ,d_loss[0])
            print("discriminator acc.:" ,d_loss[1])
            print("generator loss:" , g_loss)

    return iteration,discrim_loss,gen_loss
    

def plot_loss(iteration,discrim_loss,gen_loss):
    plt.title("Epoch vs model loss")
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.plot(iteration, gen_loss, color ='tab:blue')  
    plt.plot(iteration, discrim_loss, color ='tab:orange') 
    plt.legend(['generative loss', 'discriminator loss'], loc='upper right')
    plt.savefig('model_loss.png')
    plt.show()


def save_image(epoch):
    r, c = 25, 20
    np.random.seed(0)
    noise = np.random.normal(0, 1, (r * c, latent_dim))
    generated_imgs = generator.predict(noise)
    # generated_imgs = generated_imgs + 0.8
    generated_imgs = 2* generated_imgs + 0.5

    x_axis = []
    y_axis = []
    for i in range(500):
      x_axis.append(generated_imgs[i][0][0])
      y_axis.append(generated_imgs[i][0][1])
    plt.scatter(x_axis,y_axis,color='b')
    plt.savefig("image1_2a1_ %d.png" % epoch)
    plt.show()    
    plt.close()


if __name__ == '__main__':
    
    epochs=10000
    batch_size=128
    img_shape = (1, 2, 1)
    latent_dim = 6
    optimizer = Adam(0.0002, 0.5)
    

    X_train=load_data()

    #create discriminator model
    discriminator = build_discriminator(img_shape)
    discriminator.compile(loss='binary_crossentropy',optimizer=optimizer,metrics=['accuracy'])

    #create generator model
    generator = build_generator(img_shape,latent_dim)
    gan=create_gan(discriminator,generator)   
    iteration,discrim_loss,gen_loss=train(generator,discriminator,gan)

    plot_loss(iteration,discrim_loss,gen_loss)