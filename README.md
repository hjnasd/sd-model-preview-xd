# sd-model-preview-xd
Extension for Automatic1111 Stable Diffusion WebUI to display previews for custom models.

## About
With so many new models appearing it's becoming harder to keep track of what models output what styles and what tags are used to call these styles.
This extension allows you to create various types of preview files/notes, each with the same name as your model and have this info easily displayed for later reference in webui.

## Installation
1. From the extensions tab in web ui click install from url
2. Paste `https://github.com/CurtisDS/sd-model-preview-xd` into the url box.
3. Click Install
4. From the Installed tab click apply and restart.
5. Put `.html`, `.md`, `.txt`, `.png`, `.webp`, and/or `.jpg`/`.jpeg` files in the same directory as your models, or a subfolder. Make sure to name the files the same as your model. You may append something after the name of the model and it will still work. You can have multiple images for a single model, but only one markdown, text, or html file. You can also mix and match any of the preview files except for HTML files, if the extension finds an html file it will only show the html file.

*NOTE: Symlinks do not seem to be supported see further down for a workaround*

For example if you have `my_model.ckpt` in `models\Stable-diffusion` then you can put `my_model.txt`, `my_model_1.jpg` and, `my_model_2.jpg` in `models\Stable-diffusion\Previews` and it will display them in the "Model Preview" tab.

This extension supports the folling model types in the the default directories:

- SD Checkpoints
- Embeddings
- Hypernetworks
- LoRA (If the [Additional Networks](https://github.com/kohya-ss/sd-webui-additional-networks.git) extension is also installed)

## Usage
1. After creating the preview files select the Model Preview tab in web ui and then the type of model you want to preview
2. Select a model from the dropdown list. (If the model has any preview files they will be shown)
3. Any preview png files found that also contain prompt data embedded in them will have a red "copy" button when hovering over the image. By clicking the button it will copy the prompt data to your clipboard.

![screenshot](https://github.com/CurtisDS/sd-model-preview-xd/raw/main/sd-model-preview-xd.png)

## Known Issues

- Refreshing models with the "Refresh" button in the extra networks section doesnt update the lists
- On initial load the selected checkpoint preview doesnt load (just choose a new checkpoint and then change back)
- Now that LoRA models are supported by default I will try to add support to LoRA without needing the extension

## Symlink workaround

The latest version of gradio (the front end software) doesn't seem to support symlinks for linking files. To work around this use Automatic1111's built in arguments for adding additional model directories.

Edit your web-user.bat COMMANDLINE_ARGS to include the custom directory argument for each model type:

`--ckpt-dir "D:\\my models\\checkpoints"`

`--hypernetwork-dir "D:\\my models\\hypernetworks"`

`--embeddings-dir "D:\\my models\\embeddings"`

If you wanted to use all the settings at once your COMMANDLINE_ARGS line would look something like this:

```
set COMMANDLINE_ARGS=--xformers --api --ckpt-dir "D:\\my models\\checkpoints" --hypernetwork-dir "D:\\my models\\hypernetworks" --embeddings-dir "D:\\my models\\embeddings"
```

You would still put your preview files in the default folder because they need to be inside your automatic1111 directory otherwise you will get an error when loading the previews.