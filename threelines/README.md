**NOTE:** This code was created with the help of Copilot.  

This is a simple example of how to train a model using TensorFlow.  

The approach is straightforward. We have a Python script that generates images
randomly. These images are 100x100 pixels in size. The dataset for training the
neural network consists of 1,000 images. Each image has an associated label
indicating how many lines it contains. The number of lines ranges between 1 and
3, meaning any image can have 1, 2, or 3 lines.  

If you want to generate the images, run the following script:  

```bash python create_images.py ```  

The images will be created in a folder called `dataset`. This dataset will be
used to train the neural network.  

To train the neural network, run the following script:  

```bash python train_model.py ```  

This script will train the neural network and save the model in a file named
`line_detector_model.h5`.  

To make a prediction, run the following script:  

```bash python predict.py ```  

In the last line of the output, you will see the predicted number of lines for
the input image.
