# sd-model-preview-xd
Extension for Automatic1111 Stable Diffusion WebUI to display previews for custom models.

## About
A lot of new models and dreambooth finetunes are appearing and its becoming harder to keep track of what models output what styles and what tags are used to call these styles.
This extension allows you to create a various files with the same name as your model and have this info easily displayed for later reference in webui.

## Installation
1. From the extensions tab in web ui click install from url
2. Paste `https://github.com/Vetchems/sd-model-preview` into the url box.
3. Click Install
4. From the Installed tab click apply and restart.
5. Put `.html`, `.md`, `.txt`, `.png`, `.webp`, and/or `.jpg`/`.jpeg` files in the same directory as your models, or a subfolder. Make sure to name the files the same as your model. You may append something after the name to enable multiple preview elemnts at the same time. You can mix and match any of the preview files except for HTML files, if the extension finds an html file it will only show the html file.

For example if you have `my_model.ckpt` in `models\Stable-diffusion` then you can put `my_model.txt`, `my_model_1.jpg` and, `my_model_2.jpg` in `models\Stable-diffusion\Previews` and it will display them in the "Model Preview" tab.

This extension supports the folling model types in the the default directories:

- SD Checkpoints
- Embeddings
- Hypernetworks
- LoRA (If the [Additional Networks](https://github.com/kohya-ss/sd-webui-additional-networks.git) extension is also installed)

## Usage
1. After creating the preview files select the Model Preview tab in web ui and then the type of model you want to preview
2. Select a model from the dropdown list. (If the model has any preview files they will be shown)
3. Any preview png files found that also contain prompt data saved in the image a red copy button will appear while hovering over the image that will allow you to copy the prompt

![screenshot](https://github.com/CurtisDS/sd-model-preview-xd/raw/main/sd-model-preview-xd.png)

## Known Issues

- The latest update broke `.html` support
- Now that LoRA models are supported by default I will try to add support to LoRA without needing the extension